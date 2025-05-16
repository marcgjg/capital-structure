import streamlit as st
import numpy as np
import plotly.graph_objects as go
import pandas as pd
import uuid

# ───────────────────────── Config & Helpers ────────────────────────── #

st.set_page_config(
    page_title="Capital Structure & Returns Simulator",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded"
)

def get_colors() -> list[str]:
    """Cycling colour palette."""
    return [
        "#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd",
        "#8c564b", "#e377c2", "#7f7f7f", "#bcbd22", "#17becf",
    ]

# ────────────────────────── Header & Help ──────────────────────────── #

st.markdown(
    '<h1 style="text-align:center; color:#0F172A;">🏢 Capital Structure & Returns Simulator</h1>',
    unsafe_allow_html=True,
)

with st.expander("ℹ️ How to use this tool", expanded=False):
    st.markdown(
        """
        1. **Set the firm’s fundamentals** on the left.  
           *EBIT Margin, Tax Rate and Interest Rate all apply to Total Assets.*
        2. **Drag the “Debt %” slider** to change the capital structure  
           (Debt + Equity = 100 % of Assets).
        3. The app computes, in real time  
           - **Return on Assets (ROA)** = Net Income ÷ Total Assets  
           - **Return on Equity (ROE)** = Net Income ÷ Equity  
           - **Return on Debt (after-tax)** = Interest × (1-Tax) ÷ Debt
        4. Press **“➕ Add to Chart”** to store the current scenario and compare it
           side-by-side with others; **“🔄 Reset Chart”** clears them.
        """,
        unsafe_allow_html=True,
    )

# ───────────────────────── Session State ───────────────────────────── #

if "scenarios" not in st.session_state:
    st.session_state.scenarios = {}
    st.session_state.scenario_colors = {}

# ───────────────────────────── Layout ──────────────────────────────── #

col_inputs, col_outputs = st.columns([1, 2])

# ---------- Input column ------------------------------------------------ #

with col_inputs:
    st.subheader("Company Parameters")

    total_assets = st.slider("Total Assets (€ millions)", 10.0, 500.0, 100.0, 10.0)
    ebit_margin = st.slider("EBIT Margin (% of Assets)", 0.0, 30.0, 10.0, 0.5)
    tax_rate    = st.slider("Corporate Tax Rate (%)", 0.0, 50.0, 25.0, 0.5)
    int_rate    = st.slider("Interest Rate on Debt (%)", 0.0, 15.0, 5.0, 0.25)
    debt_pct    = st.slider("Debt as % of Assets", 0, 100, 40, 1)

    # --- Chart controls ---
    st.subheader("Chart Controls")
    add_col, reset_col = st.columns(2)
    with add_col:
        add_btn = st.button("➕ Add to Chart", use_container_width=True)
    with reset_col:
        reset_btn = st.button("🔄 Reset Chart", use_container_width=True)

    if reset_btn:
        st.session_state.scenarios.clear()
        st.session_state.scenario_colors.clear()

# ---------- Calculations ------------------------------------------------ #

ebit         = total_assets * (ebit_margin / 100)
debt         = total_assets * (debt_pct / 100)
equity       = total_assets - debt
interest_exp = debt * (int_rate / 100)
net_income   = (ebit - interest_exp) * (1 - tax_rate / 100)

roa = net_income / total_assets * 100                                   # %
roe = np.nan if equity == 0 else net_income / equity * 100              # %
rod = (
    np.nan
    if debt == 0
    else interest_exp * (1 - tax_rate / 100) / debt * 100               # %
)

# ---------- Metrics ----------------------------------------------------- #

with col_inputs:
    st.subheader("Current Scenario Metrics")
    st.metric("Return on Assets (ROA)", f"{roa:.2f} %")
    st.metric("Return on Equity (ROE)", f"{roe:.2f} %")
    st.metric("Return on Debt (after-tax)", f"{rod:.2f} %")

# ---------- Chart & data column ---------------------------------------- #

with col_outputs:
    st.subheader("Returns Comparison")

    # Base (live) scenario bar
    metrics = ["ROA", "ROE", "ROD"]
    base_vals = [roa, roe, rod]
    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            x=metrics,
            y=base_vals,
            name=f"{debt_pct}% Debt",
            marker_color="#3b82f6",
        )
    )

    # Previously stored scenarios
    for key, (vals, label) in st.session_state.scenarios.items():
        fig.add_trace(
            go.Bar(
                x=metrics,
                y=vals,
                name=label,
                marker_color=st.session_state.scenario_colors[key],
            )
        )

    fig.update_layout(
        barmode="group",
        yaxis_title="Return (%)",
        height=600,
        margin=dict(l=80, r=80, t=80, b=80),
        legend=dict(orientation="h", y=-0.25, x=0.5, xanchor="center"),
        font=dict(size=16),
    )
    st.plotly_chart(fig, use_container_width=True)

    # --- Add scenario button logic ---
    if add_btn:
        label = f"{debt_pct}% Debt"
        key   = uuid.uuid4().hex[:5]
        st.session_state.scenarios[key] = (base_vals, label)
        colour_idx = len(st.session_state.scenario_colors) % len(get_colors())
        st.session_state.scenario_colors[key] = get_colors()[colour_idx]
        st.success(f"Added scenario {label}")

    # --- Tabular detail ---
    st.subheader("Scenario Details")
    df = pd.DataFrame(
        {
            "Debt %":   [debt_pct] + [float(lbl.split("%")[0]) for _, (_, lbl) in st.session_state.scenarios.items()],
            "ROA %":    [roa]      + [vals[0] for _, (vals, _) in st.session_state.scenarios.items()],
            "ROE %":    [roe]      + [vals[1] for _, (vals, _) in st.session_state.scenarios.items()],
            "ROD %":    [rod]      + [vals[2] for _, (vals, _) in st.session_state.scenarios.items()],
        }
    ).set_index("Debt %")
    st.dataframe(df.style.format("{:.2f}"), use_container_width=True)

# ─────────────────────────── Footer ─────────────────────────────────── #

st.markdown(
    '<div class="footer">'
    'Capital Structure & Returns Simulator | Developed by Prof. Marc Goergen & ChatGPT'
    "</div>",
    unsafe_allow_html=True,
)
