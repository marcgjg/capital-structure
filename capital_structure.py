import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go

# ─────────────────────────── CONFIG ──────────────────────────── #

st.set_page_config(
    page_title="Capital-Structure Returns Curve (convex cost of debt)",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    '<h1 style="text-align:center; color:#0F172A;">📈 Capital-Structure Returns Curve</h1>',
    unsafe_allow_html=True,
)

with st.expander("ℹ️ Model logic", expanded=False):
    st.markdown(
        """
        *Fix the operating assumptions on the left.*  
        The plot shows **ROA, ROE and after-tax ROD** for every leverage level
        from 0 % to 100 % debt.  

        * A single cut-off marks the end of the **risk-free plateau**.  
        * Beyond it, the **pre-tax cost of debt rises convexly** toward a chosen
          maximum, *rounded to the nearest 0.05 %* (5 bp) at every step.
        * **Equity is never allowed to fall below a minimum buffer** (default
          0.10 % of total assets) so ROE never drops to zero or becomes “NaN”.
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
    st.subheader("Cost-of-debt parameters")

    base_rate = st.slider("Base (risk-free) rate %", 0.0, 10.0, 4.0, 0.25)

    cut_off = st.slider("Debt % where debt becomes risky", 0, 80, 30, 1)

    max_rate = st.slider(
        "Interest-rate at 100 % debt %",
        min_value=base_rate + 0.25,
        max_value=30.0,
        value=12.0,
        step=0.25,
    )

    convexity = st.slider(
        "Convexity (> 1 → steeper rise)", 1.0, 5.0, 2.0, 0.1
    )

    st.markdown("---")
    st.subheader("Equity buffer")

    min_equity_pct = st.slider(
        "Minimum equity as % of assets (never falls below this)",
        0.00, 5.00, 0.10, 0.01,
        help="Keeps ROE finite even when leverage ≈ 100 %",
    )

# ──────── BUILD CONVEX COST-OF-DEBT CURVE (rounded to 5 bp) ───────── #

debt_pcts = np.arange(0, 101, 1)                      # 0,1,2,…,100 %
interest_rates = np.empty_like(debt_pcts, dtype=float)

# 1) Risk-free plateau
interest_rates[: cut_off + 1] = base_rate

# 2) Convex risky-debt section
if cut_off < 100:
    frac = (debt_pcts[cut_off + 1:] - cut_off) / (100 - cut_off)       # 0 → 1
    interest_rates[cut_off + 1:] = base_rate + (
        max_rate - base_rate
    ) * frac ** convexity
else:  # cut-off = 100 % ⇒ flat line
    interest_rates[cut_off + 1:] = base_rate

# Round every point to the nearest 0.05 % (= 5 bp)
interest_rates = np.round(interest_rates / 0.05) * 0.05

# ─────────────── DERIVE RETURNS FOR EVERY LEVERAGE ─────────────── #

# Enforce a *minimum* equity buffer (in €) at every leverage point
min_equity_value = total_assets * min_equity_pct / 100

debt_vals_raw   = total_assets * debt_pcts / 100
equity_vals     = np.maximum(total_assets - debt_vals_raw, min_equity_value)
debt_vals       = total_assets - equity_vals               # adjusted debt €

ebit         = total_assets * (ebit_margin / 100)
interest_exp = debt_vals * interest_rates / 100
net_income   = (ebit - interest_exp) * (1 - tax_rate / 100)

roa = net_income / total_assets * 100
roe = net_income / equity_vals * 100                       # never div/0 now
rod = np.where(debt_vals == 0, np.nan, interest_rates * (1 - tax_rate / 100))

df = pd.DataFrame(
    {
        "Debt %": debt_pcts,
        "ROA %":  roa,
        "ROE %":  roe,
        "ROD %":  rod,
        "Cost-of-Debt %": interest_rates,
        "Equity €": equity_vals,
        "Debt €": debt_vals,
    }
)

# ──────────────────────────── PLOT ──────────────────────────── #

with col_right:
    st.subheader("Expected returns vs. leverage")

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=df["Debt %"],
            y=df["ROA %"],
            mode="lines",
            name="ROA",
            line=dict(width=3),
            hovertemplate="Debt % %{x}<br>ROA %{y:.2f} %<extra></extra>",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=df["Debt %"],
            y=df["ROE %"],
            mode="lines",
            name="ROE",
            line=dict(width=3, dash="dash"),
            hovertemplate="Debt % %{x}<br>ROE %{y:.2f} %<extra></extra>",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=df["Debt %"],
            y=df["ROD %"],
            mode="lines",
            name="ROD (after-tax)",
            line=dict(width=3, dash="dot"),
            hovertemplate="Debt % %{x}<br>ROD %{y:.2f} %<extra></extra>",
        )
    )

    # Optional: show pre-tax cost of debt on a second axis
    fig.add_trace(
        go.Scatter(
            x=df["Debt %"],
            y=df["Cost-of-Debt %"],
            mode="lines",
            name="Pre-tax Cost of Debt",
            line=dict(width=1, color="grey"),
            yaxis="y2",
            hovertemplate="Debt % %{x}<br>Cost of Debt %{y:.2f} %<extra></extra>",
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

    st.markdown("#### Data (rounded to 5 bp; equity never < buffer)")
    st.dataframe(
        df[["Debt %", "ROA %", "ROE %", "ROD %", "Cost-of-Debt %",
            "Equity €", "Debt €"]]
        .style.format({"ROA %": "{:.2f}", "ROE %": "{:.2f}",
                       "ROD %": "{:.2f}", "Cost-of-Debt %": "{:.2f}",
                       "Equity €": "{:,.2f}", "Debt €": "{:,.2f}"}),
        use_container_width=True,
    )

# ────────────────────────── FOOTER ──────────────────────────── #

st.markdown(
    '<div style="text-align:center; padding-top:1rem;">'
    'Capital-Structure Returns Curve | convex cost of debt with equity buffer'
    "</div>",
    unsafe_allow_html=True,
)
