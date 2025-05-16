import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go

# ────────────────── PAGE CONFIG ────────────────── #
st.set_page_config(page_title="Optimal Capital Structure",
                   page_icon="📐", layout="wide")
st.markdown(
    '<h1 style="text-align:center; color:#1E3A8A;">📐 Optimal Capital Structure</h1>',
    unsafe_allow_html=True,
)

# ℹ️  ABOUT PANEL ---------------------------------- #
with st.expander("ℹ️ About this tool", expanded=False):
    st.markdown(
        """
        *Trade-off theory visualiser*

        * **Red curve** – value with **tax shield only**  
        * **Black curve** – levered value after distress costs  
        * **Indigo dashed line** – un-levered value (your slider)  
        * **Grey dashed vertical** – optimal debt ratio  
        * **Dashed arrows** – PV (tax shield) & V<sub>L</sub> at the optimum
        """,
        unsafe_allow_html=True,
    )

# ───────────── SIDEBAR INPUTS ───────────── #
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
BETA_DECAY  = 2.0        # controls peak of red curve
FD_EXPONENT = 2.0        # convexity of distress costs

# ─────────── CALCULATIONS ─────────── #
d_pct  = np.arange(0, 101)
d_frac = d_pct / 100

pv_tax = (T_c/100) * V_U * d_frac * np.exp(-BETA_DECAY * d_frac)
V_tax  = V_U + pv_tax               # red curve

pv_fd  = FD_total * d_frac**FD_EXPONENT
V_L    = V_tax - pv_fd              # black curve

opt_idx   = int(np.argmax(V_L))
opt_d_pct = d_pct[opt_idx]
opt_val   = V_L[opt_idx]

# positions for the extra arrows (±1 ppt offset keeps guides separate)
x_VL   = opt_d_pct + 1
x_PVTS = opt_d_pct - 1

# ───────────────────── PLOT ───────────────────── #
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
    y=V_U, line=dict(color=INDIGO, dash="dash"),
    annotation=dict(text="V<sub>U</sub> (un-levered)",
                    showarrow=False, yshift=-18,
                    font=dict(size=12, color=INDIGO)),
)

# optimal grey guide (still at exact opt_d_pct)
fig.add_vline(
    x=opt_d_pct, line=dict(color="grey", dash="dash"),
    annotation=dict(text=f"Optimal {opt_d_pct:.0f}% debt",
                    textangle=-90, showarrow=False, yshift=10),
)

# ── dashed arrow to red curve: PV tax shield ──
fig.add_shape(type="line",
    x0=x_PVTS, x1=x_PVTS,
    y0=V_U + 1e-6, y1=V_tax[opt_idx],
    line=dict(color="#d62728", dash="dot"))
fig.add_annotation(
    x=x_PVTS - 1.5, y=(V_U + V_tax[opt_idx]) / 2,
    text="PV (tax shield)",
    showarrow=False, font=dict(size=12, color="#d62728"),
    align="right",
)

# ── dashed arrow to black curve: V_L ──
fig.add_shape(type="line",
    x0=x_VL, x1=x_VL,
    y0=0, y1=opt_val,
    line=dict(color="black", dash="dot"))
fig.add_annotation(
    x=x_VL + 1.5, y=opt_val / 2,
    text="Value of levered firm",
    showarrow=False, font=dict(size=12, color="black"),
    align="left",
)

fig.update_layout(
    xaxis_title="Debt as % of Assets",
    yaxis_title="Firm value (€ million)",
    hovermode="x unified",
    font=dict(size=16),
    height=620,
    legend=dict(orientation="h", y=-0.25, x=0.5, xanchor="center"),
    margin=dict(l=80, r=80, t=30, b=40),  # no y-axis range → auto-scale
)

st.plotly_chart(fig, use_container_width=True)

# ───────────── SUMMARY ───────────── #
st.markdown(
    f"**Optimal capital structure:** **{opt_d_pct:.0f}% debt**, "
    f"levered firm value **€{opt_val:,.1f} million**"
)

# ───────────── DATA TABLE ───────────── #
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

# ───────────── FOOTER ───────────── #
st.markdown(
    '<div style="text-align:center; padding-top:1rem; color:#6B7280;">'
    'Optimal Capital Structure Visualiser&nbsp;|&nbsp;Developed by Prof.&nbsp;Marc&nbsp;Goergen&nbsp;with the help of&nbsp;ChatGPT'
    '</div>',
    unsafe_allow_html=True,
)
