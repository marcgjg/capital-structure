import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go

# ─────────────────── PAGE CONFIG ─────────────────── #
st.set_page_config(page_title="Optimal Capital Structure",
                   page_icon="📐", layout="wide")
st.markdown(
    '<h1 style="text-align:center; color:#1E3A8A;">📐 Optimal Capital Structure</h1>',
    unsafe_allow_html=True,
)

# ───────────── ℹ️ ABOUT THIS TOOL ───────────── #
with st.expander("ℹ️ About this tool", expanded=False):
    st.markdown(
        """
        This visualiser shows how **corporate taxes** and **financial-distress
        costs** combine to create an **optimal debt ratio**.

        * **Red curve** – firm value with **tax shield only**  
        * **Black curve** – **levered value** after subtracting distress costs  
        * **Grey dashed line** – un-levered value Vᵤ  
        * **Grey dashed vertical** – value-maximising debt ratio  
        * **Grey vertical dash at 100 % debt** – present value of the distress
          costs you entered
        """
    )

# ───────────── SIDEBAR – THREE SLIDERS ───────────── #
sb = st.sidebar
sb.header("Core inputs")

V_U = sb.slider("Un-levered firm value  Vᵤ  (€ million)",
                50.0, 500.0, 200.0, 10.0)
T_c = sb.slider("Corporate tax rate  T꜀  (%)",
                0.0,  50.0,  25.0,  0.5)

sb.markdown("---")
sb.subheader("Financial-distress costs")

FD_total = sb.slider("PV of distress costs at 100 % debt  (€ million)",
                     0.0, 150.0, 40.0, 1.0)

# ─────────── FIXED SHAPE CONSTANTS ─────────── #
BETA_DECAY  = 3.0        # speed at which tax advantage decays
FD_EXPONENT = 2.0        # convexity of distress costs

# ─────────── COMPUTE CURVES ─────────── #
d_pct  = np.arange(0, 101)          # 0…100 %
d_frac = d_pct / 100                # 0…1

# Tax benefit (inverse-U)
pv_tax = (T_c / 100) * V_U * d_frac * np.exp(-BETA_DECAY * d_frac)
V_tax  = V_U + pv_tax               # red curve

# Distress costs
pv_fd = FD_total * d_frac ** FD_EXPONENT
V_L   = V_tax - pv_fd               # black curve

# Optimum of black curve
opt_idx   = int(np.argmax(V_L))
opt_d_pct = d_pct[opt_idx]
opt_val   = V_L[opt_idx]

# Coordinates for PV distress marker at 100 % debt
arrow_x  = 100
y_black  = V_L[-1]
y_red    = V_tax[-1]
y_mid    = (y_black + y_red) / 2

# ─────────── PLOT ─────────── #
st.subheader("Value components vs. leverage")

fig = go.Figure()

fig.add_trace(go.Scatter(
    x=d_pct, y=V_L,
    mode="lines", name="V_L (levered)",
    line=dict(color="black", width=3),
))
fig.add_trace(go.Scatter(
    x=d_pct, y=V_tax,
    mode="lines", name="V (tax benefit only)",
    line=dict(color="#d62728", width=2),
))

# Horizontal Vᵤ
fig.add_hline(
    y=V_U, line=dict(color="grey", dash="dash"),
    annotation=dict(text="Vᵤ  (un-levered)", showarrow=False, yshift=10),
)

# Optimal vertical
fig.add_vline(
    x=opt_d_pct,
    line=dict(color="grey", dash="dash"),
    annotation=dict(text=f"Optimal {opt_d_pct:.0f}% debt",
                    textangle=-90, yshift=10, showarrow=False),
)

# Distress-cost gap marker at 100 % debt
fig.add_shape(
    type="line",
    x0=arrow_x, x1=arrow_x, y0=y_black, y1=y_red,
    line=dict(color="grey", dash="dot"),
)
fig.add_annotation(
    x=arrow_x + 2, y=y_mid,
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

# ─────────── SUMMARY ─────────── #
st.markdown(
    f"**Optimal capital structure:** **{opt_d_pct:.0f}% debt**, "
    f"levered value **€{opt_val:,.1f} million**"
)

# ─────────── DATA TABLE ─────────── #
with st.expander("Data table"):
    df = pd.DataFrame({
        "Debt %": d_pct,
        "PV Tax Shield": pv_tax,
        "PV Distress Cost": pv_fd,
        "V (Tax only)": V_tax,
        "V Levered": V_L,
    })
    st.dataframe(df.style.format("{:.2f}"),
                 use_container_width=True, height=280)

# ─────────── FOOTER ─────────── #
st.markdown(
    '<div style="text-align:center; padding-top:1rem; color:#6B7280;">'
    'Optimal Capital Structure Visualiser&nbsp;•&nbsp;Developed by Prof.&nbsp;Marc&nbsp;Goergen'
    '</div>',
    unsafe_allow_html=True,
)
