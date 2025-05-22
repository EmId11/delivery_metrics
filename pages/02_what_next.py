import streamlit as st
import plotly.express as px
import pandas as pd

st.set_page_config(page_title="Comprehensive Delivery Optimisation Playbook", layout="wide")

st.title("📘 Comprehensive Delivery Optimisation Playbook")

st.markdown("""
This Playbook provides clear, detailed, step-by-step guidance for teams new to Agile methodologies, addressing common delivery challenges with practical solutions, clear instructions, and resources for immediate and sustained improvement.
""")

# Section 1: Visual Roadmap
st.header("🚀 Optimisation Roadmap")
roadmap_df = pd.DataFrame({
    "Phase": ["Restore WIP Limits", "Implement BAU Buffer", "Enhance Estimation Discipline", "Capacity Recovery", "Continuous Monitoring"],
    "Start": ["2024-06-01", "2024-07-01", "2024-08-15", "2024-09-01", "2024-11-01"],
    "Finish": ["2024-07-01", "2024-08-15", "2024-09-30", "2024-11-01", "2024-12-31"]
})
fig_roadmap = px.timeline(roadmap_df, x_start="Start", x_end="Finish", y="Phase", color="Phase")
fig_roadmap.update_layout(title='Delivery Optimisation Roadmap', showlegend=False)
st.plotly_chart(fig_roadmap, use_container_width=True)

# Section 2: Comprehensive Approach
st.header("📖 Comprehensive Approach")

approach_tabs = st.tabs(["Core Issues", "Issue Impacts", "Optimisation Overview", "Detailed Phases"])

with approach_tabs[0]:
    st.subheader("Understanding Core Issues")
    st.markdown("""
    Common delivery challenges include high WIP causing frequent task-switching, BAU interruptions reducing predictability, poor estimation practices impacting deadlines and quality, senior resource shortages causing delays in complex problem-solving, and inadequate monitoring preventing proactive improvements.
    """)

with approach_tabs[1]:
    st.subheader("Why Each Issue Matters")
    st.markdown("""
    High WIP extends delivery timelines, BAU interruptions fragment team focus, inaccurate estimations misalign expectations, senior resource shortages slow down critical decisions, and poor monitoring perpetuates systemic issues, diminishing overall productivity and quality.
    """)

with approach_tabs[2]:
    st.subheader("Optimisation Overview")
    st.markdown("""
    This structured approach resolves delivery issues through WIP control, BAU buffer implementation, disciplined estimation, effective capacity management, and continuous monitoring, providing a robust framework for sustainable improvements.
    """)

with approach_tabs[3]:
    st.subheader("Detailed Phases")
    phase_expanders = [
        ("Phase 1 - WIP Limits", "Define optimal WIP limits through analysis, train teams on pull-based workflows, and communicate clear policies."),
        ("Phase 2 - BAU Buffer", "Implement a clearly defined BAU rotation, establish measurable buffer capacity, and train teams on BAU management."),
        ("Phase 3 - Estimation Discipline", "Introduce structured estimation training, enforce DoR and DoD consistently, and regularly review accuracy."),
        ("Phase 4 - Capacity Recovery", "Audit capacity comprehensively, redistribute workloads equitably, and strategically leverage senior resources."),
        ("Phase 5 - Continuous Monitoring", "Deploy dashboards for monitoring key metrics, establish regular review sessions, and foster continuous improvement.")
    ]
    for phase, description in phase_expanders:
        with st.expander(phase):
            st.markdown(description)

# Section 3: Epics and Stories
st.header("📋 Epics and Stories")
epics = {
    "Restore WIP Limits": [
        {"story": "Analyse and define optimal WIP limits", "criteria": "Comprehensive analysis completed; WIP limits peer-reviewed, validated, and approved by team leads."},
        {"story": "Conduct WIP management training", "criteria": "Training sessions delivered; teams assessed for practical understanding and implementation."}
    ],
    "Implement BAU Buffer": [
        {"story": "Develop and communicate BAU rota", "criteria": "BAU rota clearly defined, communicated, adopted, and regularly reviewed."},
        {"story": "Deploy BAU Impact Dashboard", "criteria": "Dashboard functional, accessible, trained on, and regularly utilised by stakeholders."}
    ],
    "Enhance Estimation Discipline": [
        {"story": "Conduct Estimation Techniques Training", "criteria": "Structured training completed; proficiency validated through practical exercises."},
        {"story": "Reinforce DoR and DoD", "criteria": "Clearly documented definitions consistently adopted; adherence periodically verified."}
    ],
    "Capacity Management": [
        {"story": "Conduct Capacity Audit", "criteria": "Audit comprehensively documented, reviewed, and actionable recommendations implemented."},
        {"story": "Allocate Senior Resources", "criteria": "Resource allocation plan documented, senior resources aligned effectively, reviewed regularly."}
    ],
    "Continuous Monitoring": [
        {"story": "Implement Metrics Dashboard", "criteria": "Dashboard deployed, accessible, regularly reviewed and utilised for decision-making."},
        {"story": "Establish Monthly Reviews", "criteria": "Scheduled monthly reviews conducted; minutes captured, actions documented and tracked."}
    ]
}

for epic, stories in epics.items():
    st.subheader(f"Epic: {epic}")
    st.button(f"Export '{epic}' to Jira", key=f"export_{epic}")
    for story in stories:
        st.markdown(f"- **Story:** {story['story']}")
        st.markdown(f"  - **Acceptance Criteria:** {story['criteria']}")
        st.button(f"Export '{story['story']}' to Jira", key=f"export_{story['story']}")

# Section 4: Execution Plan
st.header("🎯 Execution Plan")
st.subheader("Implementation Steps")
st.markdown("Step-by-step guidance including roles, timings, and expected results.")

st.subheader("Change Management & Communication")
st.markdown("Clear stakeholder communication strategies, templates, FAQs, and feedback mechanisms.")

st.subheader("Training & Development")
st.markdown("Comprehensive training resources, interactive training outlines, and ongoing support strategies.")

st.subheader("Monitoring & Continuous Improvement")
st.markdown("Instructions for dashboard setup, regular review processes, and actions for continuous improvement.")

# Section 5: Supporting Visuals
st.header("📊 Supporting Visuals")
st.markdown("Clear graphical visuals illustrating WIP levels, estimation accuracy, BAU interruptions, and resource allocation.")

# Section 6: Recommended External Resources
st.header("📚 Recommended External Resources")
resources = {
    "Kanban WIP Management Guide": "https://kanbanize.com/kanban-resources/kanban-software/what-is-wip-limit",
    "Atlassian Estimation Practices": "https://www.atlassian.com/agile/project-management/estimation",
    "Protecting Teams from Interruptions": "https://www.mountaingoatsoftware.com/blog/protecting-your-team-from-interruptions"
}

for resource, link in resources.items():
    st.markdown(f"- [{resource}]({link})")

# Section 7: Export Functionality
st.header("🛠️ Export Functionality")
st.button("Export Entire Playbook to Confluence")
