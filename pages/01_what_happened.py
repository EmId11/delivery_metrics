# pages/01_What_Happened.py   ← just drop this file into the pages/ folder

import streamlit as st
import json
from pathlib import Path
import plotly.graph_objs as go
import textwrap

# ── configuration ─────────────────────────────────────────
DATA_PATH = Path(__file__).parent.parent / "delivery_health_tree_scenario.json"
st.set_page_config(page_title="What Happened – Delivery Health Model", layout="wide")

# ── helpers ───────────────────────────────────────────────
@st.cache_data
def load_tree(path: Path):
    with open(path) as f:
        return json.load(f)

def iter_metrics(nodes):
    for n in nodes:
        for m in n.get("metrics", []):
            yield m
        yield from iter_metrics(n.get("children", []))

def md(txt: str):
    st.markdown(textwrap.dedent(txt))

def plot(metric: dict, colour="#009688", height=200):
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        y=metric["timeseries"],
        mode="lines+markers",
        line=dict(width=4, shape="spline", color=colour),
        marker=dict(size=7, color=colour),
        fill="tozeroy",
        fillcolor="rgba(0,150,136,0.08)",
        showlegend=False,
    ))
    if "target" in metric:
        fig.add_trace(go.Scatter(
            y=[metric["target"]] * len(metric["timeseries"]),
            mode="lines",
            line=dict(width=2, dash="dash", color="#ffa726"),
            hoverinfo="skip",
            showlegend=False,
        ))
    fig.update_layout(
        height=height,
        margin=dict(l=0, r=0, t=0, b=0),
        xaxis=dict(title="Sprint", showgrid=True, gridcolor="#e0e0e0"),
        yaxis=dict(title=metric.get("y_axis_label", ""), showgrid=True, gridcolor="#e0e0e0"),
        plot_bgcolor="#fafafa",
        paper_bgcolor="#fafafa",
    )
    st.plotly_chart(fig, use_container_width=True)

# ── load data ─────────────────────────────────────────────
if not DATA_PATH.exists():
    st.error(f"❌ JSON not found at {DATA_PATH.resolve()}")
    st.stop()

tree = load_tree(DATA_PATH)
metrics = list(iter_metrics(tree))
name2metric = {m["metric_name"]: m for m in metrics}

# ── sidebar pickers (never crash on wording) ──────────────
st.sidebar.title("📊 Choose metrics driving the story")

def pick(label: str, default_keyword: str):
    opts = list(name2metric.keys())
    idx  = next((i for i, n in enumerate(opts) if default_keyword.lower() in n.lower()), 0)
    sel  = st.sidebar.selectbox(label, opts, index=idx)
    return name2metric[sel]

m_wip = pick("WIP metric",          "work in progress")
m_ct  = pick("Cycle-time metric",   "cycle time")
m_co  = pick("Carry-over metric",   "carry-over")
m_bau = pick("Interrupt metric",    "interrupt")
m_est = pick("Estimation metric",   "estimation")

# ── page content ──────────────────────────────────────────
st.title("📘 What Happened – Narrative View")

md("""
### 1. Executive summary
Over 12 sprints **Squad Zeta** slid from healthy flow to a reinforcing loop of  
**high WIP → long cycle-time → carry-over → even higher WIP**.

* WIP cap lifted (sprint 3)  
* Two senior devs reassigned (sprint 4)  
* API deprecation blockers (sprint 5)  
* Region launch drove BAU interrupts (sprint 6)  
* Flood of micro-tickets (sprints 7-8)

Cycle-time ↑ 140 %, predictability band widened ±12 % → ±38 %.
""")

# charts + explanation
c1, c2 = st.columns(2)
with c1:
    st.subheader("Total WIP")
    plot(m_wip)
    md("**Why:** flood of new tickets & carry-over; arrivals ≫ completions.")
with c2:
    st.subheader("Cycle-time (days)")
    plot(m_ct)
    md("**Why:** Little’s Law – CT ≈ WIP / throughput; throughput fell while WIP rose.")

c3, c4 = st.columns(2)
with c3:
    st.subheader("% Carry-over")
    plot(m_co, colour="#c62828")
    md("Rising carry-over feeds next sprint’s WIP, reinforcing the loop.")
with c4:
    st.subheader("BAU Interrupt share")
    plot(m_bau, colour="#6a1b9a")
    md("Interrupts spiked after Region-C launch, stealing focus mid-sprint.")

st.subheader("Estimation effectiveness score")
plot(m_est, colour="#0277bd")
md("Score fell as refinement was rushed and DoR/DoD applied inconsistently.")

# timeline
md("### 2. Trigger timeline")
timeline = [
    (3, "WIP cap lifted",
        "PO allowed all high-priority epics to start.",
        "WIP +20; work-item age immediately rises."),
    (4, "Two seniors reassigned",
        "Velocity –15 %; remaining devs juggle unfamiliar areas.",
        "Estimation consistency dips; carry-over grows."),
    (5, "API deprecation blockers",
        "Waiting on upstream teams for fixes.",
        "Blocked-days/item × 4; CT rises."),
    (6, "Region-C launch",
        "Support escalations create interrupt items.",
        "Interrupt share jumps 9 % → 27 %; devs context-switch."),
    (7, "Flood of micro-tickets",
        "UX splits ½-day tweaks into standalone tickets.",
        "Ticket count +60 %; devs cherry-pick small tasks."),
    (9, "Deadline panic",
        "Team starts even more items to show progress.",
        "WIP peaks ~80; CT crosses 20 d."),
]
for spr, trig, effect, impact in timeline:
    with st.expander(f"Sprint {spr} — {trig}"):
        md(f"""
**Trigger:** {trig}  
**Immediate effect:** {effect}  
**Down-stream impact:** {impact}
""")

# loops diagram
md("### 3. Feedback loops visualised")
st.markdown(
    """
```mermaid
graph LR
  WIP((WIP)) --> CT((Cycle-time))
  CT         --> Carry(Carry-over)
  Carry      --> WIP
  classDef red stroke:#c62828,color:#c62828;
  class WIP,CT,Carry red;
```""",
    unsafe_allow_html=True,
)

# counter-measures
md("""
### 4. Counter-measures
1. **Re-impose strict WIP limit ≤ 50.** Cuts queue length, shortens CT quickly.  
2. **Add BAU buffer / support rota.** Prevents mid-sprint context-switching.  
3. **Restore senior capacity & reinforce DoR/DoD.** Stabilises estimation discipline.
""")