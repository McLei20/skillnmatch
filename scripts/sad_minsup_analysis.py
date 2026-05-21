"""Why we didn't use the adaptive minimum-support threshold.

A presentation-friendly comparison between:
  (a) the SAd adaptive threshold from Ogedengbe, Junaidu & Kana (2024)
      "Adaptive Minimum Support Threshold for Association Rule Mining."
      Indonesian Journal of Data and Science, 5(2), 101-108.
      DOI: 10.56705/ijodas.v5i2.134
  (b) the flat MIN_SUPPORT = 0.05 baseline used by src/arm.py

For each of the 25 careers, the script reports how many skill-association
rules each method produces, then explains in plain English why the
adaptive method does not fit our dataset.

Run:
    python scripts/sad_minsup_analysis.py
"""
from __future__ import annotations

import ast
import math
import os
import sys
from collections import Counter

import pandas as pd
from mlxtend.preprocessing import TransactionEncoder
from mlxtend.frequent_patterns import fpgrowth, association_rules

# Force UTF-8 stdout so any special characters survive Windows consoles.
try:
    sys.stdout.reconfigure(encoding='utf-8')
except AttributeError:
    pass


HERE = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(HERE, '..', 'data', 'cleaned_jobs.csv')

FLAT_MINSUP = 0.05


def compute_sad_minsup(transactions: list) -> tuple[float, dict]:
    """SAd adaptive minimum support (Ogedengbe et al. 2024, Equation 8).

    Returns (clamped_threshold, components) where ``components`` exposes
    the intermediate values: I, sup_max, n_avg, R_overflow, omega_raw,
    omega_clamped, at_ceiling. The math:

        omega = Sup_max * (1 - (1 / sqrt(R)) ** (1 / N_avg))
        R     = 2 ** I - 1   (I = number of unique items)
        N_avg = sum of items across transactions / I

    Result is clamped to [0.05, 0.20].
    """
    n_postings = len(transactions)
    if n_postings == 0:
        return 0.05, {'reason': 'empty'}

    item_counts = Counter(item for t in transactions for item in t)
    I = len(item_counts)
    if I == 0:
        return 0.05, {'reason': 'no items'}

    sup_max = max(c / n_postings for c in item_counts.values())
    n_avg = sum(len(t) for t in transactions) / I

    R_overflow = False
    try:
        R = 2 ** I - 1
        term = (1 / math.sqrt(R)) ** (1 / n_avg)
    except (OverflowError, ZeroDivisionError):
        R_overflow = True
        term = 0.0

    omega_raw = sup_max * (1 - term)
    omega_clamped = max(0.05, min(0.2, omega_raw))

    return omega_clamped, {
        'I': I,
        'sup_max': sup_max,
        'n_avg': n_avg,
        'R_overflow': R_overflow,
        'omega_raw': omega_raw,
        'omega_clamped': omega_clamped,
        'at_ceiling': omega_clamped >= 0.1999,
    }


def _count_rules(encoded_df: pd.DataFrame, min_support: float) -> int:
    fi = fpgrowth(encoded_df, min_support=min_support, use_colnames=True)
    if len(fi) == 0:
        return 0
    rules = association_rules(fi, metric='lift', min_threshold=1)
    if len(rules) == 0:
        return 0
    rules = rules[rules['consequents'].apply(lambda x: len(x) == 1)]
    rules = rules[rules['antecedents'].apply(lambda x: len(x) <= 3)]
    return len(rules)


def main() -> None:
    df = pd.read_csv(DATA_PATH)
    df['IT Skills'] = df['IT Skills'].apply(ast.literal_eval)

    # ---- Gather results per career ----------------------------------
    rows = []
    for career in sorted(df['Query'].unique()):
        transactions = df[df['Query'] == career]['IT Skills'].tolist()
        te = TransactionEncoder()
        encoded = pd.DataFrame(te.fit_transform(transactions), columns=te.columns_)

        sad_thr, info = compute_sad_minsup(transactions)
        sad_rules = _count_rules(encoded, sad_thr)
        flat_rules = _count_rules(encoded, FLAT_MINSUP)
        rows.append({
            'career': career,
            'skills_tracked': info['I'],
            'sad_threshold': sad_thr,
            'sad_rules': sad_rules,
            'flat_rules': flat_rules,
            'at_ceiling': info['at_ceiling'],
            'omega_raw': info['omega_raw'],
            'sup_max': info['sup_max'],
        })

    n = len(rows)
    n_zero_sad = sum(1 for r in rows if r['sad_rules'] == 0)
    n_zero_flat = sum(1 for r in rows if r['flat_rules'] == 0)
    n_ceiling = sum(1 for r in rows if r['at_ceiling'])

    # ---- Header / TL;DR ---------------------------------------------
    print('=' * 78)
    print('WHY WE DID NOT USE THE ADAPTIVE THRESHOLD (SAd)')
    print('=' * 78)
    print()
    print('We tested two ways of choosing the minimum-support threshold for')
    print('association-rule mining on our 25-career job-postings dataset:')
    print()
    print('  1. SAd adaptive method  -- Ogedengbe, Junaidu & Kana (2024)')
    print('  2. Flat baseline         -- min_support = 0.05  (what we ship)')
    print()
    print('Headline result:')
    print()
    print(f'    With SAd, {n_zero_sad} of {n} careers produce ZERO skill-pair rules.')
    print(f'    With the flat 0.05 baseline, only {n_zero_flat} of {n} produces zero.')
    print()
    print('In other words: the adaptive method silently strips the recommender')
    print(f'of useful output for {n_zero_sad}/{n} careers. The flat 0.05 baseline keeps')
    print(f'{n - n_zero_flat}/{n} careers populated.')
    print()

    # ---- Per-career table -------------------------------------------
    print('-' * 78)
    print('PER-CAREER COMPARISON')
    print('-' * 78)
    print(
        f"{'Career':<35} {'Skills':>7} {'SAd thr.':>9} "
        f"{'SAd rules':>10} {'0.05 rules':>11}"
    )
    print('-' * 78)
    for r in rows:
        print(
            f"{r['career']:<35} {r['skills_tracked']:>7} "
            f"{r['sad_threshold']:>9.3f} {r['sad_rules']:>10} "
            f"{r['flat_rules']:>11}"
        )
    print('-' * 78)
    print()
    print(f"Careers where SAd hit its 0.20 upper clamp: {n_ceiling} / {n}")
    print()

    # ---- Three concrete examples ------------------------------------
    print('-' * 78)
    print('CONCRETE EXAMPLES')
    print('-' * 78)
    by_flat_desc = sorted(rows, key=lambda r: r['flat_rules'], reverse=True)
    for r in by_flat_desc[:3]:
        print(
            f"  {r['career']}: SAd threshold = {r['sad_threshold']:.2f} -> "
            f"{r['sad_rules']} rules.  "
            f"Flat 0.05 -> {r['flat_rules']} rules."
        )
    print()

    # ---- Plain-English explanation ----------------------------------
    print('-' * 78)
    print('WHY SAd BREAKS ON THIS DATASET (in plain English)')
    print('-' * 78)
    print()
    print('SAd was designed and tested by Ogedengbe et al. on datasets with a')
    print('small vocabulary -- roughly 30 to 50 unique items per dataset. At')
    print('that size, the formula produces a sensible threshold (their reported')
    print('optimal range was 0.057-0.065).')
    print()
    print('Our dataset is structured differently. Each career has on the order')
    print('of about 1,000 unique skills tracked across roughly 120 job postings.')
    print('When the formula tries to plug I = 1000 into "2 to the power of I",')
    print('the resulting number is so enormous that a normal computer cannot')
    print('represent it as a decimal -- it overflows. The formula then quietly')
    print('falls back to its strictest possible threshold (clamped at 0.20).')
    print()
    print('At a 0.20 threshold, only the few skills that appear in 20%+ of')
    print('postings for that career survive. Everything else is filtered out')
    print('before rule mining starts. With so few skills left, there are almost')
    print('no pairs to turn into "if X then Y" recommendations -- which is')
    print('exactly what we see in the table above.')
    print()
    print('-' * 78)
    print('BOTTOM LINE')
    print('-' * 78)
    print()
    print('SAd is a good algorithm for the dataset shape its authors tested it')
    print('on. Ours is bigger and sparser, so the formula degenerates. The flat')
    print('0.05 baseline is the right choice for this project, and we keep the')
    print('SAd code in this script so the trade-off can be inspected and')
    print('justified rather than glossed over.')
    print()


if __name__ == '__main__':
    main()