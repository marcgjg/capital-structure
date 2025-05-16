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

# ───────────── ℹ️ ABOUT THIS TOOL ───────────── #
with st.expander("ℹ️ About this tool", expanded=False):
    st.markdown(
        """
        This tool helps you visualise the **Trade-off Theory**: tax benefits
        versus distress costs.

        * **Red curve** – levered value with **tax shield only**  
        * **Black curve** – levered value with **tax shield *and* distress costs**  
        * **Indigo dashed line** – un-levered value **V<sub>U</sub>**  
        * **Grey dashed vertical (0 → 250)** – **optimal debt ratio**  
        * Dashed arrows at the optimum show **V<sub>L</sub>** and **PV(tax shield)**
        """,
        unsafe_allow_html=True,
    )

# ───────────── SIDEBAR – THREE SLIDERS ───────────── #
sb = st.sidebar
sb.header("Core inputs")

V_U = sb.slider("Un-levered firm value  Vᵤ  (€ million)",
                50.0, 500.0, 200.0, 10.0)
T_c = sb.slider("Corporate tax rate  T꜀  (%)",
                0.0, 50.0, 25.0, 0.5)

sb.markdown("---")
sb.subheader("Financial-distress costs")

FD_total = sb.slider("PV of distress costs at 100 % debt  (€ million)",
                     0.0, 150.0, 40.0, 1.0)

# ───────────── MODEL CONSTANTS ───────────── #
BETA_DECAY, FD_EXPONENT = 3.0, 2.0    # (tweak if desired)

# ───────────── CALCULATE CURVES ───────────── #
d_pct  = np.arange(0, 101)           # 0 … 100 %
d_frac = d_pct / 100

pv_tax = (T_c / 100) * V_U * d_frac * np.exp(-BETA_DECAY * d_frac)
V_tax  = V_U + pv_tax                # red

pv_fd  = FD_total * d_frac ** FD_EXPONENT
V_L    = V_tax - pv_fd               # black

# optimal debt ratio
opt_idx   = int(np.argmax(V_L))
opt_d_pct = d_pct[opt_idx]
opt_val   = V_L[opt_idx]

# y-values at the optimum
VL_opt   = opt_val
Vtax_opt = V_tax[opt_idx]

# ─────────────────────── PLOT ─────────────────────── #
st.subheader("Value components vs. leverage")

INDIGO = "#6366F1"
fig = go.Figure()

fig.add_trace(go.Scatter(
    x=d_pct, y=V_L,
    mode="lines",
    name="V<sub>L</sub> (with tax & distress)",
    line=dict(color="black", width=3),
))
fig.add_trace(go.Scatter(
    x=d_pct, y=V_tax,
    mode="lines",
    name="V<sub>L</sub> (tax benefit only)",
    line=dict(color="#d62728", width=2),
))

# ── un-levered baseline ────────────────────────────
fig.add_hline(
    y=V_U, line=dict(color=INDIGO, dash="dash"),
    annotation=dict(
        text="V<sub>U</sub> (un-levered)",
        showarrow=False, yshift=-18,
        font=dict(size=12, color=INDIGO),
    ),
)

# ── fixed-height optimal vertical (0 → 250) ────────
fig.add_shape(
    type="line", x0=opt_d_pct, x1=opt_d_pct, y0=0, y1=250,
    line=dict(color="grey", dash="dash"),
)
fig.add_annotation(
    x=opt_d_pct + 2, y=250,
    text=f"Optimal {opt_d_pct:.0f}% debt",
    textangle=-90, showarrow=False,
    font=dict(size=12, color="grey"),
)

# ── dashed arrow: V_L (levered) ─────────────────────
fig.add_shape(
    type="line", x0=opt_d_pct, x1=opt_d_pct, y0=0, y1=VL_opt,
    line=dict(color="black", dash="dot"),
)
fig.add_annotation(
    x=opt_d_pct + 2, y=VL_opt / 2,
    text="V<sub>L</sub> (levered)",
    showarrow=False, font=dict(size=12, color="black"), align="left",
)

# ── dashed arrow: PV tax shield ─────────────────────
fig.add_shape(
    type="line",
    x0=opt_d_pct, x1=opt_d_pct,
    y0=V_U + 1e-6, y1=Vtax_opt,          # tiny offset avoids overlap
    line=dict(color="#d62728", dash="dot"),
)
fig.add_annotation(
    x=opt_d_pct + 2, y=(V_U + Vtax_opt) / 2,
    text="PV (tax shield)",
    showarrow=False, font=dict(size=12, color="#d62728"), align="left",
)

fig.update_layout(
    xaxis_title="Debt as % of Assets",
    yaxis_title="Firm value (€ million)",
    hovermode="x unified",
    font=dict(size=16),
    height=620,
    legend=dict(orientation="h", y=-0.25, x=0.5, xanchor="center"),
    margin=dict(l=80, r=80, t=30, b=40),
    yaxis_range=[0, 260],              # keep the 0–250 frame visible
)

st.plotly_chart(fig, use_container_width=True)

# ───────────────────── SUMMARY ───────────────────── #
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
    st.dataframe(df.style.format("{:.2f}"),
                 use_container_width=True, height=280)

# ───────────────────── FOOTER ───────────────────── #
st.markdown(
    '<div style="text-align:center; padding-top:1rem; color:#6B7280;">'
    'Optimal Capital Structure Visualiser&nbsp;|&nbsp;Developed by Prof.&nbsp;Marc&nbsp;Goergen&nbsp;with&nbsp;the&nbsp;help&nbsp;of&nbsp;ChatGPT'
    '</div>',
    unsafe_allow_html=True,
)
