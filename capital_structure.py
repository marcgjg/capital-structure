import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go

# ─────────────────────────── page config ──────────────────────────── #
st.set_page_config(page_title="Optimal Capital Structure", page_icon="📐", layout="wide")

st.markdown(
    '<h1 style="text-align:center;">Optimal Capital Structure: Taxes vs Distress</h1>',
    unsafe_allow_html=True,
)

# ────────────────────────── sidebar inputs ────────────────────────── #
sb = st.sidebar
sb.header("Key assumptions")

V_U = sb.slider("Unlevered firm value  V₍U₎  (€ m)", 50.0, 500.0, 200.0, 10.0)
T_c = sb.slider("Corporate tax rate  T_c  (%)",       0.0,  50.0,  25.0,  0.5)

sb.markdown("---")
sb.subheader("Tax-shield utilisation (red curve)")

alpha = sb.slider("α   (speed utilisation falls)", 0.0, 5.0, 1.0, 0.1)
lam   = sb.slider("λ   (curvature exponent)",      1.0, 4.0, 1.0, 0.1)

sb.markdown("---")
sb.subheader("Financial-distress costs (difference red → black)")

fd_total = sb.slider("Total distress cost at 100 % debt  (€ m)", 0.0, 150.0, 40.0, 1.0)
gamma    = sb.slider("γ   (curvature exponent)",             1.0, 4.0, 1.0, 0.1,
                     help="1 = linear, >1 = more convex")

# ───────────────────────── calculations ──────────────────────────── #
d_pct  = np.arange(0, 101)            # 0 … 100 %
d_frac = d_pct / 100                  # 0 … 1

# PV{tax shield}: rises like T_c·D then decays (inverse-U)
pv_tax = (T_c/100) * V_U * d_frac * np.exp(-alpha * d_frac**lam)
V_TS   = V_U + pv_tax                 # red curve

# PV{distress}: user-set total at 100 % debt, curvature γ
pv_fd  = fd_total * d_frac**gamma
V_L    = V_TS - pv_fd                 # black curve

# optimum
opt_idx   = int(np.argmax(V_L))
opt_d_pct = d_pct[opt_idx]
opt_value = V_L[opt_idx]

# table
df = pd.DataFrame({
    "Debt %":             d_pct,
    "PV Tax Shield":      pv_tax,
    "PV Distress Cost":   pv_fd,
    "V (Tax only)":       V_TS,
    "V (Levered)":        V_L,
})

# ────────────────────────── plot ───────────────────────────── #
st.subheader("Value components vs. leverage")

fig = go.Figure()

# black – levered value after distress
fig.add_trace(go.Scatter(
    x=d_pct, y=V_L, mode="lines", name="Vₗ  (after distress)",
    line=dict(color="black", width=3)
))

# red – value with tax shield only
fig.add_trace(go.Scatter(
    x=d_pct, y=V_TS, mode="lines", name="Vₜₐₓ  (with corporate tax)",
    line=dict(color="#d62728", width=2)
))

# horizontal V_U
fig.add_hline(
    y=V_U, line=dict(color="grey", dash="dash"),
    annotation=dict(text="Vᵤ (unlevered)", showarrow=False, yshift=10)
)

# vertical optimum
fig.add_vline(
    x=opt_d_pct, line=dict(color="grey", dash="dash"),
    annotation=dict(text=f"Optimal {opt_d_pct:.0f}% debt",
                    textangle=-90, yshift=10, showarrow=False)
)

fig.update_layout(
    xaxis_title="Debt as % of Assets (≈ D / E)",
    yaxis_title="Firm value (€ m)",
    height=620,
    hovermode="x unified",
    legend=dict(orientation="h", y=-0.25, x=0.5, xanchor="center"),
    margin=dict(l=80, r=80, t=30, b=40),
    font=dict(size=16),
)

st.plotly_chart(fig, use_container_width=True)

st.markdown(
    f"**Optimal capital structure:** {opt_d_pct:.0f} % debt  →  "
    f"levered value **€{opt_value:,.1f} m**"
)

with st.expander("Data table"):
    st.dataframe(
        df.style.format("{:.2f}"),
        use_container_width=True, height=280
    )

st.markdown(
    '<div style="text-align:center; font-size:0.85rem; padding-top:1rem;">'
    'Play with the sliders to see how tax benefits and distress costs shift the optimum!</div>',
    unsafe_allow_html=True,
)
