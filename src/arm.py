import pandas as pd
import ast
from mlxtend.preprocessing import TransactionEncoder
from mlxtend.frequent_patterns import fpgrowth, association_rules
import pickle

# ====================== EVALUATION THRESHOLDS ======================
MIN_SUPPORT = 0.05          # Minimum support (5% of job postings)
MIN_LIFT = 1.0              # Minimum lift for a valid rule (1.0 = no association)
RECOMMENDATION_LIFT = 1.5   # Strong rules we recommend to users

# ===================================================================

# Step 1: Load cleaned data
df = pd.read_csv("data/cleaned_jobs.csv")

# Step 2: Convert string list back to actual Python list
df['IT Skills'] = df['IT Skills'].apply(ast.literal_eval)

all_rules = {}

for career in df['Query'].unique():
    filtered = df[df['Query'] == career]['IT Skills'].tolist()

    # One-hot encoding
    te = TransactionEncoder()
    te_array = te.fit_transform(filtered)
    encoded_df = pd.DataFrame(te_array, columns=te.columns_)

    # Generate frequent itemsets
    frequent_itemsets = fpgrowth(encoded_df, min_support=MIN_SUPPORT, use_colnames=True)
    print(f"  min_support: {MIN_SUPPORT:.2f} for {career}")

    if len(frequent_itemsets) == 0:
        continue

    # Generate rules + calculate Support, Confidence, and Lift
    rules = association_rules(frequent_itemsets,
                              metric="lift",
                              min_threshold=MIN_LIFT)

    if len(rules) == 0:
        continue

    # Filter useful rules only
    rules = rules[rules['consequents'].apply(lambda x: len(x) == 1)]   # Single skill recommendation
    rules = rules[rules['antecedents'].apply(lambda x: len(x) <= 3)]   # Max 3 input skills
    rules = rules[rules['lift'] >= MIN_LIFT]                           # Explicit lift filter

    # Sort by strongest rules first
    rules = rules.sort_values('lift', ascending=False)

    all_rules[career] = rules
    print(f"'{career}': {len(rules)} rules generated")

# Save IT Skills rules
with open('data/arm_rules.pkl', 'wb') as f:
    pickle.dump(all_rules, f)

print("\nAll IT skill rules saved to data/arm_rules.pkl")

# ========================= SOFT SKILLS =========================
df_soft = pd.read_csv("data/cleaned_soft_skills.csv")
df_soft['Soft Skills'] = df_soft['Soft Skills'].apply(ast.literal_eval)

all_soft_rules = {}

for career in df_soft['Query'].unique():
    filtered = df_soft[df_soft['Query'] == career]['Soft Skills'].tolist()

    te = TransactionEncoder()
    te_array = te.fit_transform(filtered)
    encoded_df = pd.DataFrame(te_array, columns=te.columns_)

    frequent_itemsets = fpgrowth(encoded_df, min_support=MIN_SUPPORT, use_colnames=True)

    if len(frequent_itemsets) == 0:
        continue

    rules = association_rules(frequent_itemsets, metric="lift", min_threshold=MIN_LIFT)

    if len(rules) == 0:
        continue

    rules = rules[rules['consequents'].apply(lambda x: len(x) == 1)]
    rules = rules[rules['antecedents'].apply(lambda x: len(x) <= 3)]
    rules = rules[rules['lift'] >= MIN_LIFT]
    rules = rules.sort_values('lift', ascending=False)

    all_soft_rules[career] = rules
    print(f"Soft skills — '{career}': {len(rules)} rules generated")

with open('data/soft_rules.pkl', 'wb') as f:
    pickle.dump(all_soft_rules, f)

print("Soft skill rules saved to data/soft_rules.pkl")