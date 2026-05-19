import pandas as pd
import re

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

# --- NLP normalization ---

# Citation artifacts that survived earlier filters.
SKILL_JUNK = {'e.g.', 'etc.', 'i.e.', 'e.g', 'etc', 'i.e', '###'}

# variant -> canonical. Direction picked by frequency in the cleaned data.
SKILL_SYNONYMS = {
    # Abbreviations
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
    'gcp': 'google cloud platform',
    # Framework / language variant collapses
    'reactjs': 'react',
    'react.js': 'react',
    'nodejs': 'node.js',
    'vuejs': 'vue.js',
    'postgres': 'postgresql',
    'java script': 'javascript',
    'type script': 'typescript',
    # Vendor-prefix variants
    'microsoft excel': 'excel',
    'ms excel': 'excel',
    'microsoft word': 'word',
    'ms word': 'word',
    'microsoft outlook': 'outlook',
    'microsoft access': 'access',
}

# Tokens that are really a slash-joined list of distinct skills.
SKILL_SPLIT_MAP = {
    'c/c++': ['c', 'c++'],
}

_TRAILING_FILLER = (
    ' skills', ' skill',
    ' tools', ' tool',
    ' technologies', ' technology',
)

# Words ending in -s that are NOT plurals. Must be the LAST word of a skill token
# (e.g. "data analytics" -> last word "analytics" is exempt).
_PLURAL_EXCEPTIONS = {
    'devops', 'jenkins', 'kubernetes', 'microservices',
    'windows', 'angularjs', 'ssrs', 'series', 'news',
    'business', 'wireless', 'objects',  # 'business objects' is a brand
    'aws', 'sas', 'sass', 'css', 'rss',
    'ios', 'macos', 'tls', 'ssl', 'dns', 'aix', 'nas',
}


def _strip_trailing_filler(skill: str) -> str:
    """Drop a trailing ' skill' or ' skills' that adds nothing (e.g. 'communication skills')."""
    for suf in _TRAILING_FILLER:
        if skill.endswith(suf) and skill != suf.strip():
            return skill[: -len(suf)].strip()
    return skill


def _singularize_last_word(skill: str) -> str:
    """Conservatively singularize the trailing word.

    Skips:
      - last word length <= 3 (too short to confidently strip)
      - last word in _PLURAL_EXCEPTIONS (false plurals like 'devops', 'kubernetes')
      - last word ending in '-ics' (analytics, statistics, mathematics, physics, ...)
      - last word containing '.' (node.js, react.js, vb.net)
      - last word ending in -ss/-us/-is/-os/-as (mass, focus, basis, macos, gas)
    """
    parts = skill.split(' ')
    last = parts[-1]
    if len(last) <= 3 or last in _PLURAL_EXCEPTIONS:
        return skill
    if '.' in last:
        return skill
    if last.endswith('ics'):
        return skill
    # libraries -> library
    if last.endswith('ies') and len(last) > 4:
        parts[-1] = last[:-3] + 'y'
        return ' '.join(parts)
    # kisses/boxes/buzzes/churches/bushes -> kiss/box/buzz/church/bush.
    # Only fire on doubled-s ('sses') so 'databases' -> 'database' via the plain -s rule, not 'databas'.
    if last.endswith(('sses', 'xes', 'zes', 'ches', 'shes')) and len(last) > 4:
        parts[-1] = last[:-2]
        return ' '.join(parts)
    # plain -s; skip non-plural endings
    if last.endswith('s') and not last.endswith(('ss', 'us', 'is', 'os', 'as')):
        parts[-1] = last[:-1]
        return ' '.join(parts)
    return skill


def _normalize_token(s: str) -> list[str]:
    """Normalize one raw token. May return zero, one, or many cleaned skills."""
    s = s.strip().lower()
    if not s:
        return []
    if s in SKILL_JUNK:
        return []
    # Must contain at least one letter (drops '###', '50+', pure punctuation).
    if not re.search(r'[a-z]', s):
        return []
    if '*' in s:
        return []
    if s.isdigit():
        return []
    # Multi-skill explode (e.g. 'c/c++' -> ['c', 'c++']) before any other rewriting.
    if s in SKILL_SPLIT_MAP:
        return SKILL_SPLIT_MAP[s]
    # Synonyms run BEFORE singularize so variants ending in -s ('postgres', 'nodejs', 'reactjs')
    # are canonicalized before the plural-stripper would corrupt them.
    s = SKILL_SYNONYMS.get(s, s)
    # Hyphen variants ('problem-solving' -> 'problem solving') collapse with their unhyphenated forms.
    s = s.replace('-', ' ')
    s = ' '.join(s.split())
    if len(s.split()) > 4:
        return []
    s = _strip_trailing_filler(s)
    if not s:
        return []
    s = _singularize_last_word(s)
    # Second pass catches any post-normalization variants.
    s = SKILL_SYNONYMS.get(s, s)
    return [s]


#Extracts skill within parenthesis
def clean_skills(raw_string):
    result = re.sub(r'\(([^)]+)\)', r', \1', raw_string)
    tokens = result.split(',')
    cleaned = set()
    for t in tokens:
        for norm in _normalize_token(t):
            cleaned.add(norm)
    return list(cleaned)

df['IT Skills'] = df['IT Skills'].apply(clean_skills)


print(len(df["IT Skills"]))
print(df["IT Skills"].sample(10))

df[["Query", "IT Skills"]].to_csv("data/cleaned_jobs.csv", index=False)

# Clean Soft Skills column
df_soft = pd.read_csv("data/JobsDatasetProcessed.csv")
df_soft = df_soft.dropna(subset=['Soft Skills'])

def clean_soft_skills(raw_string):
    tokens = raw_string.split(',')
    cleaned = set()
    for t in tokens:
        for norm in _normalize_token(t):
            cleaned.add(norm)
    return list(cleaned)

df_soft['Soft Skills'] = df_soft['Soft Skills'].apply(clean_soft_skills)
df_soft[["Query", "Soft Skills"]].to_csv("data/cleaned_soft_skills.csv", index=False)
print(f"Soft skills saved: {len(df_soft)} rows")