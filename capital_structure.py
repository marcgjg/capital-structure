import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go

# ───────────────────────────── App set-up ───────────────────────────── #

st.set_page_config(
    page_title="Capital-Structure Returns Curve",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    '<h1 style="text-align:center; color:#0F172A;">📈 Capital-Structure Returns Curve</h1>',
    unsafe_allow_html=True,
)

with st.expander("ℹ️ What this shows", expanded=False):
    st.markdown(
        """
        *Fix operating assumptions on the left.*  
        The chart on the right plots, **for every possible debt ratio (0 % → 100 %)**:

        | Metric | Formula (after-tax) |
        |--------|---------------------|
        | **ROA** | Net Income ÷ Total Assets |
        | **ROE** | Net Income ÷ Equity |
        | **ROD** | Interest Expense × (1-Tax) ÷ Debt |

        where  
        &nbsp;&nbsp;• **EBIT** = *EBIT-margin* × Assets  
        &nbsp;&nbsp;• **Interest Expense** = *Debt* × Interest-rate  
        &nbsp;&nbsp;• **Net Income** = (EBIT − Interest) × (1 − Tax rate)
        """,
        unsafe_allow_html=True,
    )

# ───────────────────────────── Inputs ──────────────────────────────── #

col_left, col_right = st.columns([1, 2], gap="large")

with col_left:
    st.subheader("Company assumptions")

    total_assets = st.slider("Total Assets (€ millions)", 10.0, 500.0, 100.0, 10.0)
    ebit_margin = st.slider("EBIT-margin (% of assets)", 0.0, 30.0, 10.0, 0.5)
    tax_rate    = st.slider("Corporate tax rate (%)", 0.0, 50.0, 25.0, 0.5)
    int_rate    = st.slider("Interest rate on debt (%)", 0.0, 15.0, 5.0, 0.25)

# ─────────────────────── Calculations over 0-100 % debt ────────────── #

debt_pcts = np.arange(0, 101, 1)           # 0,1,2,…,100 %
debt_vals = total_assets * debt_pcts / 100
equity_vals = total_assets - debt_vals
ebit = total_assets * (ebit_margin / 100)
interest_exp = debt_vals * (int_rate / 100)
net_income = (ebit - interest_exp) * (1 - tax_rate / 100)

roa = net_income / total_assets * 100                       # %
roe = np.where(equity_vals == 0, np.nan, net_income / equity_vals * 100)
rod = np.where(debt_vals == 0, np.nan,
               interest_exp * (1 - tax_rate / 100) / debt_vals * 100)

df = pd.DataFrame(
    {
        "Debt %": debt_pcts,
        "ROA %": roa,
        "ROE %": roe,
        "ROD %": rod,
    }
)

# ───────────────────────────── Plot ────────────────────────────────── #

with col_right:
    st.subheader("How returns evolve as Debt % changes")

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=df["Debt %"],
            y=df["ROA %"],
            mode="lines",
            name="ROA",
            line=dict(width=3),
        )
    )
    fig.add_trace(
        go.Scatter(
            x=df["Debt %"],
            y=df["ROE %"],
            mode="lines",
            name="ROE",
            line=dict(width=3, dash="dash"),
        )
    )
    fig.add_trace(
        go.Scatter(
            x=df["Debt %"],
            y=df["ROD %"],
            mode="lines",
            name="ROD (after-tax)",
            line=dict(width=3, dash="dot"),
        )
    )

    # Highlight the “current” debt = middle slider (just visual aid)
    current_idx = 40  # 40 % as a neutral anchor
    fig.add_vline(
        x=current_idx,
        line_width=1,
        line_dash="dot",
        line_color="gray",
    )

    fig.update_layout(
        xaxis_title="Debt as % of Assets",
        yaxis_title="Return (%)",
        height=600,
        margin=dict(l=80, r=80, t=20, b=20),
        legend=dict(orientation="h", y=-0.25, x=0.5, xanchor="center"),
        font=dict(size=16),
        hovermode="x unified",
    )
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("### Data")
    st.dataframe(df.style.format("{:.2f}"), use_container_width=True)

# ───────────────────────── Footer ──────────────────────────────────── #

st.markdown(
    '<div style="text-align:center; padding-top:1rem;">'
    'Capital-Structure Returns Curve | Developed for MBA Corporate-Finance lab'
    "</div>",
    unsafe_allow_html=True,
)
