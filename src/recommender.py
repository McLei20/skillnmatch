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



def recommend_careers(user_skills, all_rules, top_n=5, min_rules=20):
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
        
        score = (avg_confidence * 0.33) + (match_count_norm * 0.33) + (lift_norm * 0.33)
        career_scores[career] = round(score, 4)
    
    ranked = sorted(career_scores.items(), key=lambda x: x[1], reverse=True)
    return ranked[:top_n]

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
    score = (avg_confidence * 0.33) + (match_count_norm * 0.33) + (lift_norm * 0.33)
    print(f"Data Scientist matching: {len(matching)}")
    print(f"Data Scientist score: {round(score, 4)}")
    
    # Career recommendations
    print("\n--- Career Recommendations ---")
    career_results = recommend_careers(user_skills, all_rules)
    for career, score in career_results:
        print(f"{career}: {score}")
    
    print(len(get_all_skills(all_rules)))