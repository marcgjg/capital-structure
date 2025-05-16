import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go

# ────────────────────────── PAGE CONFIG ────────────────────────── #
st.set_page_config(
    page_title="Optimal Capital Structure", page_icon="📐", layout="wide"
)
st.markdown(
    '<h1 style="text-align:center;">Optimal Capital Structure: '
    'Taxes&nbsp;vs&nbsp;Distress</h1>',
    unsafe_allow_html=True,
)

# ────────────────────── SIDEBAR – THREE SLIDERS ───────────────────── #
sb = st.sidebar
sb.header("Core inputs")

V_U = sb.slider(
    "Un-levered firm value  Vᵤ  (€ million)",
    min_value=50.0, max_value=500.0, value=200.0, step=10.0
)

T_c = sb.slider(
    "Corporate tax rate  T꜀  (%)",
    min_value=0.0, max_value=50.0, value=25.0, step=0.5
)

sb.markdown("---")
sb.subheader("Financial-distress costs")

FD_total = sb.slider(
    "PV of distress costs at 100 % debt  (€/ million)",
    min_value=0.0, max_value=150.0, value=40.0, step=1.0
)

# ─────────────────── HIDDEN SHAPE PARAMETERS (FIXED) ───────────────── #
BETA_DECAY  = 3.0   # how fast the tax advantage decays
FD_EXPONENT = 2.0   # convexity of distress costs (γ = 2 keeps gap exact)

# ───────────────────── CALCULATE CURVES (0 … 100 % D) ───────────────── #
d_pct  = np.arange(0, 101)          # leverage in %
d_frac = d_pct / 100                # leverage as fraction of assets

# Tax benefit (inverse-U): linear near origin, exponential decay thereafter
pv_tax = (T_c / 100) * V_U * d_frac * np.exp(-BETA_DECAY * d_frac)
V_tax  = V_U + pv_tax               # red curve

# Distress costs: convex, hits FD_total at d = 1
pv_fd = FD_total * d_frac ** FD_EXPONENT
V_L   = V_tax - pv_fd               # black curve

# Locate optimum of black curve
opt_idx   = int(np.argmax(V_L))
opt_d_pct = d_pct[opt_idx]
opt_val   = V_L[opt_idx]

# Numerical verification of the gap at 100 % debt
gap_100 = V_tax[-1] - V_L[-1]       # should equal FD_total

# ────────────────────────────── PLOT ──────────────────────────────── #
st.subheader("Value components vs. leverage")

fig = go.Figure()

# Black curve – levered value after distress
fig.add_trace(
    go.Scatter(
        x=d_pct, y=V_L,
        mode="lines", name="Vₗ  (after distress)",
        line=dict(color="black", width=3),
    )
)

# Red curve – value with tax only
fig.add_trace(
    go.Scatter(
        x=d_pct, y=V_tax,
        mode="lines", name="V (tax benefit only)",
        line=dict(color="#d62728", width=2),
    )
)

# Dashed horizontal V_U
fig.add_hline(
    y=V_U,
    line=dict(color="grey", dash="dash"),
    annotation=dict(text="Vᵤ  (un-levered)", showarrow=False, yshift=10),
)

# Dashed vertical optimal debt ratio
fig.add_vline(
    x=opt_d_pct,
    line=dict(color="grey", dash="dash"),
    annotation=dict(
        text=f"Optimal {opt_d_pct:.0f}% debt",
        textangle=-90, yshift=10, showarrow=False,
    ),
)

fig.update_layout(
    xaxis_title="Debt as % of Assets (≈ D / E)",
    yaxis_title="Firm value (€/ million)",
    font=dict(size=16),
    hovermode="x unified",
    height=620,
    legend=dict(orientation="h", y=-0.25, x=0.5, xanchor="center"),
    margin=dict(l=80, r=80, t=30, b=40),
)

st.plotly_chart(fig, use_container_width=True)

# ────────────────────────── NUMERIC OUTPUTS ───────────────────────── #
st.markdown(
    f"**Optimal capital structure:** **{opt_d_pct:.0f}% debt**, "
    f"levered firm value **€{opt_val:,.1f} million**"
)

st.info(
    f"At **100 % debt** the red-to-black gap is "
    f"**€{gap_100:,.2f} million** "
    f"(slider input = **€{FD_total:,.2f} million**).",
    icon="🔍",
)

# ─────────────────────────── DATA TABLE ───────────────────────────── #
with st.expander("Data table"):
    df = pd.DataFrame({
        "Debt %": d_pct,
        "PV Tax Shield": pv_tax,
        "PV Distress Cost": pv_fd,
        "V (Tax only)": V_tax,
        "V Levered": V_L,
    })
    st.dataframe(
        df.style.format("{:.2f}"),
        use_container_width=True,
        height=280,
    )

st.markdown(
    '<div style="text-align:center; font-size:0.85rem; padding-top:1rem;">'
    'Move the sliders and watch how taxes and distress interact to determine '
    'the optimal leverage.</div>',
    unsafe_allow_html=True,
)
