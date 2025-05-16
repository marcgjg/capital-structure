import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go

# ───────────────────── page config ───────────────────── #
st.set_page_config(page_title="Optimal Capital Structure",
                   page_icon="📐", layout="wide")
st.markdown(
    '<h1 style="text-align:center;">Optimal Capital Structure: '
    'Taxes&nbsp;vs&nbsp;Distress</h1>',
    unsafe_allow_html=True,
)

# ─────────────── user-facing inputs (3) ─────────────── #
sb = st.sidebar
sb.header("Core inputs")

V_U = sb.slider("Un-levered firm value  V₍U₎  (€ m)",
                50.0, 500.0, 200.0, 10.0)
T_c = sb.slider("Corporate tax rate  T₍c₎  (%)",
                0.0,  50.0,  25.0,  0.5)
FD_total = sb.slider("PV of distress costs at 100 % debt  (€ m)",
                     0.0, 150.0,  40.0,  1.0)

# ─────────────── fixed shape parameters ─────────────── #
BETA_DECAY   = 3.0      # speed at which tax advantage erodes
FD_EXPONENT  = 2.0      # convexity of distress costs (γ = 2)

# ────────────── compute curves 0 … 100 % D ───────────── #
d_pct  = np.arange(0, 101)         # 0,1,…,100
d_frac = d_pct / 100               # 0…1  (D / Assets)

# inverse-U tax advantage  (linear near zero)
pv_tax = (T_c / 100) * V_U * d_frac * np.exp(-BETA_DECAY * d_frac)
V_tax  = V_U + pv_tax              # red curve

# convex distress costs  (gap equals FD_total at 100 %)
pv_fd = FD_total * d_frac ** FD_EXPONENT
V_L   = V_tax - pv_fd              # black curve

# locate optimum
opt_idx   = int(np.argmax(V_L))
opt_d_pct = d_pct[opt_idx]
opt_val   = V_L[opt_idx]

# numerical check of the gap at 100 % debt
gap_100 = V_tax[-1] - V_L[-1]      # should equal FD_total

# ─────────────────────── plot ─────────────────────── #
st.subheader("Value components vs. leverage")

fig = go.Figure()

fig.add_trace(go.Scatter(
    x=d_pct, y=V_L,
    mode="lines", name="Vₗ  (after distress)",
    line=dict(color="black", width=3),
))
fig.add_trace(go.Scatter(
    x=d_pct, y=V_tax,
    mode="lines", name="V (tax benefit only)",
    line=dict(color="#d62728", width=2),
))
fig.add_hline(
    y=V_U,
    line=dict(color="grey", dash="dash"),
    annotation=dict(text="Vᵤ  (un-levered)", showarrow=False, yshift=10),
)
fig.add_vline(
    x=opt_d_pct,
    line=dict(color="grey", dash="dash"),
    annotation=dict(text=f"Optimal {opt_d_pct:.0f}% debt",
                    textangle=-90, yshift=10, showarrow=False),
)

fig.update_layout(
    xaxis_title="Debt as % of Assets (≈ D/E)",
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
    f"levered value **€{opt_val:,.1f} m**"
)

st.info(
    f"Gap at **100 % debt** = **€{gap_100:,.2f} m** "
    f"(equals slider input **€{FD_total:,.2f} m**).",
    icon="🔍",
)

# ─────────────────────── data table ─────────────────── #
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

st.markdown(
    '<div style="text-align:center; font-size:0.85rem; padding-top:1rem;">'
    'The black curve now rises at low leverage; try different inputs to see '
    'how the optimum shifts.</div>',
    unsafe_allow_html=True,
)
