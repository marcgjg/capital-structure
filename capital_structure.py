import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go

# ──────────────────────────── CONFIG ───────────────────────────── #

st.set_page_config(
    page_title="Optimal Capital Structure • Tax Shield vs. Distress Costs",
    page_icon="📐",
    layout="wide",
)

st.markdown(
    '<h1 style="text-align:center;">Optimal Capital Structure</h1>',
    unsafe_allow_html=True,
)

with st.expander("Model notes"):
    st.markdown(
        """
        *Value of levered firm*  

        \\[
        V_L(D) \\,=\\, V_U \\, + \\, T_c \\times D
                   \\, - \\, k \\; \\bigl(\\tfrac{D}{A}\\bigr)^{\\gamma} \\; A
        \\]

        where  

        • **D** = Debt value (we vary it from 0 → 100 % of assets)  
        • **A** = Total assets = *V<sub>U</sub>* in this simple set-up  
        • **T<sub>c</sub>** = corporate tax rate (slider)  
        • **k**, **γ** = scale & convexity of financial-distress costs (sliders)

        The peak of the black curve is the **optimal capital structure**.
        """,
        unsafe_allow_html=True,
    )

# ──────────────────────────── INPUTS ───────────────────────────── #

controls, plot_col = st.columns([1, 2], gap="large")

with controls:
    st.subheader("Key assumptions")

    V_U = st.slider("Unlevered firm value  (V₍U₎) € million", 50.0, 500.0, 200.0, 10.0)
    tax_rate = st.slider("Corporate tax rate  T_c  (%)", 0.0, 50.0, 25.0, 0.5)

    st.markdown("### Financial-distress cost function")
    k_scale = st.slider("Scale parameter  k", 0.0, 1.0, 0.15, 0.01)
    gamma   = st.slider("Convexity  γ", 1.0, 4.0, 2.0, 0.1)

# ───────────────────── COMPUTE CURVES ACROSS DEBT RANGE ───────────── #

debt_pct = np.arange(0, 101)                 # 0 … 100 %
debt_val = V_U * debt_pct / 100              # € million (assets = V_U)

pv_tax   = (tax_rate / 100) * debt_val
pv_fd    = k_scale * (debt_val / V_U) ** gamma * V_U
V_lever  = V_U + pv_tax - pv_fd

opt_idx  = np.argmax(V_lever)                # index of max firm value
opt_d_pct = debt_pct[opt_idx]
opt_value = V_lever[opt_idx]

df = pd.DataFrame({
    "Debt %": debt_pct,
    "PV Tax Shield": pv_tax,
    "PV Distress Cost": pv_fd,
    "Levered Firm Value": V_lever,
})

# ──────────────────────────── PLOTS ───────────────────────────── #

with plot_col:
    st.subheader("Value components vs. leverage")

    fig = go.Figure()

    # black: levered firm value
    fig.add_trace(
        go.Scatter(
            x=debt_pct,
            y=V_lever,
            mode="lines",
            name="V (L)  – Levered value",
            line=dict(color="black", width=3),
        )
    )

    # blue: PV tax shield
    fig.add_trace(
        go.Scatter(
            x=debt_pct,
            y=pv_tax,
            mode="lines",
            name="PV (Tax shield)",
            line=dict(color="#2563eb", width=2),
        )
    )

    # red: PV distress costs
    fig.add_trace(
        go.Scatter(
            x=debt_pct,
            y=pv_fd,
            mode="lines",
            name="PV (Financial-distress costs)",
            line=dict(color="#dc2626", width=2),
        )
    )

    # baseline V_U
    fig.add_hline(
        y=V_U,
        line=dict(dash="dash", color="grey"),
        annotation=dict(text="V (U)", showarrow=False, yshift=10),
    )

    # optimal vertical
    fig.add_vline(
        x=opt_d_pct,
        line=dict(dash="dash", color="grey"),
        annotation=dict(
            text=f"Optimal {opt_d_pct:.0f}% debt",
            showarrow=False,
            xshift=0,
            yshift=10,
            textangle=-90,
        ),
    )

    fig.update_layout(
        xaxis_title="Debt as % of Assets",
        yaxis_title="€ million",
        hovermode="x unified",
        height=620,
        legend=dict(orientation="h", y=-0.25, x=0.5, xanchor="center"),
        margin=dict(l=80, r=80, t=30, b=40),
    )

    st.plotly_chart(fig, use_container_width=True)

    st.markdown(f"**Optimal debt ratio:** **{opt_d_pct:.0f} %**, giving a levered value of **€ {opt_value:,.1f} million**")

    with st.expander("Data"):
        st.dataframe(
            df.style.format("{:.2f}"),
            use_container_width=True,
            height=300,
        )

# ──────────────────────────── FOOTER ───────────────────────────── #

st.markdown(
    '<div style="text-align:center; padding-top:1.2rem; font-size:0.9rem;">'
    'Prototype – tweak the functional form or parameters as you like!'
    '</div>',
    unsafe_allow_html=True,
)
