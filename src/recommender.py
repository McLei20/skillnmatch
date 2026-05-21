import json

import pandas as pd

# ====================== SETTINGS ======================
RECOMMENDATION_LIFT = 1.5   # Only show strong recommendations (Lift >= 1.5)
# =====================================================


def _load_rules_json(path: str) -> dict:
    """Read a rules JSON file and rebuild {career: DataFrame} with frozenset itemset columns."""
    with open(path, 'r', encoding='utf-8') as f:
        raw = json.load(f)
    out = {}
    for career, rows in raw.items():
        df = pd.DataFrame(rows)
        if not df.empty:
            df['antecedents'] = df['antecedents'].apply(frozenset)
            df['consequents'] = df['consequents'].apply(frozenset)
        out[career] = df
    return out


def load_rules(path='data/arm_rules.json'):
    """Load the main IT skill rules (created by arm.py)"""
    return _load_rules_json(path)


def load_soft_rules(path='data/soft_rules.json'):
    """Load the soft skills rules"""
    return _load_rules_json(path)


# ===================================================================
# 1. Recommend Skills to Learn for a Specific Career
# ===================================================================
def recommend_skills(career, user_skills, all_rules, top_n=10):
    """Recommend new skills the user should learn for a career."""
    if career not in all_rules:
        return []

    rules = all_rules[career]
    user_set = set(user_skills)
    recommendations = {}

    for _, row in rules.iterrows():
        if len(row['consequents']) != 1:        # Only single skill recommendations
            continue
            
        skill = list(row['consequents'])[0]
        
        if skill in user_set:                   # Skip skills user already has
            continue
            
        lift = float(row['lift'])
        if lift < RECOMMENDATION_LIFT:          # Only strong rules
            continue
            
        # Keep the best (highest) lift for each skill
        if skill not in recommendations or lift > recommendations[skill]:
            recommendations[skill] = lift

    # Sort by lift (strongest first) and return top N
    sorted_recs = sorted(recommendations.items(), key=lambda x: x[1], reverse=True)
    
    return [{"skill": skill, "lift": lift} for skill, lift in sorted_recs[:top_n]]


# ===================================================================
# 2. Recommend Careers
# ===================================================================
def recommend_careers(user_skills, all_rules, top_n=5):
    """Rank careers based on user's current skills."""
    user_set = set(user_skills)
    career_scores = {}

    for career, rules in all_rules.items():
        # Find rules where user has all required skills
        matching = rules[rules['antecedents'].apply(lambda x: x <= user_set)]
        
        if len(matching) == 0:
            continue

        # Simple score: average of confidence and lift
        avg_confidence = matching['confidence'].mean()
        avg_lift = matching['lift'].mean()
        
        # Combined score
        score = (avg_confidence + avg_lift) / 2
        career_scores[career] = round(score, 4)

    # Return top careers
    ranked = sorted(career_scores.items(), key=lambda x: x[1], reverse=True)
    return ranked[:top_n]


# ===================================================================
# 3. Recommend Soft Skills
# ===================================================================
def recommend_soft_skills(career, all_soft_rules, top_n=5):
    """Recommend soft skills for a career."""
    if career not in all_soft_rules:
        return []

    rules = all_soft_rules[career]
    
    # Only strong rules
    strong_rules = rules[rules['lift'] >= RECOMMENDATION_LIFT]
    top = strong_rules.head(top_n)

    results = []
    for _, row in top.iterrows():
        skill = list(row['consequents'])[0]
        results.append({
            'skill': skill.title(),
            'lift': float(row['lift'])
        })
    return results


# ===================================================================
# Helper Functions
# ===================================================================
def get_all_skills(all_rules):
    """Get list of all available skills (used in Discover step)"""
    all_skills = set()
    for rules in all_rules.values():
        for antecedent in rules['antecedents']:
            all_skills.update(antecedent)
    return sorted(list(all_skills))


# For testing
if __name__ == "__main__":
    all_rules = load_rules()
    user_skills = ['python', 'sql', 'machine learning']
    
    print("Top Careers:")
    print(recommend_careers(user_skills, all_rules))
    
    print("\nSkills to learn for Data Scientist:")
    print(recommend_skills("Data Scientist", user_skills, all_rules))