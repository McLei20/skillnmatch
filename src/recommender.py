import pickle

# ====================== RECOMMENDATION THRESHOLDS ======================
RECOMMENDATION_LIFT = 1.5      # Strong rules shown to users (standard in ARM)

# =======================================================================

def load_rules(path='data/arm_rules.pkl'):
    """Load pre-mined IT skill association rules."""
    with open(path, 'rb') as f:
        return pickle.load(f)


def load_soft_rules(path='data/soft_rules.pkl'):
    """Load pre-mined soft skill association rules."""
    with open(path, 'rb') as f:
        return pickle.load(f)


def load_frequencies(path='data/arm_freq.pkl'):
    """Load skill frequency data (for 'In Demand' chart)."""
    with open(path, 'rb') as f:
        return pickle.load(f)


def recommend_role_skills(career, user_skills, all_rules, top_n=10):
    """
    Recommend skills for a specific career.
    Only returns strong rules (Lift >= 1.5).
    """
    if career not in all_rules:
        return []

    rules = all_rules[career]
    user_set = set(user_skills)
    skill_to_max_lift = {}

    for _, row in rules.iterrows():
        if len(row['consequents']) != 1:
            continue

        skill = list(row['consequents'])[0]
        if skill in user_set:
            continue

        lift = float(row['lift'])
        if lift < RECOMMENDATION_LIFT:
            continue

        # Keep the highest lift for each skill
        if skill not in skill_to_max_lift or lift > skill_to_max_lift[skill]:
            skill_to_max_lift[skill] = lift

    # Sort by lift descending
    ranked = sorted(skill_to_max_lift.items(), key=lambda x: x[1], reverse=True)

    return [{"skill": s, "lift": l} for s, l in ranked[:top_n]]


def recommend_careers(user_skills, all_rules, top_n=5, min_rules=20, weights=(1/3, 1/3, 1/3)):
    """Rank careers based on how well user's skills match each career's rules."""
    w_conf, w_match, w_lift = weights
    w_total = w_conf + w_match + w_lift
    w_conf = w_conf / w_total
    w_match = w_match / w_total
    w_lift = w_lift / w_total

    user_set = set(user_skills)
    career_scores = {}

    for career, rules in all_rules.items():
        if len(rules) < min_rules:
            continue

        matching = rules[rules['antecedents'].apply(lambda x: x <= user_set)]

        if len(matching) == 0:
            continue

        max_lift = rules['lift'].max()
        total_rules = len(rules)

        avg_confidence = matching['confidence'].mean()
        match_count_norm = len(matching) / total_rules
        lift_norm = ((matching['lift'] - 1) / (max_lift - 1)).mean()

        score = (avg_confidence * w_conf) + (match_count_norm * w_match) + (lift_norm * w_lift)
        career_scores[career] = round(score, 4)

    ranked = sorted(career_scores.items(), key=lambda x: x[1], reverse=True)
    return ranked[:top_n]


def recommend_soft_skills(career, all_soft_rules, top_n=5):
    """Recommend soft skills for a career using strong rules only."""
    if career not in all_soft_rules:
        return []

    rules = all_soft_rules[career]
    rules = rules[rules['lift'] >= RECOMMENDATION_LIFT]   # Strong rules only

    top = rules.head(top_n)
    results = []
    seen = set()

    for _, row in top.iterrows():
        skill = list(row['consequents'])[0]
        if skill not in seen:
            results.append({
                'skill': skill.title(),
                'lift': float(row['lift'])
            })
            seen.add(skill)

    return results


def get_skills_from_rules(career, all_rules):
    """Get all skills associated with a career."""
    if career not in all_rules:
        return []

    rules = all_rules[career]
    skills = set()
    for antecedent in rules['antecedents']:
        skills.update(antecedent)

    return sorted(list(skills))


def get_all_skills(all_rules):
    """Get every unique skill across all careers."""
    all_skills = set()
    for career in all_rules.keys():
        all_skills.update(get_skills_from_rules(career, all_rules))
    return sorted(list(all_skills))