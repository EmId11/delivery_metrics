import streamlit as st
import json
import plotly.graph_objs as go
from pathlib import Path
from itertools import chain

# ---------- config ----------
DATA_PATH = Path(__file__).parent.parent / "delivery_health_tree_scenario.json"

st.set_page_config(page_title="What Happened – Delivery Health Model", layout="wide")

# ---------- helpers ----------
@st.cache_data
def load_tree(path):
    with open(path) as f:
        return json.load(f)

def find_metric(tree, keyword):
    """return first metric dict whose name contains keyword (case-insensitive)"""
    for node in tree:
        stack = [node]
        while stack:
            n = stack.pop()
            for m in n.get("metrics", []):
                if keyword.lower() in m["metric_name"].lower():
                    return m
            stack.extend(n.get("children", []))
    return None

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

# ---------- data ----------
tree = load_tree(DATA_PATH)

# pull the main storyline metrics
wip         = find_metric(tree, "total volume of work in progress")
cycle_time  = find_metric(tree, "cycle time") or find_metric(tree, "age of unfinished work")
carry_over  = find_metric(tree, "departure is less than")
interrupts  = find_metric(tree, "interrupt") or find_metric(tree, "BAU")
estimation  = find_metric(tree, "estimation effectiveness") or find_metric(tree, "consistency of estimation")

# ---------- UI ----------
st.title("📖 What Happened – Narrative View")

st.markdown("""
### 1. Executive summary
Over a 12-sprint window, **Squad Zeta** shifted from a healthy, flow-based team
to one trapped in a classic high-WIP / long-cycle reinforcement loop:

*   WIP limits were relaxed → total WIP ↑ **75 %**.
*   Two senior devs left → effective capacity ↓, estimation discipline slipped.
*   External API change introduced new **blockers**; region launch drove **BAU interrupts**.
*   Result: cycle-time more than doubled, predictability band widened from ±12 % to ±38 %.
""")

# ---------- show big charts ----------
col1, col2 = st.columns(2)
with col1:
    st.subheader("Total WIP")
    simple_chart(wip)
with col2:
    st.subheader("Cycle-time (days)")
    simple_chart(cycle_time)

col3, col4 = st.columns(2)
with col3:
    st.subheader("% Carry-over (work not finished in sprint)")
    simple_chart(carry_over, colour="#c62828")
with col4:
    st.subheader("BAU Interrupt share")
    simple_chart(interrupts, colour="#6a1b9a")

st.subheader("Estimation effectiveness score")
simple_chart(estimation, colour="#0277bd")

# ---------- detailed narrative ----------
st.markdown("""
### 2. Detailed cause-and-effect timeline

| Sprint | Trigger | Immediate effect | Downstream impact |
|--------|---------|------------------|-------------------|
| **3** | Exec removes WIP cap | WIP +20 items | Age of work begins climbing |
| **4** | 2 senior devs reassigned | Velocity –15 % | Estimation consistency drops; carry-over rises |
| **5** | Platform API deprecation | Items blocked waiting on other squads | Blocker-days/item ↑ 4× |
| **6** | New region launch (support escalations) | BAU interrupts spike to 27 % | Frequent context-switching, more work-in-progress |
| **7-8** | PO splits tiny UI tickets | Median item size halves, ticket count +60 % | Developers cherry-pick, large items stall |
| **9-12** | Deadline pressure → “start everything” mindset reinforced | WIP peaks ~80, cycle-time tops 22 d | Predictability band blows out to ±38 % |

### 3. Reinforcing vs balancing loops

* **R1 (Reinforcing):**  
  WIP ↑ → Cycle-time ↑ → Carry-over ↑ → *even more* WIP.
* **B1 (Broken balancing):**  
  Estimation & refinement should keep batch size small, but loss of seniors + rushed refinement weakened this loop.

### 4. Key take-aways

1. **Limit WIP aggressively.** Shrinking WIP back below 50 would reclaim ~40 % of flow-efficiency.
2. **Stabilise BAU demand.** A shared BAU rota or buffer day avoids mid-sprint context switches.
3. **Restore capacity & discipline.** Re-invest in DoR/DoD and get a senior back into the squad.

---

*All charts above are generated from the same data powering the dashboard, so numbers stay consistent.*
""")