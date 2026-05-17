import streamlit as st
import plotly.express as px
import pandas as pd
import ast
import sys
sys.path.append('src')
from recommender import load_rules, load_frequencies, load_soft_rules, recommend_skills, recommend_soft_skills, get_skills_from_rules, get_all_skills, recommend_careers
from src.ui.theme import inject_css


# Load data and rules
df = pd.read_csv('data/cleaned_jobs.csv')
df['IT Skills'] = df['IT Skills'].apply(ast.literal_eval)
all_rules = load_rules()
all_freq = load_frequencies()
all_soft_rules = load_soft_rules()

inject_css()

# Title
st.title("SkillNMatch")



tab1, tab2, tab3 = st.tabs([
    "Career Fit",
    "Skill Recommendations",
    "Skill Demand"
])

with tab1:
    st.subheader("Find Your Best Career Match")
    all_available_skills = get_all_skills(all_rules)
    career_fit_skills = st.multiselect("Select your current skills", all_available_skills)
    
    if st.button("Find My Career"):
        if len(career_fit_skills) == 0:
            st.warning("Please select at least one skill.")
        else:
            results = recommend_careers(career_fit_skills, all_rules)
            
            if len(results) == 0:
                st.warning("No matching careers found. Try adding more skills.")
            else:
                st.success("Here are the best career matches for your skills:")
                
                medals = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣"]
                
                for i, (career, score) in enumerate(results):
                    if score >= 0.35:
                        label = "Great Match"
                        st.success(f"{medals[i]} **{career}** — {label}")
                    elif score >= 0.25:
                        label = "Good Match"
                        st.info(f"{medals[i]} **{career}** — {label}")
                    else:
                        label = "Fair Match"
                        st.warning(f"{medals[i]} **{career}** — {label}")

with tab2:
    career = st.selectbox("Choose a career", list(all_rules.keys()), key="tab2_career")
    available_skills = get_skills_from_rules(career, all_rules)
    user_skills = st.multiselect("Choose your current skills", available_skills)

    if st.button('Get Recommendations'):
        results = recommend_skills(user_skills, career, all_rules)
        
        if len(results) == 0:
            st.warning("No recommendations found. Try adding more skills.")
        else:
            st.success(f"Found {len(results)} skills to help you qualify for **{career}** roles!")
            
            for r in results:
                lift = r['lift']
                skill = r['skill'].title()
                
                if lift >= 2.0:
                    label = "⭐ Highly Recommended"
                    color = "success"
                elif lift >= 1.5:
                    label = "📈 Recommended"
                    color = "info"
                else:
                    label = "💡 Consider Learning"
                    color = "warning"
                
                if color == "success":
                    st.success(f"**{skill}** — {label}")
                elif color == "info":
                    st.info(f"**{skill}** — {label}")
                else:
                    st.warning(f"**{skill}** — {label}")
            
            # Keep chart but hide raw numbers
            results_df = pd.DataFrame(results)
            results_df_sorted = results_df.sort_values('lift', ascending=True)
            fig = px.bar(
                results_df_sorted, x='lift', y='skill', orientation='h',
                color='lift', color_continuous_scale='teal',
            )
            fig.update_layout(
                title='Skill Relevance Chart',
                xaxis_title='Relevance Score', yaxis_title='',
                xaxis_range=[1, results_df_sorted['lift'].max() + 0.15],
                coloraxis_showscale=False,
                template='plotly_dark',
                margin=dict(l=0, r=20, t=40, b=40),
                height=max(350, len(results_df_sorted) * 40),
            )
            st.plotly_chart(fig, use_container_width=True)

            # Soft skills section
            st.markdown("---")
            st.markdown("### 🤝 Soft Skills Employers Look For")
            soft_results = recommend_soft_skills(career, all_soft_rules)

            if soft_results:
                for r in soft_results:
                    lift = r['lift']
                    skill = r['skill']
                    if lift >= 2.0:
                        st.success(f"**{skill}** — ⭐ Highly Expected")
                    elif lift >= 1.5:
                        st.info(f"**{skill}** — 📈 Commonly Expected")
                    else:
                        st.warning(f"**{skill}** — 💡 Good to Have")
            else:
                st.write("No soft skill data available for this career.")


with tab3:
    # Career dropdown
    career = st.selectbox("Choose a career", list(all_rules.keys()),  key="tab3_career")
    available_skills = get_skills_from_rules(career, all_rules)
    st.subheader(f"Top 10 Most Frequent Skills for {career}")

    # Use ARM-derived support values (single-item frequent itemsets from Apriori)
    if career in all_freq:
        top_skills = all_freq[career].head(10).copy()
        top_skills['support'] = top_skills['support'].round(3)

        # Display table
        top_skills['In-Demand (%)'] = (top_skills['support'] * 100).round(1).astype(str) + '%'
        st.dataframe(top_skills[['skill', 'In-Demand (%)']], use_container_width=True, hide_index=True)

        # Plot
        plot_data = top_skills.sort_values('support', ascending=True)
        fig = px.bar(
            plot_data, x='support', y='skill', orientation='h',
            text=plot_data['support'].apply(lambda v: f'{v:.3f}'),
            color='support',
            color_continuous_scale='teal',
        )
        fig.update_layout(
            title=f'Top 10 Skills by Support — {career}',
            xaxis_title='% of Job Postings Requiring This Skill', yaxis_title='',
            coloraxis_showscale=False,
            template='plotly_dark',
            margin=dict(l=0, r=20, t=40, b=40),
            height=max(350, len(plot_data) * 40),
        )
        fig.update_traces(textposition='outside')
        st.plotly_chart(fig, use_container_width=True)

        st.info("Skills are ranked by how often they appear in real job postings for this career.")
    else:
        st.write("No frequency data available for this career.")

