import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go

# ─────────── PAGE CONFIG ─────────── #
st.set_page_config(page_title="Optimal Capital Structure",
                   page_icon="📐", layout="wide")
st.markdown(
    '<h1 style="text-align:center; color:#1E3A8A;">📐 Optimal Capital Structure</h1>',
    unsafe_allow_html=True,
)

# ───────── ℹ️ ABOUT (collapsible) ───────── #
with st.expander("ℹ️ About this tool", expanded=False):
    st.markdown(
        """
        Trade-off Theory visualiser: compares **tax shield** (red) against
        **financial-distress costs** (black minus red).

        * **Indigo dashed line** → un-levered value **V<sub>U</sub> = 100 m**  
        * **Grey dashed vertical (50 → 250)** → value-maximising debt ratio  
        * Dashed arrows at the optimum mark **V<sub>L</sub>** and **PV(tax shield)**
        """,
        unsafe_allow_html=True,
    )

# ───────── SIDEBAR – TWO INPUTS ───────── #
sb = st.sidebar
sb.header("Inputs")

T_c = sb.slider("Corporate tax rate  T꜀  (%)", 0.0, 50.0, 25.0, 0.5)

sb.markdown("---")
FD_total = sb.slider("PV of distress costs at 100 % debt  (€ m)",
                     0.0, 150.0, 40.0, 1.0)

# ───────── FIXED CONSTANTS ───────── #
V_U          = 100.0   # € m  (fixed)
BETA_DECAY   = 3.0     # exponential decay of tax shield
TAX_HEIGHT   = 6.0     # height scaler  ↑ makes curve peak higher
FD_EXPONENT  = 2.0     # distress-cost convexity

# ───────── CALCULATE CURVES ───────── #
d_pct  = np.arange(0, 101)
d      = d_pct / 100     # D/A

pv_tax = TAX_HEIGHT * (T_c/100) * V_U * d**2 * np.exp(-BETA_DECAY * d)
V_tax  = V_U + pv_tax                  # red curve

pv_fd  = FD_total * d**FD_EXPONENT
V_L    = V_tax - pv_fd                 # black curve

# optimal D
opt_idx   = int(np.argmax(V_L))
opt_d_pct = d_pct[opt_idx]
opt_val   = V_L[opt_idx]
VL_opt    = opt_val
Vtax_opt  = V_tax[opt_idx]

# ───────── PLOT ───────── #
st.subheader("Value components vs. leverage")

INDIGO = "#6366F1"
fig = go.Figure()

fig.add_trace(go.Scatter(
    x=d_pct, y=V_L, mode="lines",
    name="V<sub>L</sub> (levered)",
    line=dict(color="black", width=3),
))
fig.add_trace(go.Scatter(
    x=d_pct, y=V_tax, mode="lines",
    name="V (tax benefit only)",
    line=dict(color="#d62728", width=2),
))

# V_U baseline
fig.add_hline(
    y=V_U,
    line=dict(color=INDIGO, dash="dash"),
    annotation=dict(text="V<sub>U</sub> = 100 m",
                    showarrow=False, yshift=-18,
                    font=dict(size=12, color=INDIGO)),
)

# Fixed vertical guide 50→250
fig.add_shape(type="line",
    x0=opt_d_pct, x1=opt_d_pct, y0=50, y1=250,
    line=dict(color="grey", dash="dash"))
fig.add_annotation(
    x=opt_d_pct + 2, y=250,
    text=f"Optimal {opt_d_pct:.0f}% debt",
    textangle=-90, showarrow=False, font=dict(size=12, color="grey"),
)

# Arrow to V_L
fig.add_shape(type="line",
    x0=opt_d_pct, x1=opt_d_pct, y0=50, y1=VL_opt,
    line=dict(color="black", dash="dot"))
fig.add_annotation(
    x=opt_d_pct + 2, y=(50+VL_opt)/2,
    text="V<sub>L</sub> (levered)",
    showarrow=False, font=dict(size=12, color="black"), align="left",
)

# Arrow to PV tax shield
fig.add_shape(type="line",
    x0=opt_d_pct, x1=opt_d_pct, y0=V_U+1e-6, y1=Vtax_opt,
    line=dict(color="#d62728", dash="dot"))
fig.add_annotation(
    x=opt_d_pct + 2, y=(V_U+Vtax_opt)/2,
    text="PV (tax shield)",
    showarrow=False, font=dict(size=12, color="#d62728"), align="left",
)

fig.update_layout(
    xaxis_title="Debt as % of Assets",
    yaxis_title="Firm value (€ m)",
    hovermode="x unified",
    font=dict(size=16),
    height=620,
    legend=dict(orientation="h", y=-0.25, x=0.5, xanchor="center"),
    margin=dict(l=80, r=80, t=30, b=40),
    yaxis_range=[0, 260],
)

st.plotly_chart(fig, use_container_width=True)

# ───────── SUMMARY ───────── #
st.markdown(
    f"**Optimal capital structure:** **{opt_d_pct:.0f}% debt**, "
    f"levered firm value **€{opt_val:,.1f} million**"
)

# ───────── DATA TABLE ───────── #
with st.expander("Data table"):
    df = pd.DataFrame({
        "Debt %": d_pct, "PV Tax Shield": pv_tax,
        "PV Distress Cost": FD_total * d**FD_EXPONENT,
        "V (Tax only)": V_tax, "V Levered": V_L,
    })
    st.dataframe(df.style.format("{:.2f}"),
                 use_container_width=True, height=280)

# ───────── FOOTER ───────── #
st.markdown(
    '<div style="text-align:center; padding-top:1rem; color:#6B7280;">'
    'Optimal Capital Structure Visualiser&nbsp;|&nbsp;Developed by Prof.&nbsp;Marc&nbsp;Goergen&nbsp;with the help of&nbsp;ChatGPT'
    '</div>',
    unsafe_allow_html=True,
)
