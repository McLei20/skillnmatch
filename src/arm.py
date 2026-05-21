import pandas as pd
import ast
from collections import Counter
from mlxtend.preprocessing import TransactionEncoder
from mlxtend.frequent_patterns import fpgrowth, association_rules
import pickle


def compute_adaptive_minsup(transactions: list) -> float:
    total_transactions = len(transactions)
    if total_transactions == 0:
        return 0.05  # fallback

    item_counts = Counter(item for transaction in transactions for item in transaction)
    total_items = len(item_counts)

    if total_items == 0:
        return 0.05  # fallback

    # Step 1 & 2: support × utility(=1) per item
    utilities = [count / total_transactions for count in item_counts.values()]
    # Step 3: average utility
    avesup = sum(utilities) / total_items
    # Step 4: minsup = avesup / total_transactions
    minsup = avesup / total_transactions

    return max(0.05, min(0.2, minsup))

# Step 1: Load cleaned data
df = pd.read_csv("data/cleaned_jobs.csv")

# Step 2: Convert IT Skills string back to actual list
df['IT Skills'] = df['IT Skills'].apply(ast.literal_eval)

# Step 3: Filter by career
all_rules = {}
all_freq = {}

for career in df['Query'].unique():
    # Filter by career
    filtered = df[df['Query'] == career]['IT Skills'].tolist()

    # One-hot encode
    te = TransactionEncoder()
    te_array = te.fit_transform(filtered)
    encoded_df = pd.DataFrame(te_array, columns=te.columns_)

    # Run FP-Growth with adaptive minimum support (Hikmawati et al. 2021)
    adaptive_minsup = compute_adaptive_minsup(filtered)
    frequent_itemsets = fpgrowth(encoded_df, min_support=adaptive_minsup, use_colnames=True)
    print(f"  adaptive minsup: {adaptive_minsup:.4f}")

    # Skip if no frequent itemsets found
    if len(frequent_itemsets) == 0:
        continue

    # Save single-item frequent itemsets as skill frequencies
    single_items = frequent_itemsets[frequent_itemsets['itemsets'].apply(lambda x: len(x) == 1)].copy()
    single_items['skill'] = single_items['itemsets'].apply(lambda x: list(x)[0])
    single_items = single_items[['skill', 'support']].sort_values('support', ascending=False)
    all_freq[career] = single_items

    # Generate rules
    rules = association_rules(frequent_itemsets, metric="lift", min_threshold=1)

    # Skip if no rules found
    if len(rules) == 0:
        continue

    rules = rules[rules['consequents'].apply(lambda x: len(x) == 1)]
    rules = rules[rules['antecedents'].apply(lambda x: len(x) <= 3)]
    rules = rules.sort_values('lift', ascending=False)

    all_rules[career] = rules
    print(f"'{career}': {len(rules)} rules generated")

# Save all rules and frequencies
with open('data/arm_rules.pkl', 'wb') as f:
    pickle.dump(all_rules, f)

with open('data/arm_freq.pkl', 'wb') as f:
    pickle.dump(all_freq, f)

print("\nAll rules saved to data/arm_rules.pkl")
print(f"Skill frequencies saved to data/arm_freq.pkl ({len(all_freq)} careers)")

# Run FP-Growth on Soft Skills
import ast
df_soft = pd.read_csv("data/cleaned_soft_skills.csv")
df_soft['Soft Skills'] = df_soft['Soft Skills'].apply(ast.literal_eval)

all_soft_rules = {}

for career in df_soft['Query'].unique():
    filtered = df_soft[df_soft['Query'] == career]['Soft Skills'].tolist()

    te = TransactionEncoder()
    te_array = te.fit_transform(filtered)
    encoded_df = pd.DataFrame(te_array, columns=te.columns_)

    adaptive_minsup = compute_adaptive_minsup(filtered)
    frequent_itemsets = fpgrowth(encoded_df, min_support=adaptive_minsup, use_colnames=True)
    print(f"  adaptive minsup: {adaptive_minsup:.4f}")

    if len(frequent_itemsets) == 0:
        continue

    rules = association_rules(frequent_itemsets, metric="lift", min_threshold=1)

    if len(rules) == 0:
        continue

    rules = rules[rules['consequents'].apply(lambda x: len(x) == 1)]
    rules = rules[rules['antecedents'].apply(lambda x: len(x) <= 3)]
    rules = rules.sort_values('lift', ascending=False)

    all_soft_rules[career] = rules
    print(f"Soft skills — '{career}': {len(rules)} rules generated")

with open('data/soft_rules.pkl', 'wb') as f:
    pickle.dump(all_soft_rules, f)

print("Soft skill rules saved to data/soft_rules.pkl")


