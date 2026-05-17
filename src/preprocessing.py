import pandas as pd
import re
from mlxtend.preprocessing import TransactionEncoder
from mlxtend.frequent_patterns import apriori, association_rules

#Load the data
df = pd.read_csv("data\JobsDatasetProcessed.csv")

#Exploring Data
df.info()

#Handling missing value
print(df.isnull().sum())

#Count and Show duplicate rows
print(df.duplicated().sum())
print(df[df.duplicated()])

#Show first rows
print(df.head(10))

print(df['Query'].unique())

df = df.dropna(subset=['IT Skills'])

# Skill synonym mapping (NLP normalization)
SKILL_SYNONYMS = {
    'ml': 'machine learning',
    'ai': 'artificial intelligence',
    'nlp': 'natural language processing',
    'dl': 'deep learning',
    'js': 'javascript',
    'ts': 'typescript',
    'py': 'python',
    'k8s': 'kubernetes',
    'cv': 'computer vision',
    'db': 'database',
    'oop': 'object oriented programming',
    'bi': 'business intelligence',
    'etl': 'extract transform load',
    'api': 'application programming interface',
    'ui': 'user interface',
    'ux': 'user experience',
}

#Extracts skill within parenthesis
def clean_skills(raw_string):
    result = re.sub(r'\(([^)]+)\)', r', \1', raw_string)
    skills = result.split(',')

    cleaned = []
    for s in skills:
        s = s.strip().lower()
        if not s:
            continue
        if len(s.split()) > 4:
            continue
        if '*' in s:
            continue
        if s.isdigit():
            continue
        # Apply synonym mapping
        s = SKILL_SYNONYMS.get(s, s)
        cleaned.append(s)

    return list(set(cleaned))

df['IT Skills'] = df['IT Skills'].apply(clean_skills)


print(len(df["IT Skills"]))
print(df["IT Skills"].sample(10))

df[["Query", "IT Skills"]].to_csv("data/cleaned_jobs.csv", index=False)

# Clean Soft Skills column
df_soft = pd.read_csv("data/JobsDatasetProcessed.csv")
df_soft = df_soft.dropna(subset=['Soft Skills'])

def clean_soft_skills(raw_string):
    skills = raw_string.split(',')

    cleaned = []
    for s in skills:
        s = s.strip().lower()
        if not s:
            continue
        if len(s.split()) > 4:
            continue
        if '*' in s:
            continue
        if s.isdigit():
            continue
        # Apply synonym mapping
        s = SKILL_SYNONYMS.get(s, s)
        cleaned.append(s)

    return list(set(cleaned))

df_soft['Soft Skills'] = df_soft['Soft Skills'].apply(clean_soft_skills)
df_soft[["Query", "Soft Skills"]].to_csv("data/cleaned_soft_skills.csv", index=False)
print(f"Soft skills saved: {len(df_soft)} rows")