import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go

# ─────────────────────────── CONFIG ──────────────────────────── #

st.set_page_config(
    page_title="Capital-Structure Returns Curve ( piece-wise cost of debt )",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    '<h1 style="text-align:center; color:#0F172A;">🏗️ Capital-Structure Returns Curve</h1>',
    unsafe_allow_html=True,
)

with st.expander("ℹ️ What the model does", expanded=False):
    st.markdown(
        """
        *Fix the operating assumptions on the left.*  
        The chart then shows **ROA, ROE and after-tax ROD for every leverage level
        from 0 % debt to 100 % debt**.  
        <br>

        ### Cost-of-debt behaviour  
        | Region | Debt % range | Interest-rate | Slope |
        |--------|--------------|---------------|-------|
        | **Risk-free** | 0 % → `cut-off 1` | = **Base rate** | 0 |
        | **Moderate**  | `cut-off 1` → `cut-off 2` | linearly ↑ from Base → **Mid rate** | gentle |
        | **High-risk** | `cut-off 2` → 100 % | linearly ↑ from Mid → **Max rate** | steeper |

        Returns are computed *after tax* using  
        &nbsp;&nbsp;• **EBIT** = _EBIT-margin_ × Assets  
        &nbsp;&nbsp;• **Net Income** = (EBIT − Interest) × (1 − Tax)  
        &nbsp;&nbsp;• **ROA** = NI ÷ Assets  • **ROE** = NI ÷ Equity  • **ROD** = Interest × (1 − Tax) ÷ Debt
        """,
        unsafe_allow_html=True,
    )

# ────────────────────────── INPUTS ──────────────────────────── #

col_left, col_right = st.columns([1, 2], gap="large")

with col_left:
    st.subheader("Operating assumptions")

    total_assets = st.slider("Total Assets (€ millions)", 10.0, 500.0, 100.0, 10.0)
    ebit_margin  = st.slider("EBIT margin (% of assets)", 0.0, 30.0, 10.0, 0.5)
    tax_rate     = st.slider("Corporate tax rate (%)", 0.0, 50.0, 25.0, 0.5)

    st.markdown("---")
    st.subheader("Cost-of-debt shape")

    base_rate    = st.slider("Base (risk-free) rate %", 0.0, 10.0, 4.0, 0.25)

    cut1 = st.slider("Debt % where rate starts to rise", 0, 60, 30, 1)
    cut2 = st.slider("Debt % where slope steepens", cut1 + 1, 95, 70, 1)

    mid_rate = st.slider(
        f"Interest-rate at {cut2} % debt %",
        min_value=base_rate,
        max_value=20.0,
        value=6.0,
        step=0.25,
    )
    max_rate = st.slider(
        "Interest-rate at 100 % debt %",
        min_value=mid_rate,
        max_value=30.0,
        value=15.0,
        step=0.25,
    )

# ────────────── BUILD piece-wise COST-OF-DEBT CURVE ────────────── #

debt_pcts = np.arange(0, 101, 1)                    # 0,1,2,…,100 %
interest_rates = np.empty_like(debt_pcts, dtype=float)

# 1) Risk-free plateau
interest_rates[: cut1 + 1] = base_rate

# 2) Gentle slope region
if cut2 > cut1:
    slope1 = (mid_rate - base_rate) / (cut2 - cut1)
    interest_rates[cut1 + 1 : cut2 + 1] = base_rate + slope1 * (
        debt_pcts[cut1 + 1 : cut2 + 1] - cut1
    )
else:  # cut-offs coincide – keep flat until cut2
    interest_rates[cut1 + 1 : cut2 + 1] = mid_rate

# 3) Steeper slope region
if cut2 < 100:
    slope2 = (max_rate - mid_rate) / (100 - cut2)
    interest_rates[cut2 + 1 :] = mid_rate + slope2 * (
        debt_pcts[cut2 + 1 :] - cut2
    )
else:  # cut2 = 100 % ⇒ no steeper region
    interest_rates[cut2 + 1 :] = max_rate

# ─────────────── DERIVE RETURNS FOR EVERY LEVERAGE ─────────────── #

debt_vals   = total_assets * debt_pcts / 100
equity_vals = total_assets - debt_vals

ebit           = total_assets * (ebit_margin / 100)
interest_exp   = debt_vals * interest_rates / 100
net_income     = (ebit - interest_exp) * (1 - tax_rate / 100)

roa = net_income / total_assets * 100
roe = np.where(equity_vals == 0, np.nan, net_income / equity_vals * 100)
rod = np.where(debt_vals == 0, np.nan, interest_rates * (1 - tax_rate / 100))

df = pd.DataFrame(
    {
        "Debt %": debt_pcts,
        "ROA %":  roa,
        "ROE %":  roe,
        "ROD %":  rod,
        "Cost-of-Debt %": interest_rates,          # helpful for hover-tooltips
    }
)

# ──────────────────────────── PLOT ──────────────────────────── #

with col_right:
    st.subheader("Returns as Debt % changes")

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=df["Debt %"],
            y=df["ROA %"],
            mode="lines",
            name="ROA",
            line=dict(width=3),
            hovertemplate="Debt %: %{x}<br>ROA: %{y:.2f} %<extra></extra>",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=df["Debt %"],
            y=df["ROE %"],
            mode="lines",
            name="ROE",
            line=dict(width=3, dash="dash"),
            hovertemplate="Debt %: %{x}<br>ROE: %{y:.2f} %<extra></extra>",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=df["Debt %"],
            y=df["ROD %"],
            mode="lines",
            name="ROD (after-tax)",
            line=dict(width=3, dash="dot"),
            hovertemplate="Debt %: %{x}<br>ROD: %{y:.2f} %<extra></extra>",
        )
    )

    # optional: show cost-of-debt curve on secondary y-axis for context
    fig.add_trace(
        go.Scatter(
            x=df["Debt %"],
            y=df["Cost-of-Debt %"],
            mode="lines",
            name="Pre-tax Cost of Debt",
            line=dict(width=1, color="grey"),
            yaxis="y2",
            hovertemplate="Debt %: %{x}<br>Cost-of-Debt: %{y:.2f} %<extra></extra>",
        )
    )

    fig.update_layout(
        xaxis_title="Debt as % of Assets",
        yaxis=dict(title="Return (%)"),
        yaxis2=dict(
            title="Cost-of-Debt (%)",
            overlaying="y",
            side="right",
            showgrid=False,
            zeroline=False,
        ),
        height=620,
        margin=dict(l=80, r=80, t=20, b=20),
        legend=dict(orientation="h", y=-0.25, x=0.5, xanchor="center"),
        font=dict(size=16),
        hovermode="x unified",
    )

    st.plotly_chart(fig, use_container_width=True)

    st.markdown("#### Data")
    st.dataframe(
        df[["Debt %", "ROA %", "ROE %", "ROD %", "Cost-of-Debt %"]]
        .style.format("{:.2f}"),
        use_container_width=True,
    )

# ────────────────────────── FOOTER ──────────────────────────── #

st.markdown(
    '<div style="text-align:center; padding-top:1rem;">'
    'Capital-Structure Returns Curve | piece-wise cost of debt | MBA Corporate-Finance Lab'
    "</div>",
    unsafe_allow_html=True,
)
