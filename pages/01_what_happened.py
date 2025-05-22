# pages/01_What_Happened.py
import streamlit as st
import json
from pathlib import Path
import plotly.graph_objs as go

# ───────────────────────────────────────────────────────────────────────────────
#  CONFIG
# ───────────────────────────────────────────────────────────────────────────────
DATA_PATH = (
    Path(__file__).parent.parent / "delivery_health_tree_scenario.json"
)  # adjust if your JSON has a different name

st.set_page_config(page_title="What Happened – Delivery Health Model", layout="wide")

# ───────────────────────────────────────────────────────────────────────────────
#  Helpers
# ───────────────────────────────────────────────────────────────────────────────
@st.cache_data
def load_tree(path):
    with open(path) as f:
        return json.load(f)

def find_metric(tree, keyword: str):
    """Return first metric whose name contains keyword (case-insensitive)."""
    for node in tree:
        stack = [node]
        while stack:
            n = stack.pop()
            for m in n.get("metrics", []):
                if keyword.lower() in m["metric_name"].lower():
                    return m
            stack.extend(n.get("children", []))
    return None

def grab(tree, hint):
    """Gracefully try to pull a metric; warn if not found."""
    m = find_metric(tree, hint)
    if m is None:
        st.warning(f"Metric containing **{hint}** not found in JSON.")
    return m

def simple_chart(metric, colour="#009688"):
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
                hoverinfo="skip",
                showlegend=False,
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

# ───────────────────────────────────────────────────────────────────────────────
#  Load data
# ───────────────────────────────────────────────────────────────────────────────
if not DATA_PATH.exists():
    st.error(f"❌ JSON data file not found at {DATA_PATH.resolve()}")
    st.stop()

tree = load_tree(DATA_PATH)

# ───────────────────────────────────────────────────────────────────────────────
#  Pull narrative-driver metrics
# ───────────────────────────────────────────────────────────────────────────────
wip         = grab(tree, "total volume of work in progress")
cycle_time  = grab(tree, "cycle time") or grab(tree, "age of unfinished work")
carry_over  = grab(tree, "carry-over")  or grab(tree, "departure is less")
interrupts  = grab(tree, "interrupt")   or grab(tree, "BAU")
estimation  = grab(tree, "estimation effectiveness") or grab(tree, "estimation consistency")

key_metrics = dict(
    wip=wip, cycle_time=cycle_time, carry_over=carry_over,
    interrupts=interrupts, estimation=estimation
)
missing = [k for k, m in key_metrics.items() if m is None]
if missing:
    st.error(f"Page cannot render – these key metrics are missing: {', '.join(missing)}")
    st.stop()

# ───────────────────────────────────────────────────────────────────────────────
#  UI – Narrative
# ───────────────────────────────────────────────────────────────────────────────
st.title("📖 What Happened – Narrative View")

st.markdown("""
### 1. Executive summary
Over a 12-sprint window, **Squad Zeta** shifted from a healthy, flow-based team
to one trapped in a classic **high-WIP → long cycle-time** loop:

* WIP limits were relaxed → total WIP ↑ **75 %**  
* Two senior devs left → effective capacity ↓, estimation discipline slipped  
* External API upgrade introduced blockers; region launch drove BAU interrupts  
* Result: cycle-time more than doubled, predictability band widened from ±12 % to ±38 %
""")

# ── big charts
c1, c2 = st.columns(2)
with c1:
    st.subheader("Total WIP")
    simple_chart(wip)
with c2:
    st.subheader("Cycle-time (days)")
    simple_chart(cycle_time)

c3, c4 = st.columns(2)
with c3:
    st.subheader("% Carry-over (work not finished in sprint)")
    simple_chart(carry_over, colour="#c62828")
with c4:
    st.subheader("BAU Interrupt share")
    simple_chart(interrupts, colour="#6a1b9a")

st.subheader("Estimation effectiveness score")
simple_chart(estimation, colour="#0277bd")

st.markdown("""
### 2. Trigger-effect timeline

| Sprint | Trigger | Immediate effect | Down-stream impact |
|--------|---------|------------------|--------------------|
| **3** | WIP cap lifted | WIP +20 items | Age of work climbs |
| **4** | Two seniors reassigned | Velocity –15 % | Estimation consistency dips |
| **5** | Platform API upgrade | Items blocked | Blocked-days ×4 |
| **6** | Region launch (support) | Interrupt items spike | Context-switching ↑ |
| **7-8** | PO splits micro-tickets | Ticket count +60 % | Large items stall |
| **9-12** | Deadline panic | WIP peaks ~80 | Cycle-time tops 22 d |

### 3. Loops

* **R1 (reinforcing):** WIP ↑ → Cycle-time ↑ → Carry-over ↑ → *even more* WIP  
* **B1 (broken):** Estimation & refinement no longer limit batch size, so balance is lost.

### 4. Key take-aways
1. Reinstate strict WIP limit (≤50 items).  
2. Introduce BAU rota to shield sprint work.  
3. Restore senior capacity / pair-mentoring to rebuild estimation discipline.
""")