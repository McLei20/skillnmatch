"""Skill → category mapping for the Discover step's category filter.

Mapping is hand-curated. Any skill not present here falls through to 'Other'
so the UI never breaks on a new or unseen skill.
"""

# Display order of categories in the UI.
CATEGORY_ORDER = [
    "Languages",
    "Data & ML",
    "Cloud & DevOps",
    "Web",
    "Databases",
    "Tools",
    "Other",
]

# Starter mapping — covers the most common ~60 skills. The engineer should
# extend this after running scripts/dump_uncategorized.py against the real
# rules dataset (see Step 2.7).
SKILL_CATEGORIES: dict[str, str] = {
    # Languages
    "python": "Languages",
    "java": "Languages",
    "javascript": "Languages",
    "typescript": "Languages",
    "c++": "Languages",
    "c#": "Languages",
    "c": "Languages",
    "r": "Languages",
    "scala": "Languages",
    "go": "Languages",
    "ruby": "Languages",
    "php": "Languages",
    "swift": "Languages",
    "kotlin": "Languages",
    "rust": "Languages",
    "sas": "Languages",
    "matlab": "Languages",
    "c/c++": "Languages",

    # Data & ML
    "machine learning": "Data & ML",
    "deep learning": "Data & ML",
    "artificial intelligence": "Data & ML",
    "natural language processing": "Data & ML",
    "computer vision": "Data & ML",
    "tensorflow": "Data & ML",
    "pytorch": "Data & ML",
    "keras": "Data & ML",
    "scikit-learn": "Data & ML",
    "pandas": "Data & ML",
    "numpy": "Data & ML",
    "statistics": "Data & ML",
    "data analysis": "Data & ML",
    "data visualization": "Data & ML",
    "spark": "Data & ML",
    "hadoop": "Data & ML",
    "spss": "Data & ML",
    "stata": "Data & ML",
    "caffe": "Data & ML",
    "algorithms": "Data & ML",
    "analytics": "Data & ML",
    "big data": "Data & ML",
    "big data technologies": "Data & ML",
    "data analytics": "Data & ML",
    "data architecture": "Data & ML",
    "data collection": "Data & ML",
    "data engineering": "Data & ML",
    "data governance": "Data & ML",
    "data integration": "Data & ML",
    "data management": "Data & ML",
    "data manipulation": "Data & ML",
    "data mining": "Data & ML",
    "data modeling": "Data & ML",
    "data science": "Data & ML",
    "data visualization tools": "Data & ML",
    "data warehousing": "Data & ML",
    "extract transform load": "Data & ML",
    "forecasting": "Data & ML",
    "machine learning algorithms": "Data & ML",
    "predictive analytics": "Data & ML",
    "predictive modeling": "Data & ML",
    "reinforcement learning": "Data & ML",
    "reporting": "Data & ML",
    "statistical analysis": "Data & ML",
    "statistical modeling": "Data & ML",
    "business intelligence": "Data & ML",
    "business intelligence tools": "Data & ML",
    "mapreduce": "Data & ML",
    "hdfs": "Data & ML",
    "hive": "Data & ML",
    "pig": "Data & ML",
    "impala": "Data & ML",
    "kafka": "Data & ML",
    "optimization": "Data & ML",

    # Cloud & DevOps
    "aws": "Cloud & DevOps",
    "azure": "Cloud & DevOps",
    "gcp": "Cloud & DevOps",
    "docker": "Cloud & DevOps",
    "kubernetes": "Cloud & DevOps",
    "terraform": "Cloud & DevOps",
    "jenkins": "Cloud & DevOps",
    "ci/cd": "Cloud & DevOps",
    "linux": "Cloud & DevOps",
    "windows": "Cloud & DevOps",
    "devops": "Cloud & DevOps",
    "active directory": "Cloud & DevOps",
    "dns": "Cloud & DevOps",
    "bgp": "Cloud & DevOps",
    "ospf": "Cloud & DevOps",
    "eigrp": "Cloud & DevOps",
    "mpls": "Cloud & DevOps",
    "routing protocols": "Cloud & DevOps",
    "ec2": "Cloud & DevOps",
    "s3": "Cloud & DevOps",
    "redshift": "Cloud & DevOps",
    "performance tuning": "Cloud & DevOps",

    # Web
    "html": "Web",
    "css": "Web",
    "react": "Web",
    "angular": "Web",
    "vue": "Web",
    "node.js": "Web",
    "express": "Web",
    "django": "Web",
    "flask": "Web",
    "rest": "Web",
    "graphql": "Web",
    "application programming interface": "Web",
    "html5": "Web",
    "css3": "Web",
    "angularjs": "Web",
    "ajax": "Web",
    "jquery": "Web",
    "mvc": "Web",

    # Databases
    "sql": "Databases",
    "mysql": "Databases",
    "postgresql": "Databases",
    "mongodb": "Databases",
    "redis": "Databases",
    "oracle": "Databases",
    "nosql": "Databases",
    "database": "Databases",
    "access": "Databases",
    "cassandra": "Databases",
    "hbase": "Databases",
    "relational databases": "Databases",
    "database administration": "Databases",
    "database design": "Databases",
    "database management": "Databases",
    "database querying": "Databases",
    "ssis": "Databases",
    "ssrs": "Databases",

    # Tools
    "git": "Tools",
    "github": "Tools",
    "jira": "Tools",
    "tableau": "Tools",
    "power bi": "Tools",
    "excel": "Tools",
    "vs code": "Tools",
    "agile": "Tools",
    "scrum": "Tools",
    "microsoft excel": "Tools",
    "outlook": "Tools",
    "word": "Tools",
    "business analysis": "Tools",
    "project management": "Tools",
    "process improvement": "Tools",
    "quality assurance": "Tools",
    "requirements gathering": "Tools",
    "user acceptance testing": "Tools",
    "programming": "Tools",
    "programming languages": "Tools",
}


def categorize(skill: str) -> str:
    """Return the category for a skill, defaulting to 'Other' if unmapped."""
    return SKILL_CATEGORIES.get(skill, "Other")


def get_skills_by_category(category: str, all_skills: list[str]) -> list[str]:
    """Return the subset of `all_skills` that fall under `category`, sorted."""
    return sorted(s for s in all_skills if categorize(s) == category)


def get_uncategorized_skills(all_skills: list[str]) -> list[str]:
    """Return the subset of `all_skills` that fall into 'Other'. Useful for
    extending SKILL_CATEGORIES — run scripts/dump_uncategorized.py to see them."""
    return sorted(s for s in all_skills if categorize(s) == "Other")
