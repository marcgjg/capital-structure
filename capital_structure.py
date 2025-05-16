import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go

# ───────────────────────── PAGE CONFIG ───────────────────────── #
st.set_page_config(
    page_title="Optimal Capital Structure", page_icon="📐", layout="wide"
)
st.markdown(
    '<h1 style="text-align:center;">Optimal Capital Structure: '
    'Taxes&nbsp;vs&nbsp;Distress</h1>',
    unsafe_allow_html=True,
)

# ─────────────────────── USER INPUTS (3 sliders) ─────────────────── #
sb = st.sidebar
sb.header("Core inputs")

V_U = sb.slider("Un-levered firm value  V₍U₎  (€ m)", 50.0, 500.0, 200.0, 10.0)
T_c = sb.slider("Corporate tax rate  T₍c₎  (%)",      0.0,  50.0,  25.0,  0.5)
FD_total = sb.slider(
    "PV of distress costs at 100 % debt  (€ m)", 0.0, 150.0, 40.0, 1.0
)

# ───────────────────── MODEL CONSTANTS (fixed) ──────────────────── #
TAX_HEIGHT  = 4.0   # scales the red curve’s maximum height
TAX_DECAY   = 3.0   # how fast the tax advantage erodes
FD_EXPONENT = 2.0   # curvature of distress costs  (γ = 2 ⇒ convex)

# ─────────────────────── CALCULATIONS ───────────────────────────── #
d_pct  = np.arange(0, 101)          # 0 … 100 %
d_frac = d_pct / 100                # 0 … 1  (D / Assets)

# Tax advantage (inverse-U)
pv_tax = (
    TAX_HEIGHT
    * (T_c / 100)
    * V_U
    * d_frac**2
    * np.exp(-TAX_DECAY * d_frac)
)
V_tax = V_U + pv_tax                # red curve

# Distress costs (convex)
pv_fd = FD_total * d_frac**FD_EXPONENT
V_L   = V_tax - pv_fd               # black curve

# Locate optimum
opt_idx   = int(np.argmax(V_L))
opt_d_pct = d_pct[opt_idx]
opt_value = V_L[opt_idx]

# Data table
df = pd.DataFrame(
    {
        "Debt %": d_pct,
        "PV Tax Shield": pv_tax,
        "PV Distress Cost": pv_fd,
        "V (Tax only)": V_tax,
        "V Levered": V_L,
    }
)

# ─────────────────────────── PLOT ──────────────────────────────── #
st.subheader("Value components vs. leverage")

fig = go.Figure()

# Black – levered value
fig.add_trace(
    go.Scatter(
        x=d_pct,
        y=V_L,
        mode="lines",
        name="Vₗ  (after distress)",
        line=dict(color="black", width=3),
    )
)

# Red – value with tax benefit only
fig.add_trace(
    go.Scatter(
        x=d_pct,
        y=V_tax,
        mode="lines",
        name="V (tax benefit only)",
        line=dict(color="#d62728", width=2),
    )
)

# Dashed horizontal V_U
fig.add_hline(
    y=V_U,
    line=dict(color="grey", dash="dash"),
    annotation=dict(text="Vᵤ (un-levered)", showarrow=False, yshift=10),
)

# Dashed vertical optimum
fig.add_vline(
    x=opt_d_pct,
    line=dict(color="grey", dash="dash"),
    annotation=dict(
        text=f"Optimal {opt_d_pct:.0f}% debt",
        textangle=-90,
        yshift=10,
        showarrow=False,
    ),
)

fig.update_layout(
    xaxis_title="Debt as % of Assets (≈ D / E)",
    yaxis_title="Firm value (€ m)",
    font=dict(size=16),
    hovermode="x unified",
    height=620,
    legend=dict(orientation="h", y=-0.25, x=0.5, xanchor="center"),
    margin=dict(l=80, r=80, t=30, b=40),
)

st.plotly_chart(fig, use_container_width=True)

st.markdown(
    f"**Optimal capital structure:** **{opt_d_pct:.0f}% debt**, "
    f"levered firm value **€{opt_value:,.1f} m**"
)

with st.expander("Data table"):
    st.dataframe(
        df.style.format("{:.2f}"),
        use_container_width=True,
        height=280,
    )

st.markdown(
    '<div style="text-align:center; font-size:0.85rem; padding-top:1rem;">'
    'Move the three sliders to see how taxes and distress shift the optimum!</div>',
    unsafe_allow_html=True,
)
