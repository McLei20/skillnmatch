import pickle


def load_rules(path='data/arm_rules.pkl'):
    with open(path, 'rb') as f:
        return pickle.load(f)

def load_frequencies(path='data/arm_freq.pkl'):
    with open(path, 'rb') as f:
        return pickle.load(f)

def load_soft_rules(path='data/soft_rules.pkl'):
    with open(path, 'rb') as f:
        return pickle.load(f)

def recommend_skills(user_skills, career, all_rules, top_n=10):
    # Check if career has rules
    if career not in all_rules:
        return []
    
    rules = all_rules[career]
    user_set = set(user_skills)
    
    # Step 1: Find rules where antecedent is subset of user skills
    matching = rules[rules['antecedents'].apply(
        lambda x: x <= user_set
    )]
    
    # Step 2 & 3: Get consequents, remove skills user already has
    recommendations = []
    for _, row in matching.iterrows():
        skill = list(row['consequents'])[0]
        if skill not in user_set:
            recommendations.append({
                'skill': skill,
                'confidence': row['confidence'],
                'lift': row['lift']
            })

    seen = {}
    for r in recommendations:
        skill = r['skill']
        if skill not in seen or r['lift'] > seen[skill]['lift']:
            seen[skill] = r
    # Convert back to list
    recommendations = list(seen.values())
    
    # Step 4: Sort by lift
    recommendations = sorted(recommendations, key=lambda x: x['lift'], reverse=True)
    
    # Step 5: Return top N
    return recommendations[:top_n]


def recommend_role_skills(career, user_skills, all_rules, top_n=10):
    """Rank skills by how strongly this role's rules point at them.

    For every single-consequent rule in the career, take the consequent's
    highest lift across all such rules. Filter out skills the user already
    has, sort by max lift descending, return the top N.

    This answers "what does this role need?" -- independent of which rule
    antecedents the user happens to match.
    """
    if career not in all_rules:
        return []

    rules = all_rules[career]
    user_set = set(user_skills)
    skill_to_max_lift: dict[str, float] = {}

    for _, row in rules.iterrows():
        if len(row['consequents']) != 1:
            continue
        skill = list(row['consequents'])[0]
        if skill in user_set:
            continue
        lift = float(row['lift'])
        if skill not in skill_to_max_lift or lift > skill_to_max_lift[skill]:
            skill_to_max_lift[skill] = lift

    ranked = sorted(skill_to_max_lift.items(), key=lambda x: x[1], reverse=True)
    return [{"skill": s, "lift": l} for s, l in ranked[:top_n]]


def recommend_careers(user_skills, all_rules, top_n=5, min_rules=20, weights=(1/3, 1/3, 1/3)):
    """Rank careers by how well a user's skills match each career's ARM rules.

    Weighting: the three metrics (avg_confidence, match_count_norm, lift_norm)
    are combined with EQUAL weights by default. No labeled ground truth exists
    to optimize weights against, so unequal weights would impose arbitrary
    researcher bias. Equal (unit) weighting is the established neutral baseline
    in multi-criteria decision analysis, robust under small samples and
    correlated criteria (Dawes 1979, American Psychologist 34(7):571-582). The
    `weights` argument lets sensitivity_analysis() re-score under alternative
    weightings to confirm the ranking is not an artifact of this choice
    (standard MCDA robustness check; Wieckowski & Salabun 2023). Weights are
    normalized to sum to 1, so the default (1/3,1/3,1/3) sums to exactly 1.0 --
    avoiding the rounding error of 0.33 + 0.33 + 0.33 = 0.99.
    """
    w_conf, w_match, w_lift = weights
    w_total = w_conf + w_match + w_lift
    w_conf, w_match, w_lift = w_conf / w_total, w_match / w_total, w_lift / w_total

    user_set = set(user_skills)
    career_scores = {}
    
    for career, rules in all_rules.items():
        # Skip careers with too few rules
        if len(rules) < min_rules:
            continue
        
        # Find matching rules ← this was missing!
        matching = rules[rules['antecedents'].apply(
            lambda x: x <= user_set
        )]
        
        if len(matching) == 0:
            continue
        
        # Normalize metrics
        max_lift = rules['lift'].max()
        total_rules = len(rules)
        
        avg_confidence = matching['confidence'].mean()
        match_count_norm = len(matching) / total_rules
        lift_norm = ((matching['lift'] - 1) / (max_lift - 1)).mean()
        
        score = (avg_confidence * w_conf) + (match_count_norm * w_match) + (lift_norm * w_lift)
        career_scores[career] = round(score, 4)
    
    ranked = sorted(career_scores.items(), key=lambda x: x[1], reverse=True)
    return ranked[:top_n]

def sensitivity_analysis(user_skills, all_rules, top_n=5):
    """Test whether career rankings depend on the choice of metric weights.

    Re-runs recommend_careers() under several weightings and reports how stable
    the top-N ranking is. Stability across very different weightings shows the
    result is not an artifact of the (unavoidably arbitrary) weight choice --
    the standard robustness argument in multi-criteria decision analysis
    (Wieckowski & Salabun 2023; Demir et al. 2024).
    """
    import pandas as pd

    scenarios = {
        "Equal (baseline)":    (1/3, 1/3, 1/3),
        "Confidence-heavy":    (0.60, 0.20, 0.20),
        "Match-heavy":         (0.20, 0.60, 0.20),
        "Lift-heavy":          (0.20, 0.20, 0.60),
        "Prior (0.6/0.1/0.3)": (0.60, 0.10, 0.30),
    }

    results = {
        name: recommend_careers(user_skills, all_rules, top_n=top_n, weights=w)
        for name, w in scenarios.items()
    }

    table = {}
    for name, ranked in results.items():
        col = [c for c, _ in ranked]
        col += ["-"] * (top_n - len(col))
        table[name] = col
    df = pd.DataFrame(table, index=[f"#{i+1}" for i in range(top_n)])

    baseline = [c for c, _ in results["Equal (baseline)"]]
    print(f"\nSensitivity analysis -- skills: {sorted(set(user_skills))}")
    print(df.to_string())

    print("\nStability vs Equal baseline:")
    for name, ranked in results.items():
        if name == "Equal (baseline)":
            continue
        careers = [c for c, _ in ranked]
        top1_same = careers[:1] == baseline[:1]
        overlap = len(set(careers) & set(baseline))
        print(f"  {name:<22} top-1 same: {str(top1_same):<5}  overlap top-{top_n}: {overlap}/{top_n}")

    return results


def recommend_soft_skills(career, all_soft_rules, top_n=5):
    if career not in all_soft_rules:
        return []
    
    rules = all_soft_rules[career]
    
    # Get most confident single-consequent rules
    top = rules.head(top_n)
    results = []
    seen = set()
    
    for _, row in top.iterrows():
        skill = list(row['consequents'])[0]
        if skill not in seen:
            results.append({
                'skill': skill.title(),
                'lift': row['lift']
            })
            seen.add(skill)
    
    return results

def get_skills_from_rules(career, all_rules):
    if career not in all_rules:
        return []
    
    rules = all_rules[career]
    skills = set()
    
    for antecedent in rules['antecedents']:
        skills.update(antecedent)
    
    return sorted(list(skills))

def get_all_skills(all_rules):
    all_skills = set()
    for career in all_rules.keys():
        all_skills.update(get_skills_from_rules(career, all_rules))
    return sorted(list(all_skills))

if __name__ == "__main__":
    all_rules = load_rules()
    user_skills = ['python', 'sql', 'machine learning', 'statistics']
    user_set = set(user_skills)
    
    # Data Scientist
    rules = all_rules['Data Scientist']
    matching = rules[rules['antecedents'].apply(lambda x: x <= user_set)]
    max_lift = rules['lift'].max()
    avg_confidence = matching['confidence'].mean()
    match_count_norm = len(matching) / len(rules)
    lift_norm = ((matching['lift'] - 1) / (max_lift - 1)).mean()
    score = (avg_confidence + match_count_norm + lift_norm) / 3
    print(f"Data Scientist matching: {len(matching)}")
    print(f"Data Scientist score: {round(score, 4)}")
    
    # Career recommendations
    print("\n--- Career Recommendations ---")
    career_results = recommend_careers(user_skills, all_rules)
    for career, score in career_results:
        print(f"{career}: {score}")

    print(len(get_all_skills(all_rules)))

    print()
    sensitivity_analysis(user_skills, all_rules)