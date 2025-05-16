import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go

# ─────────────────── PAGE CONFIG ──────────────────── #
st.set_page_config(page_title="Optimal Capital Structure",
                   page_icon="📐", layout="wide")
st.markdown(
    '<h1 style="text-align:center; color:#1E3A8A;">📐 Optimal Capital Structure</h1>',
    unsafe_allow_html=True,
)

# ─────────────── ℹ️ About this tool ──────────────── #
with st.expander("ℹ️ About this tool", expanded=False):
    st.markdown(
        """
        This visualiser shows how **corporate taxes** and **financial-distress
        costs** interact to create an **optimal debt ratio** in the classic
        trade-off theory of capital structure.

        * **Red curve** → value gain from the tax shield *only*  
        * **Black curve** → value after subtracting the PV of distress costs  
        * **Dashed line** → un-levered value Vᵤ  
        * **Vertical arrows** → PV of distress costs at 100 % debt  
        * The **dashed vertical** marks the leverage that maximises firm value.
        """
    )

# ──────────── SIDEBAR – THREE SLIDERS ───────────── #
sb = st.sidebar
sb.header("Core inputs")

V_U = sb.slider("Un-levered firm value  Vᵤ  (€ million)",
                min_value=50.0, max_value=500.0, value=200.0, step=10.0)

T_c = sb.slider("Corporate tax rate  T꜀  (%)",
                min_value=0.0, max_value=50.0, value=25.0, step=0.5)

sb.markdown("---")
sb.subheader("Financial-distress costs")

FD_total = sb.slider("PV of distress costs at 100 % debt  (€ million)",
                     min_value=0.0, max_value=150.0, value=40.0, step=1.0)

# ─────────── HIDDEN SHAPE CONSTANTS ─────────── #
BETA_DECAY  = 3.0   # speed tax advantage decays
FD_EXPONENT = 2.0   # convexity of distress costs

# ─────────── COMPUTE CURVES 0 … 100 % D ────────── #
d_pct  = np.arange(0, 101)          # 0 … 100 %
d_frac = d_pct / 100                # 0 … 1

# Tax benefit (inverse-U)
pv_tax = (T_c / 100) * V_U * d_frac * np.exp(-BETA_DECAY * d_frac)
V_tax  = V_U + pv_tax               # red curve

# Distress costs
pv_fd = FD_total * d_frac ** FD_EXPONENT
V_L   = V_tax - pv_fd               # black curve

# Optimum
opt_idx   = int(np.argmax(V_L))
opt_d_pct = d_pct[opt_idx]
opt_val   = V_L[opt_idx]

# Arrow coordinates at 100 % debt
arrow_x  = 100
arrow_y0 = V_L[-1]                  # black
arrow_y1 = V_tax[-1]                # red
arrow_y_mid = (arrow_y0 + arrow_y1) / 2

# ─────────────────────── PLOT ────────────────────── #
st.subheader("Value components vs. leverage")

fig = go.Figure()

# Black curve
fig.add_trace(
    go.Scatter(
        x=d_pct, y=V_L,
        mode="lines",
        name="V_L (levered)",
        line=dict(color="black", width=3),
    )
)

# Red curve
fig.add_trace(
    go.Scatter(
        x=d_pct, y=V_tax,
        mode="lines",
        name="V (tax benefit only)",
        line=dict(color="#d62728", width=2),
    )
)

# Horizontal dashed V_U
fig.add_hline(
    y=V_U, line=dict(color="grey", dash="dash"),
    annotation=dict(text="Vᵤ  (un-levered)", showarrow=False, yshift=10),
)

# Vertical dashed optimum
fig.add_vline(
    x=opt_d_pct,
    line=dict(color="grey", dash="dash"),
    annotation=dict(
        text=f"Optimal {opt_d_pct:.0f}% debt",
        textangle=-90, yshift=10, showarrow=False,
    ),
)

# Double-arrow for distress cost gap at 100 % debt
fig.add_shape(
    type="line",
    x0=arrow_x, y0=arrow_y0, x1=arrow_x, y1=arrow_y1,
    line=dict(color="grey", width=1),
    arrowside="both", startarrowhead=2, endarrowhead=2,
)
fig.add_annotation(
    x=arrow_x + 2, y=arrow_y_mid,
    text="PV of financial distress costs",
    showarrow=False, font=dict(size=12, color="grey"), align="left",
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

# ─────────────────── NUMERIC SUMMARY ────────────────── #
st.markdown(
    f"**Optimal capital structure:** **{opt_d_pct:.0f}% debt**, "
    f"levered firm value **€{opt_val:,.1f} million**"
)

# ───────────────────── DATA TABLE ───────────────────── #
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

# ───────────────────────── FOOTER ───────────────────── #
st.markdown(
    '<div style="text-align:center; padding-top:1rem; color:#6B7280;">'
    'Optimal Capital Structure Visualiser | Developed by Prof. Marc Goergen &nbsp;•&nbsp; Powered by ChatGPT'
    '</div>',
    unsafe_allow_html=True,
)
