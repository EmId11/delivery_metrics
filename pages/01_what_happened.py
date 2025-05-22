# pages/01_What_Happened.py
import streamlit as st
import json
from pathlib import Path
import plotly.graph_objs as go

# ╭──────────────────────────────────────────────────────────────────────────╮
#  CONFIG
# ╰──────────────────────────────────────────────────────────────────────────╯
DATA_PATH = Path(__file__).parent.parent / "delivery_health_tree_scenario.json"
DEFAULTS = {
    "wip":               ["work in progress", "wip"],
    "cycle_time":        ["cycle time", "age of unfinished"],
    "carry_over":        ["carry-over", "departure is less"],
    "interrupts":        ["interrupt", "bau"],
    "estimation":        ["estimation effectiveness", "estimation consistency"],
}

st.set_page_config(page_title="What Happened – Delivery Health Model", layout="wide")

# ╭──────────────────────────────────────────────────────────────────────────╮
#  Load tree
# ╰──────────────────────────────────────────────────────────────────────────╯
@st.cache_data
def load_tree(path):
    with open(path) as f:
        return json.load(f)

if not DATA_PATH.exists():
    st.error(f"❌ JSON not found at {DATA_PATH}. Put the file at repo root.")
    st.stop()

tree = load_tree(DATA_PATH)

# ╭──────────────────────────────────────────────────────────────────────────╮
#  Flatten all metrics so user can pick interactively
# ╰──────────────────────────────────────────────────────────────────────────╯
def walk_metrics(nodes):
    for n in nodes:
        for m in n.get("metrics", []):
            yield m
        yield from walk_metrics(n.get("children", []))

all_metrics = list(walk_metrics(tree))
metric_names = [m["metric_name"] for m in all_metrics]

def find_by_keywords(keywords):
    for kw in keywords:
        for m in all_metrics:
            if kw.lower() in m["metric_name"].lower():
                return m
    return None

# Sidebar pickers (default to keyword match, else first metric)
st.sidebar.title("📊 Choose metrics for the narrative")
selected_metrics = {}
for key, words in DEFAULTS.items():
    default_metric = find_by_keywords(words) or all_metrics[0]
    sel = st.sidebar.selectbox(
        f"{key.replace('_',' ').title()} metric",
        metric_names,
        index=metric_names.index(default_metric["metric_name"]),
    )
    selected_metrics[key] = next(m for m in all_metrics if m["metric_name"] == sel)

# ╭──────────────────────────────────────────────────────────────────────────╮
#  Chart helper
# ╰──────────────────────────────────────────────────────────────────────────╯
def chart(metric, colour="#009688"):
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            y=metric["timeseries"],
            mode="lines+markers",
            line=dict(width=4, shape="spline", color=colour),
            marker=dict(size=7, color=colour),
            fill="tozeroy",
            fillcolor="rgba(0,150,136,0.08)",
            showlegend=False,
        )
    )
    if "target" in metric:
        fig.add_trace(
            go.Scatter(
                y=[metric["target"]] * len(metric["timeseries"]),
                mode="lines",
                line=dict(width=2, dash="dash", color="#ffa726"),
                showlegend=False,
                hoverinfo="skip",
            )
        )
    fig.update_layout(
        height=220,
        margin=dict(l=0, r=0, t=0, b=0),
        xaxis=dict(title="Sprint", showgrid=True, gridcolor="#e0e0e0"),
        yaxis=dict(title=metric.get("y_axis_label", ""), showgrid=True, gridcolor="#e0e0e0"),
        plot_bgcolor="#fafafa",
        paper_bgcolor="#fafafa",
    )
    st.plotly_chart(fig, use_container_width=True)

# ╭──────────────────────────────────────────────────────────────────────────╮
#  Narrative Page
# ╰──────────────────────────────────────────────────────────────────────────╯
st.title("📖 What Happened – Narrative View")

st.markdown("""
### 1. Executive summary
Over a 12-sprint window the team drifted from controlled flow to a reinforcing
loop of **high WIP → long cycle-time → carry-over → even higher WIP**.
""")

# big charts
c1, c2 = st.columns(2)
with c1:
    st.subheader("Total WIP")
    chart(selected_metrics["wip"])
with c2:
    st.subheader("Cycle-time (days)")
    chart(selected_metrics["cycle_time"])

c3, c4 = st.columns(2)
with c3:
    st.subheader("% Carry-over")
    chart(selected_metrics["carry_over"], colour="#c62828")
with c4:
    st.subheader("BAU Interrupt share")
    chart(selected_metrics["interrupts"], colour="#6a1b9a")

st.subheader("Estimation effectiveness score")
chart(selected_metrics["estimation"], colour="#0277bd")

st.markdown("""
### 2. Trigger timeline
| Sprint | Trigger | Immediate effect | Down-stream impact |
|--------|---------|------------------|--------------------|
| 3 | WIP cap lifted | WIP +20 | Work age rises |
| 4 | Two seniors leave | Velocity –15 % | Estimation slippage |
| 5 | API upgrade needed | Items blocked | Blocker-days ×4 |
| 6 | Region launch | Interrupt items spike | Context-switching |
| 7-8 | Micro-ticket split | Ticket count +60 % | Large items stall |
| 9-12 | Deadline panic | WIP peaks ~80 | Cycle-time 22 d |

### 3. Loops
* **R1** High WIP → longer CT → more carry-over → higher WIP.  
* **B1** Estimation & refinement no longer limit batch size.

### 4. Take-aways
1. Reinstate strict WIP limits.  
2. Shield sprints from BAU via rota/buffer.  
3. Restore senior capacity, rebuild estimation discipline.
""")