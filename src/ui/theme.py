import streamlit as st

_CSS = """
<style>
/* Stepper */
.snm-stepper {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 12px 0;
    margin-bottom: 24px;
    position: sticky;
    top: 0;
    background: #0f1419;
    z-index: 100;
    border-bottom: 1px solid #1a2333;
}
.snm-step {
    padding: 6px 14px;
    border-radius: 999px;
    font-size: 13px;
    font-weight: 600;
    border: 1px solid #2a3a4f;
    color: #8a9aab;
    background: transparent;
}
.snm-step--active {
    background: #14b8a6;
    color: #0f1419;
    border-color: #14b8a6;
}
.snm-step--past {
    border-color: #14b8a6;
    color: #14b8a6;
}
.snm-step--locked {
    color: #4a5a6b;
}
.snm-step-divider {
    flex: 0 0 24px;
    height: 1px;
    background: #2a3a4f;
}

/* Chips */
.snm-chips {
    display: flex;
    flex-wrap: wrap;
    gap: 6px;
    margin: 8px 0;
}
.snm-chip {
    padding: 4px 10px;
    border-radius: 999px;
    font-size: 12px;
    background: #2a3a4f;
    color: #e8edf2;
    border: 1px solid transparent;
}
.snm-chip--selected {
    background: #14b8a6;
    color: #0f1419;
    font-weight: 600;
}
.snm-chip--soft {
    background: #1a2333;
    color: #e8edf2;
    border-color: #2a3a4f;
}

/* Match cards */
.snm-card {
    background: #1a2333;
    border-radius: 6px;
    padding: 14px 16px;
    margin-bottom: 10px;
    border-left: 3px solid #2a3a4f;
}
.snm-card--great { border-left-color: #10b981; }
.snm-card--good { border-left-color: #3b82f6; }
.snm-card--fair { border-left-color: #f59e0b; }
.snm-card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 8px;
}
.snm-card-title {
    font-size: 16px;
    font-weight: 600;
    color: #e8edf2;
}
.snm-badge {
    padding: 2px 8px;
    border-radius: 999px;
    font-size: 10px;
    font-weight: 700;
    text-transform: uppercase;
}
.snm-badge--great { background: #10b981; color: #0f1419; }
.snm-badge--good { background: #3b82f6; color: #fff; }
.snm-badge--fair { background: #f59e0b; color: #0f1419; }
.snm-card-meta {
    font-size: 11px;
    color: #8a9aab;
    margin-bottom: 4px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

/* Section labels */
.snm-section-label {
    font-size: 11px;
    color: #8a9aab;
    text-transform: uppercase;
    letter-spacing: 1px;
    margin: 8px 0 4px 0;
}
</style>
"""

def inject_css() -> None:
    """Inject SkillNMatch CSS into the Streamlit page. Call once near app start."""
    st.markdown(_CSS, unsafe_allow_html=True)
