import sys
import os
import time
import ast
import pandas as pd
from mlxtend.preprocessing import TransactionEncoder
from mlxtend.frequent_patterns import apriori, fpgrowth, association_rules
from collections import namedtuple

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

# ── Configuration ────────────────────────────────────────────────────────────
DATA_PATH   = os.path.join(os.path.dirname(__file__), '..', 'data', 'cleaned_jobs.csv')
MIN_SUPPORT = 0.05
MIN_LIFT    = 1.0

CareerResult = namedtuple('CareerResult', [
    'career',
    'postings',
    'apriori_time',
    'fpgrowth_time',
    'apriori_itemsets',
    'fpgrowth_itemsets',
    'itemsets_identical',
    'apriori_rules',
    'fpgrowth_rules',
    'rules_identical',
])

# ── Helpers ───────────────────────────────────────────────────────────────────
def encode(transactions):
    te = TransactionEncoder()
    arr = te.fit_transform(transactions)
    return pd.DataFrame(arr, columns=te.columns_)


def count_rules(frequent_itemsets, encoded_df):
    """Generate rules and return count. Returns 0 if no itemsets found."""
    if len(frequent_itemsets) == 0:
        return 0
    rules = association_rules(
        frequent_itemsets, metric='lift', min_threshold=MIN_LIFT
    )
    if len(rules) == 0:
        return 0
    rules = rules[rules['consequents'].apply(lambda x: len(x) == 1)]
    rules = rules[rules['antecedents'].apply(lambda x: len(x) <= 3)]
    return len(rules)


def frozenset_rows(df):
    """Return a set of frozensets representing each itemset row for comparison."""
    return set(frozenset(row) for row in df['itemsets'])


# ── Core benchmark ────────────────────────────────────────────────────────────
def run_comparison():
    df = pd.read_csv(DATA_PATH)
    df['IT Skills'] = df['IT Skills'].apply(ast.literal_eval)

    results = []
    careers = df['Query'].unique()

    print(f"\n{'Career':<35} {'Posts':>5}  {'Apriori':>9}  {'FP-Growth':>9}  {'Items':>6}  {'Match':>5}")
    print('─' * 80)

    for career in sorted(careers):
        transactions = df[df['Query'] == career]['IT Skills'].tolist()
        encoded = encode(transactions)

        # Apriori
        t0 = time.perf_counter()
        fi_apriori = apriori(encoded, min_support=MIN_SUPPORT, use_colnames=True)
        apriori_time = time.perf_counter() - t0

        # FP-Growth
        t0 = time.perf_counter()
        fi_fpgrowth = fpgrowth(encoded, min_support=MIN_SUPPORT, use_colnames=True)
        fpgrowth_time = time.perf_counter() - t0

        # Compare itemsets
        sets_a = frozenset_rows(fi_apriori)
        sets_f = frozenset_rows(fi_fpgrowth)
        itemsets_identical = sets_a == sets_f

        # Compare rule counts
        rules_a = count_rules(fi_apriori, encoded)
        rules_f = count_rules(fi_fpgrowth, encoded)
        rules_identical = rules_a == rules_f

        r = CareerResult(
            career=career,
            postings=len(transactions),
            apriori_time=apriori_time,
            fpgrowth_time=fpgrowth_time,
            apriori_itemsets=len(fi_apriori),
            fpgrowth_itemsets=len(fi_fpgrowth),
            itemsets_identical=itemsets_identical,
            apriori_rules=rules_a,
            fpgrowth_rules=rules_f,
            rules_identical=rules_identical,
        )
        results.append(r)

        match_icon = '✅' if itemsets_identical and rules_identical else '❌'
        print(
            f"{career:<35} {len(transactions):>5}  "
            f"{apriori_time:>8.4f}s  {fpgrowth_time:>8.4f}s  "
            f"{len(fi_apriori):>6}  {match_icon}"
        )

    return results


# ── Summary ───────────────────────────────────────────────────────────────────
def print_summary(results):
    total_a   = sum(r.apriori_time   for r in results)
    total_f   = sum(r.fpgrowth_time  for r in results)
    speedup   = total_a / total_f if total_f > 0 else 0
    all_match = all(r.itemsets_identical and r.rules_identical for r in results)

    print('\n' + '═' * 80)
    print('SUMMARY')
    print('═' * 80)
    print(f"  Careers benchmarked  : {len(results)}")
    print(f"  Total Apriori time   : {total_a:.4f}s")
    print(f"  Total FP-Growth time : {total_f:.4f}s")
    print(f"  Speed ratio          : {speedup:.2f}x  ", end='')
    print("(FP-Growth faster)" if speedup > 1 else "(Apriori faster at this scale)")
    print(f"  All itemsets identical: {'✅ Yes' if all_match else '❌ No — see rows above'}")
    print('═' * 80)

    return all_match


# ── Assertions (acts as a test suite) ────────────────────────────────────────
def run_assertions(results):
    print('\nRunning assertions...')

    # 1. Every career produced results
    assert len(results) > 0, "No careers were benchmarked"

    # 2. All itemsets and rules are identical between algorithms
    for r in results:
        assert r.itemsets_identical, (
            f"Itemset mismatch for '{r.career}': "
            f"Apriori={r.apriori_itemsets}, FP-Growth={r.fpgrowth_itemsets}"
        )
        assert r.rules_identical, (
            f"Rule count mismatch for '{r.career}': "
            f"Apriori={r.apriori_rules}, FP-Growth={r.fpgrowth_rules}"
        )

    # 3. Both algorithms finish in under 1 second per career (sanity check)
    for r in results:
        assert r.apriori_time < 1.0, f"Apriori too slow for '{r.career}': {r.apriori_time:.4f}s"
        assert r.fpgrowth_time < 1.0, f"FP-Growth too slow for '{r.career}': {r.fpgrowth_time:.4f}s"

    # 4. Total combined time under 10 seconds
    total = sum(r.apriori_time + r.fpgrowth_time for r in results)
    assert total < 10.0, f"Combined benchmark took too long: {total:.2f}s"

    print("✅ All assertions passed.")


# ── Entry point ───────────────────────────────────────────────────────────────
if __name__ == '__main__':
    results = run_comparison()
    all_match = print_summary(results)
    run_assertions(results)