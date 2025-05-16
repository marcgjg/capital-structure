import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go

# ─────────── PAGE CONFIG ─────────── #
st.set_page_config(page_title="Optimal Capital Structure",
                   page_icon="📐", layout="wide")
st.markdown('<h1 style="text-align:center; color:#1E3A8A;">📐 Optimal Capital Structure</h1>',
            unsafe_allow_html=True)

# ℹ️  ABOUT PANEL ------------------------------------------------------ #
with st.expander("ℹ️ About this tool", expanded=False):
    st.markdown(
        """
        Visualises the **tax-shield vs. distress-cost** trade-off.

        * **Red** – firm value with **tax shield only**  
        * **Black** – levered value after distress costs  
        * **Indigo dashed** – un-levered value **V<sub>U</sub>**  
        * **Grey dashed vertical** – debt ratio that maximises V<sub>L</sub>  
        * **Dashed arrows** – PV (tax shield) & V<sub>L</sub> at clear offsets  
        * **Grey dotted line at 100 % debt** – PV (distress costs)
        """,
        unsafe_allow_html=True,
    )

# ─────────── SIDEBAR INPUTS ─────────── #
sb = st.sidebar
sb.header("Core inputs")

V_U = sb.slider("Un-levered firm value  Vᵤ  (€ million)",
                50.0, 500.0, 200.0, 10.0)
T_c = sb.slider("Corporate tax rate  T꜀  (%)",
                0.0, 50.0, 25.0, 0.5)

sb.markdown("---")
FD_total = sb.slider("PV of distress costs at 100 % debt  (€ million)",
                     0.0, 150.0, 40.0, 1.0)

# ─────────── MODEL CONSTANTS ─────────── #
BETA_DECAY  = 2.0      # red-curve decay
FD_EXPONENT = 2.0      # distress-cost convexity
OFFSET      = 7        # spacing (ppt) between verticals

# ─────────── CALCULATIONS ─────────── #
d_pct  = np.arange(0, 101)
d_frac = d_pct / 100

pv_tax = (T_c/100) * V_U * d_frac * np.exp(-BETA_DECAY * d_frac)
V_tax  = V_U + pv_tax

pv_fd  = FD_total * d_frac**FD_EXPONENT
V_L    = V_tax - pv_fd

opt_idx   = np.argmax(V_L)
opt_d_pct = int(d_pct[opt_idx])        # integer -- easier offsets

# x-positions for the two arrows
x_left  = max(0,  opt_d_pct - OFFSET)   # PV (tax shield)
x_right = min(100, opt_d_pct + OFFSET)  # V_L arrow

# y-coordinates where the arrows should stop (at their curves)
PVTS_top = V_tax[x_left]
VL_top   = V_L[x_right]

# ─────────── PLOT ─────────── #
INDIGO = "#6366F1"
fig = go.Figure()

fig.add_trace(go.Scatter(
    x=d_pct, y=V_L,
    mode="lines", name="V<sub>L</sub> (levered)",
    line=dict(color="black", width=3),
))
fig.add_trace(go.Scatter(
    x=d_pct, y=V_tax,
    mode="lines", name="V (tax benefit only)",
    line=dict(color="#d62728", width=2),
))

# un-levered baseline
fig.add_hline(
    y=V_U,
    line=dict(color=INDIGO, dash="dash"),
    annotation=dict(text="V<sub>U</sub> (un-levered)",
                    showarrow=False, yshift=-18,
                    font=dict(size=12, color=INDIGO)),
)

# grey optimal guide
fig.add_vline(
    x=opt_d_pct,
    line=dict(color="grey", dash="dash"),
    annotation=dict(text=f"Optimal {opt_d_pct}% debt",
                    textangle=-90, showarrow=False, yshift=10),
)

# dashed arrow → PV (tax shield)
fig.add_shape(type="line",
    x0=x_left, x1=x_left,
    y0=V_U, y1=PVTS_top,
    line=dict(color="#d62728", dash="dot"))
fig.add_annotation(
    x=x_left - 1.5, y=(V_U + PVTS_top)/2,
    text="PV (tax shield)",
    showarrow=False, font=dict(size=12, color="#d62728"),
    align="right",
)

# dashed arrow → Value of levered firm
fig.add_shape(type="line",
    x0=x_right, x1=x_right,
    y0=V_U, y1=VL_top,
    line=dict(color="black", dash="dot"))
fig.add_annotation(
    x=x_right + 1.5, y=(V_U + VL_top)/2,
    text="Value of levered firm",
    showarrow=False, font=dict(size=12, color="black"),
    align="left",
)

# grey dotted line at 100 % debt (PV distress)
fig.add_shape(type="line",
    x0=100, x1=100,
    y0=V_L[-1], y1=V_tax[-1],
    line=dict(color="grey", dash="dot"))
fig.add_annotation(
    x=100 + 1.5, y=(V_L[-1] + V_tax[-1]) / 2,
    text="PV of distress costs",
    showarrow=False, font=dict(size=12, color="grey"),
    align="left",
)

fig.update_layout(
    xaxis_title="Debt as % of Assets",
    yaxis_title="Firm value (€ million)",
    hovermode="x unified",
    font=dict(size=16),
    height=620,
    legend=dict(orientation="h", y=-0.25, x=0.5, xanchor="center"),
    margin=dict(l=80, r=80, t=30, b=40),   # auto-scaled y-axis
)

st.plotly_chart(fig, use_container_width=True)

# ─────────── SUMMARY ─────────── #
st.markdown(
    f"**Optimal capital structure:** **{opt_d_pct}% debt**, "
    f"levered firm value **€{VL_top:,.1f} million**"
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
    'Optimal Capital Structure Visualiser&nbsp;|&nbsp;Developed by Prof.&nbsp;Marc&nbsp;Goergen&nbsp;with the help of&nbsp;ChatGPT'
    '</div>',
    unsafe_allow_html=True,
)
