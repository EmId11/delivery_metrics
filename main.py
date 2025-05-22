import streamlit as st
import json
import plotly.graph_objs as go

# ----- CONFIG: Force light mode -----
st.set_page_config(page_title="Delivery Health Model Dashboard", layout="wide")
st.markdown("""
    <style>
    body, .stApp { background-color: #f7f7fa !important; color: #111 !important; }
    .metric-card {background: #f9fafb; border-radius: 16px; border: 1.5px solid #e4e6ed;
                  box-shadow: 0 2px 8px #0001; padding: 18px 24px 8px 24px; margin-bottom: 28px;}
    .metric-title {font-weight: 600; color: #009688;}
    .metric-value {font-size: 2.2em; color: #222;}
    .metric-source {font-size: 1em; color: #666;}
    </style>
""", unsafe_allow_html=True)

# ----- Load Data -----
with open("delivery_health_tree_scenario.json") as f:
    tree_data = json.load(f)

def build_radio_options(nodes, parent_path='', level=0):
    result = []
    for node in nodes:
        node_path = f"{parent_path}/{node['indicator']}".strip("/")
        prefix = "&nbsp;" * (4 * level)
        icon = "▶ " if node.get("children") else "• "
        result.append((node_path, f"{prefix}{icon}{node['indicator']}"))
        if node.get("children"):
            result += build_radio_options(node["children"], node_path, level+1)
    return result

all_options = build_radio_options(tree_data)

def find_node_by_path(nodes, path):
    if not path:
        return nodes[0]
    parts = path.strip("/").split("/")
    for node in nodes:
        if node['indicator'] == parts[0]:
            if len(parts) == 1:
                return node
            return find_node_by_path(node.get('children', []), '/'.join(parts[1:]))
    return nodes[0]

def metric_card(metric, target=None, higher_is_better=True):
    values = metric.get("timeseries", [])
    if not values or not all(isinstance(x, (int, float)) for x in values):
        st.warning("No data for this metric.")
        return
    metric_name = metric.get("metric_name", "Metric")
    description = metric.get("description", "")
    unit = metric.get("unit", "")
    y_axis_label = metric.get("y_axis_label", unit or "")
    x_axis_label = "Sprint"

    trend = "up" if values[-1] > values[0] else "down" if values[-1] < values[0] else "neutral"
    delta = values[-1] - values[0]
    val_format = "{:.0f}" if unit in ["count", "days", "sprints"] else "{:.1f}"
    value_display = val_format.format(metric.get("value", 0))
    delta_str = f"{'+' if delta>=0 else ''}{val_format.format(delta)}"
    if unit == "%":
        value_display = f"{metric.get('value', 0):.1f}%"
        delta_str = f"{'+' if delta>=0 else ''}{delta:.1f}%"
    elif unit == "score":
        value_display = f"{metric.get('value', 0):.1f}"
    elif unit and unit not in value_display:
        value_display = f"{value_display} {unit}"

    is_good = (trend == "up" and higher_is_better) or (trend == "down" and not higher_is_better)
    arrow = "▲" if trend == "up" else "▼" if trend == "down" else ""
    arrow_color = "#14d964" if is_good else "#e4572e" if trend != "neutral" else "#aaa"

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        y=values,
        mode="lines+markers",
        line=dict(width=4, color="#009688", shape="spline"),
        marker=dict(size=7, color="#009688"),
        fill="tozeroy",
        fillcolor="rgba(0,150,136,0.09)",
        showlegend=False,
    ))
    if target is not None:
        fig.add_trace(go.Scatter(
            y=[target]*len(values),
            mode="lines",
            line=dict(width=2, dash="dash", color="#ffa726"),
            showlegend=False,
            name="Target",
            hoverinfo="skip"
        ))
    fig.update_layout(
        margin=dict(l=0, r=0, t=0, b=0),
        height=140,
        xaxis=dict(
            showgrid=True,
            gridcolor="#e0e0e0",
            visible=True,
            title=dict(text=x_axis_label, font=dict(color="#444", size=14)),
            showticklabels=True,
            tickfont=dict(color="#222", size=13),
            linecolor="#aaa",
            mirror=True
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor="#e0e0e0",
            visible=True,
            title=dict(text=y_axis_label, font=dict(color="#444", size=14)),
            showticklabels=True,
            tickfont=dict(color="#222", size=13),
            linecolor="#aaa",
            mirror=True
        ),
        plot_bgcolor="#f9fafb",
        paper_bgcolor="#f9fafb",
    )

    info_icon = f"""
        <span title="{description}" style="cursor:pointer;color:#888;font-size:1.2em;margin-left:10px;">
            &#9432;
        </span>
    """ if description else ""

    st.markdown(
        f"""
        <div class="metric-card">
            <div style="font-size:1.16em; color:#009688; font-weight:700; margin-bottom:6px; display: flex; align-items: center;">
                {metric_name} {info_icon}
            </div>
            <div style="display:flex; align-items:center; gap:18px; margin-bottom:10px;">
                <span style="font-size:2.1em; color:#222; font-weight:800;">{value_display}</span>
                <span style="font-size:1.4em; color:{arrow_color}; font-weight:800;">{arrow}</span>
                <span style="font-size:1.13em; color:{arrow_color};">{delta_str}</span>
                <span style="font-size:1.02em; color:#888; margin-left:12px;">(vs start)</span>
            </div>
        """,
        unsafe_allow_html=True,
    )
    st.plotly_chart(fig, use_container_width=True)
    st.markdown("</div></div>", unsafe_allow_html=True)

def children_chips(children):
    if not children:
        return None
    st.markdown("**Children:**")
    for child in children:
        st.markdown(
            f"<span style='display:inline-block; background:#f1f1fa; color:#009688; border-radius:12px; padding:6px 14px; margin:0 8px 8px 0; font-size:1.05em; font-weight:600;'>{child['indicator']}</span>",
            unsafe_allow_html=True
        )

st.title("🟢 Delivery Health Model Dashboard")

# --- Sidebar navigation with indented radios for visible hierarchy ---
radio_labels = [label for path, label in all_options]
radio_map = {label: path for path, label in all_options}

selected_label = st.sidebar.radio(
    "Navigate indicators (parent/child hierarchy is shown visually):", radio_labels, index=0
)
selected_path = radio_map[selected_label]

selected_node = find_node_by_path(tree_data, selected_path)

st.header(selected_node['indicator'])
if selected_node.get("description"):
    st.markdown(f"<div style='color:#444; font-size:1.11em; margin-bottom:18px;'>{selected_node['description']}</div>", unsafe_allow_html=True)
if selected_node.get("data_source"):
    st.markdown(f"<b class='metric-source'>Data source:</b> {selected_node['data_source']}")

if selected_node.get("metrics"):
    st.markdown("### Metrics")
    for metric in selected_node["metrics"]:
        metric_card(metric)

children_chips(selected_node.get("children", []))