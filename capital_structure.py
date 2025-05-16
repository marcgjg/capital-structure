import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go

# ───────────────────── PAGE CONFIG ───────────────────── #
st.set_page_config(page_title="Optimal Capital Structure",
                   page_icon="📐", layout="wide")
st.markdown(
    '<h1 style="text-align:center; color:#1E3A8A;">📐 Optimal Capital Structure</h1>',
    unsafe_allow_html=True,
)

# ℹ️ ABOUT THIS TOOL -------------------------------------------------- #
with st.expander("ℹ️ About this tool", expanded=False):
    st.markdown(
        """
        Change the **corporate tax rate** and the **PV of distress costs** to see
        how they shift the optimal debt ratio.

        * **Red curve** – levered value with **tax shield only**  
        * **Black curve** – levered value with **tax shield and distress costs**  
        * **Horizontal dashed** – un-levered value  
        """,
        unsafe_allow_html=True,
    )

# SIDEBAR INPUTS ------------------------------------------------------ #
sb = st.sidebar
sb.header("Core inputs")

V_U = sb.slider("Unlevered firm value  Vᵤ  (€ million)",
                50.0, 500.0, 200.0, 10.0)
T_c = sb.slider("Corporate tax rate  T꜀  (%)",
                0.0, 50.0, 25.0, 0.5)

sb.markdown("---")
FD_total = sb.slider("PV of distress costs at 100 % debt  (€ million)",
                     0.0, 150.0, 40.0, 1.0)

# MODEL CONSTANTS ----------------------------------------------------- #
BETA_DECAY  = 2.0
FD_EXPONENT = 2.0

# CALCULATE CURVES ---------------------------------------------------- #
d_pct  = np.arange(0, 101)
d_frac = d_pct / 100

pv_tax = (T_c / 100) * V_U * d_frac * np.exp(-BETA_DECAY * d_frac)
V_tax  = V_U + pv_tax

pv_fd  = FD_total * d_frac ** FD_EXPONENT
V_L    = V_tax - pv_fd

opt_idx   = int(np.argmax(V_L))
opt_d_pct = d_pct[opt_idx]
opt_val   = V_L[opt_idx]

# ----------------------------- PLOT ---------------------------------- #
INDIGO = "#6366F1"
fig = go.Figure()

fig.add_trace(go.Scatter(
    x=d_pct, y=V_L, mode="lines",
    name="V<sub>L</sub> (with tax & distress)",
    line=dict(color="black", width=3),
))
fig.add_trace(go.Scatter(
    x=d_pct, y=V_tax, mode="lines",
    name="V<sub>L</sub> (tax benefit only)",
    line=dict(color="#d62728", width=2),
))

# Un-levered baseline
fig.add_hline(
    y=V_U, line=dict(color=INDIGO, dash="dash"),
    annotation=dict(text="V<sub>U</sub> (unlevered)",
                    showarrow=False, yshift=-20,
                    font=dict(size=12, color=INDIGO)),
)

# Optimal-ratio guide
fig.add_vline(
    x=opt_d_pct, line=dict(color="grey", dash="dash"),
    annotation=dict(text=f"Optimal {opt_d_pct:.0f}% debt",
                    textangle=-90, showarrow=False, yshift=10),
)

# NEW — vertical dashed line up to black curve
fig.add_shape(
    type="line",
    x0=opt_d_pct, x1=opt_d_pct,
    y0=0, y1=opt_val,
    line=dict(color="black", dash="dot"),
)
fig.add_annotation(
    x=opt_d_pct + 2,
    y=opt_val / 2,
    text="Value of levered firm",
    showarrow=False,
    font=dict(size=12, color="black"),
    align="left",
)

# Existing PV-distress arrow at 100 % debt
arrow_x, y_black, y_red = 100, V_L[-1], V_tax[-1]
fig.add_shape(type="line",
    x0=arrow_x, x1=arrow_x, y0=y_black, y1=y_red,
    line=dict(color="grey", dash="dot"))
fig.add_annotation(
    x=arrow_x + 2, y=(y_black + y_red) / 2,
    text="PV of financial-distress costs",
    showarrow=False, font=dict(size=12, color="grey"), align="left",
)

fig.update_layout(
    xaxis_title="Debt as % of Assets",
    yaxis_title="Firm value (€ million)",
    hovermode="x unified",
    font=dict(size=16),
    height=620,
    legend=dict(orientation="h", y=-0.25, x=0.5, xanchor="center"),
    margin=dict(l=80, r=80, t=30, b=40),
)

st.plotly_chart(fig, use_container_width=True)

# SUMMARY ------------------------------------------------------------- #
st.markdown(
    f"**Optimal capital structure:** **{opt_d_pct:.0f}% debt**, "
    f"levered firm value **€{opt_val:,.1f} million**"
)

# DATA TABLE ---------------------------------------------------------- #
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

# FOOTER -------------------------------------------------------------- #
st.markdown(
    '<div style="text-align:center; padding-top:1rem; color:#6B7280;">'
    'Optimal Capital Structure Visualiser&nbsp;|&nbsp;Developed by Prof.&nbsp;Marc&nbsp;Goergen&nbsp;with the help of&nbsp;ChatGPT'
    '</div>',
    unsafe_allow_html=True,
)
