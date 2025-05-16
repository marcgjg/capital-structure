import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go

# ─────────────────────── page config ──────────────────────── #
st.set_page_config(
    page_title="Optimal Capital Structure",
    page_icon="📐",
    layout="wide",
)

st.markdown(
    '<h1 style="text-align:center;">Optimal Capital Structure: Taxes vs. Distress Costs</h1>',
    unsafe_allow_html=True,
)

# ─────────────────────── side-bar inputs ───────────────────── #
sidebar = st.sidebar
sidebar.header("Key assumptions")

V_U = sidebar.slider("Unlevered firm value  V₍U₎  (€ m)", 50.0, 500.0, 200.0, 10.0)
T_c = sidebar.slider("Corporate tax rate  T_c  (%)", 0.0, 50.0, 25.0, 0.5)

sidebar.markdown("---")
sidebar.subheader("Tax-shield utilisation")

alpha = sidebar.slider("α  (speed utilisation falls)", 0.0, 5.0, 1.5, 0.1)
lam   = sidebar.slider("λ  (curvature)",              1.0, 4.0, 2.0, 0.1,
                       help="λ = 1 → simple exponential, λ > 1 → more peaked")

sidebar.markdown("---")
sidebar.subheader("Financial-distress cost function")

k_scale = sidebar.slider("k  (scale)",    0.00, 1.00, 0.20, 0.01)
gamma   = sidebar.slider("γ  (convexity)", 1.0, 4.0, 2.0, 0.1)

# ─────────────────────── core calculations ────────────────── #
d_pct  = np.arange(0, 101)               # 0 … 100 % of assets
d_frac = d_pct / 100                     # 0 … 1

PV_tax = (T_c / 100) * V_U * d_frac * np.exp(-alpha * d_frac ** lam)
V_TS   = V_U + PV_tax

PV_fd  = k_scale * (d_frac ** gamma) * V_U
V_L    = V_TS - PV_fd

opt_idx   = np.argmax(V_L)
opt_d_pct = d_pct[opt_idx]
opt_value = V_L[opt_idx]

df = pd.DataFrame({
    "Debt %":             d_pct,
    "PV Tax Shield":      PV_tax,
    "V_tax (red)":        V_TS,
    "PV Distress Cost":   PV_fd,
    "V_levered (black)":  V_L,
})

# ─────────────────────────── plot ─────────────────────────── #
st.subheader("Value components vs. leverage")

fig = go.Figure()

# black – levered value after distress costs
fig.add_trace(go.Scatter(
    x=d_pct, y=V_L, mode="lines", name="Vₗ  (after distress)",
    line=dict(color="black", width=3)
))

# red – value with tax shield only
fig.add_trace(go.Scatter(
    x=d_pct, y=V_TS, mode="lines", name="Vₜₐₓ  (with corporate tax)",
    line=dict(color="#d62728", width=2)
))

# dashed horizontal V_U
fig.add_hline(
    y=V_U, line=dict(dash="dash", color="grey"),
    annotation=dict(text="Vᵤ", showarrow=False, yshift=10)
)

# dashed vertical optimum
fig.add_vline(
    x=opt_d_pct, line=dict(dash="dash", color="grey"),
    annotation=dict(text=f"Optimal {opt_d_pct:.0f} % debt",
                    textangle=-90, yshift=10, showarrow=False)
)

# cosmetic layout
fig.update_layout(
    xaxis_title="Debt as % of Assets (≈ D / E)",
    yaxis_title="Firm value (€ m)",
    height=620,
    hovermode="x unified",
    legend=dict(orientation="h", y=-0.25, x=0.5, xanchor="center"),
    margin=dict(l=80, r=80, t=30, b=40),
    font=dict(size=16),
)

st.plotly_chart(fig, use_container_width=True)

st.markdown(
    f"**Optimal capital structure:** {opt_d_pct:.0f} % debt  →  "
    f"levered value **€ {opt_value:,.1f} m**"
)

with st.expander("Data table"):
    st.dataframe(
        df.style.format("{:.2f}"),
        use_container_width=True, height=280
    )

st.markdown(
    '<div style="text-align:center; font-size:0.85rem; padding-top:1rem;">'
    'Drag the sliders to see how taxes and distress interact!</div>',
    unsafe_allow_html=True,
)
