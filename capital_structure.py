import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go

# ─────────────────────── page setup ──────────────────────── #
st.set_page_config(
    page_title="Optimal Capital Structure",
    page_icon="📐",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    '<h1 style="text-align:center;">Optimal Capital Structure</h1>',
    unsafe_allow_html=True,
)

# ──────────────────── model explanation ──────────────────── #
with st.expander("Model & formulas"):
    st.markdown(
        r"""
The app evaluates the firm for every leverage point \(D/A \in [0,1]\).

### Components  

| symbol | formula | description |
|--------|---------|-------------|
| \(V_U\) | *(slider)* | Value of unlevered firm |
| PV(TS) | \(T_c \times D\) | Present value of corporate-tax shield |
| PV(FD) | \(k \, (D/A)^{\gamma}\,A\) | Present value of expected financial-distress costs |

### Curves  

\[
\begin{aligned}
\text{Red: } V_{\text{tax}}(D) &= V_U + \text{PV(TS)} \\[4pt]
\text{Black: } V_L(D) &= V_U + \text{PV(TS)} - \text{PV(FD)}
\end{aligned}
\]

The **gap** between red and black is exactly PV(FD).  
The optimal capital structure maximises \(V_L\).
        """,
        unsafe_allow_html=True,
    )

# ───────────────────────── inputs ────────────────────────── #
left, right = st.columns([1, 2], gap="large")

with left:
    st.subheader("Assumptions")

    V_U = st.slider("Unlevered firm value  V₍U₎  (€ m)", 50.0, 500.0, 200.0, 10.0)
    tax_rate = st.slider("Corporate tax rate  T_c  (%)", 0.0, 50.0, 25.0, 0.5)

    st.markdown("### Financial-distress cost function")
    k_scale = st.slider("Scale  k", 0.00, 1.00, 0.15, 0.01)
    gamma   = st.slider("Convexity  γ", 1.0, 4.0, 2.0, 0.1)

# ───────────── compute values across leverage range ───────── #
debt_pct = np.arange(0, 101)                        # 0 … 100 %
debt_val = V_U * debt_pct / 100                     # assumes Assets ≈ V_U

pv_ts  = (tax_rate / 100) * debt_val
pv_fd  = k_scale * (debt_val / V_U) ** gamma * V_U

V_tax  = V_U + pv_ts                  # red
V_lev  = V_tax - pv_fd                # black

opt_idx   = np.argmax(V_lev)
opt_d_pct = debt_pct[opt_idx]
opt_value = V_lev[opt_idx]

df = pd.DataFrame({
    "Debt %": debt_pct,
    "V_unlevered": V_U,
    "V_tax": V_tax,
    "V_levered": V_lev,
    "PV_tax_shield": pv_ts,
    "PV_distress": pv_fd,
})

# ─────────────────────────── plot ────────────────────────── #
with right:
    st.subheader("Value vs. leverage")

    fig = go.Figure()

    # black – levered value
    fig.add_trace(
        go.Scatter(
            x=debt_pct, y=V_lev,
            mode="lines", name="Firm value incl. distress (black)",
            line=dict(color="black", width=3),
            hovertemplate="Debt % %{x}<br>V_L €%{y:.1f} m<extra></extra>",
        )
    )

    # red – with tax only
    fig.add_trace(
        go.Scatter(
            x=debt_pct, y=V_tax,
            mode="lines", name="Firm value with tax shield only (red)",
            line=dict(color="#dc2626", width=2),
            hovertemplate="Debt % %{x}<br>V_tax €%{y:.1f} m<extra></extra>",
        )
    )

    # fill between red and black = PV(FD)
    fig.add_trace(
        go.Scatter(
            x=np.concatenate([debt_pct, debt_pct[::-1]]),
            y=np.concatenate([V_tax, V_lev[::-1]]),
            fill="toself",
            fillcolor="rgba(220,38,38,0.15)",  # translucent red
            line=dict(width=0),
            hoverinfo="skip",
            showlegend=False,
        )
    )

    # horizontal V_U
    fig.add_hline(
        y=V_U,
        line=dict(dash="dash", color="grey"),
        annotation=dict(text="V_U", showarrow=False, yshift=10),
    )

    # optimal vertical
    fig.add_vline(
        x=opt_d_pct,
        line=dict(dash="dash", color="grey"),
        annotation=dict(
            text=f"Optimal {opt_d_pct:.0f} % debt",
            textangle=-90,
            yshift=10,
            showarrow=False,
        ),
    )

    fig.update_layout(
        xaxis_title="Debt as % of Assets  (≈ D / E)",
        yaxis_title="Firm value  (€ million)",
        hovermode="x unified",
        legend=dict(orientation="h", y=-0.25, x=0.5, xanchor="center"),
        height=620,
        margin=dict(l=80, r=80, t=30, b=40),
    )

    st.plotly_chart(fig, use_container_width=True)

    st.markdown(
        f"**Optimal capital structure:** **{opt_d_pct:.0f} % debt**, "
        f"giving a levered value of **€ {opt_value:,.1f} m**"
    )

    with st.expander("Data"):
        st.dataframe(
            df.style.format("{:.2f}"),
            use_container_width=True,
            height=300,
        )

# ───────────────────────── footer ────────────────────────── #
st.markdown(
    '<div style="text-align:center; font-size:0.9rem; padding-top:1rem;">'
    'Capital-Structure model • red minus black = PV(distress costs)'
    '</div>',
    unsafe_allow_html=True,
)
