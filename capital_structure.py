import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.io as pio
import os
import subprocess
import sys

# ─────────────────  PAGE CONFIG  ───────────────── #
st.set_page_config(page_title="Optimal Capital Structure",
                   page_icon="📐", layout="wide")
st.markdown('<h1 style="text-align:center; color:#1E3A8A;">📐 Optimal Capital Structure</h1>',
            unsafe_allow_html=True)

def setup_chrome_for_kaleido():
    """Setup Chrome/Chromium for kaleido with multiple fallback methods"""
    
    # Try to find Chrome/Chromium in common locations
    possible_chrome_paths = [
        '/usr/bin/chromium-browser',
        '/usr/bin/chromium',
        '/usr/bin/google-chrome',
        '/usr/bin/google-chrome-stable',
        '/opt/google/chrome/chrome',
        '/snap/bin/chromium'
    ]
    
    chrome_path = None
    for path in possible_chrome_paths:
        if os.path.exists(path):
            chrome_path = path
            break
    
    if chrome_path:
        # Set environment variables
        os.environ['CHROME_BIN'] = chrome_path
        os.environ['GOOGLE_CHROME_BIN'] = chrome_path
        os.environ['CHROMIUM_BIN'] = chrome_path
        
        # Configure kaleido
        try:
            pio.kaleido.scope.chromium_args = [
                '--no-sandbox',
                '--disable-dev-shm-usage',
                '--disable-gpu',
                '--disable-software-rasterizer',
                '--disable-background-timer-throttling',
                '--disable-backgrounding-occluded-windows',
                '--disable-renderer-backgrounding',
                '--disable-features=TranslateUI',
                '--disable-ipc-flooding-protection',
                '--virtual-time-budget=5000',
                '--run-all-compositor-stages-before-draw',
                '--disable-checker-imaging'
            ]
            return True, f"Chrome found at: {chrome_path}"
        except Exception as e:
            return False, f"Chrome found but configuration failed: {str(e)}"
    
    return False, "Chrome/Chromium not found in system"

def test_svg_generation():
    """Test if SVG generation works"""
    try:
        test_fig = go.Figure(go.Scatter(x=[1,2,3], y=[1,2,3]))
        svg_bytes = test_fig.to_image(format="svg", width=200, height=200)
        return True, "SVG generation working!"
    except Exception as e:
        return False, str(e)

# 🔍 ENHANCED DIAGNOSTIC SECTION
with st.expander("🔍 Diagnostic Information", expanded=False):
    st.write("**Kaleido Status:**")
    
    try:
        import kaleido
        st.write("✅ Kaleido installed")
        
        # Try to get version, but don't fail if it doesn't exist
        try:
            st.write(f"Version: {kaleido.__version__}")
        except AttributeError:
            st.write("Version: (version info not available)")
        
        # Setup Chrome
        chrome_success, chrome_msg = setup_chrome_for_kaleido()
        if chrome_success:
            st.write(f"✅ {chrome_msg}")
        else:
            st.write(f"❌ {chrome_msg}")
        
        # Test SVG generation
        svg_success, svg_msg = test_svg_generation()
        if svg_success:
            st.write(f"✅ {svg_msg}")
            st.success("SVG export should work!")
        else:
            st.write(f"❌ SVG test failed: {svg_msg}")
            st.warning("SVG export may not work")
            
    except ImportError:
        st.write("❌ Kaleido not installed")
    except Exception as e:
        st.write(f"❌ Unexpected error: {str(e)}")

# ℹ️  ABOUT PANEL ---------------------------------- #
with st.expander("ℹ️ About this tool", expanded=False):
    st.markdown(
        """
        This tool visualizes the trade-off between the **tax shield of debt** and the expected
        **costs of financial distress**.

        The various lines stand for the following firm values:

        * **Red** – firm value with **tax shield only**  
        * **Black** – firm value with **tax shield** and **financial distress costs**  
        * **Horizontal indigo dashed** – unlevered firm value **V<sub>U</sub>**  
        
        Note that in practice it is not straightforward to estimate a firm's costs of financial distress.
        """,
        unsafe_allow_html=True,
    )

# ─────────── SIDEBAR INPUTS ─────────── #
sb = st.sidebar
sb.header("Core inputs")

V_U = sb.slider("Unlevered firm value  Vᵤ  (€ million)",
                50.0, 500.0, 200.0, 10.0)
T_c = sb.slider("Corporate tax rate  T꜀  (%)",
                0.0, 50.0, 25.0, 0.5)

sb.markdown("---")
FD_total = sb.slider("PV of distress costs at 100 % debt  (€ million)",
                     0.0, 150.0, 40.0, 1.0)

# ─────────── MODEL CONSTANTS ─────────── #
BETA_DECAY  = 2.0
FD_EXPONENT = 2.0
OFFSET      = 7       # ppt left / right for the two arrows
DIST_GAP    = 3       # ppt further right for PV(distress) marker
INDIGO      = "#6366F1"

# ─────────── COMPUTATIONS ─────────── #
d_pct  = np.arange(0, 101)
d_frac = d_pct / 100

pv_tax = (T_c/100) * V_U * d_frac * np.exp(-BETA_DECAY * d_frac)
V_tax  = V_U + pv_tax

pv_fd  = FD_total * d_frac**FD_EXPONENT
V_L    = V_tax - pv_fd

opt_idx   = np.argmax(V_L)
opt_d_pct = int(d_pct[opt_idx])

x_left   = max(0,  opt_d_pct - OFFSET)
x_right  = min(100, opt_d_pct + OFFSET)
x_dist   = min(100, x_right + DIST_GAP)

PVTS_top = V_tax[x_left]
VL_top   = V_L[x_right]
VDist_bot, VDist_top = V_L[x_dist], V_tax[x_dist]

# ─────────── PLOT ─────────── #
fig = go.Figure()

fig.add_trace(go.Scatter(x=d_pct, y=V_L,
                         mode="lines", name="V<sub>L</sub> (levered)",
                         line=dict(color="black", width=3)))
fig.add_trace(go.Scatter(x=d_pct, y=V_tax,
                         mode="lines", name="V (tax benefit only)",
                         line=dict(color="#d62728", width=2)))

fig.add_hline(y=V_U, line=dict(color=INDIGO, dash="dash"),
              annotation=dict(text="V<sub>U</sub> (unlevered)",
                              showarrow=False, yshift=-18,
                              font=dict(size=12, color=INDIGO)))

fig.add_vline(x=opt_d_pct, line=dict(color="grey", dash="dash"),
              annotation=dict(text=f"Optimal debt",
                              textangle=-90, showarrow=False, yshift=10))

# PV (tax shield) arrow
fig.add_shape(type="line", x0=x_left, x1=x_left,
              y0=V_U, y1=PVTS_top,
              line=dict(color="#d62728", dash="dot"))
fig.add_annotation(x=x_left - 1.5, y=(V_U + PVTS_top)/2,
                   text="PV&nbsp;(tax&nbsp;shield)",
                   showarrow=False, font=dict(size=12, color="#d62728"),
                   align="right")

# Value of levered firm arrow
fig.add_shape(type="line", x0=x_right, x1=x_right,
              y0=V_U, y1=VL_top,
              line=dict(color="black", dash="dot"))
fig.add_annotation(x=x_right + 1.5, y=(V_U + VL_top)/2,
                   text="Value&nbsp;of&nbsp;levered&nbsp;firm",
                   showarrow=False, font=dict(size=12, color="black"),
                   align="left")

# PV(distress) marker
fig.add_shape(type="line", x0=x_dist, x1=x_dist,
              y0=VDist_bot, y1=VDist_top,
              line=dict(color="grey", dash="dot"))
fig.add_annotation(x=x_dist + 1.5, y=(VDist_bot + VDist_top)/2,
                   text="PV&nbsp;of&nbsp;distress&nbsp;costs",
                   showarrow=False, font=dict(size=12, color="grey"),
                   align="left")

fig.update_layout(xaxis_title="Debt/Equity",
                  yaxis_title="Firm value (€ million)",
                  hovermode="x unified",
                  font=dict(size=16),
                  height=620,
                  legend=dict(orientation="h", y=-0.25, x=0.5,
                              xanchor="center"),
                  margin=dict(l=80, r=80, t=30, b=40))

st.plotly_chart(fig, use_container_width=True)

# ───────────  SMART DOWNLOAD SECTION  ─────────── #
st.subheader("📥 Export Options")

# Setup Chrome before attempting exports
chrome_setup, _ = setup_chrome_for_kaleido()

col1, col2, col3 = st.columns(3)

with col1:
    # SVG with smart error handling
    if chrome_setup:
        try:
            svg_bytes = fig.to_image(format="svg", width=1200, height=620, scale=2)
            st.download_button(
                "⬇️ Download SVG",
                svg_bytes,
                file_name="capital_structure.svg",
                mime="image/svg+xml",
                help="High-quality SVG vector graphics"
            )
        except Exception as e:
            st.error(f"SVG export failed: {str(e)}")
            st.info("💡 Try refreshing the page or use PNG export instead.")
    else:
        st.info("💡 SVG export requires Chrome browser in the system")

with col2:
    # PNG (more reliable fallback)
    try:
        png_bytes = fig.to_image(format="png", width=1200, height=620, scale=2)
        st.download_button(
            "⬇️ Download PNG",
            png_bytes,
            file_name="capital_structure.png",
            mime="image/png",
            help="High-quality PNG image"
        )
    except Exception as e:
        st.info("💡 Use the camera icon in the chart toolbar above for PNG download.")

with col3:
    # HTML (always works)
    html_string = fig.to_html(include_plotlyjs='cdn')
    st.download_button(
        "⬇️ Download HTML",
        html_string,
        file_name="capital_structure.html",
        mime="text/html",
        help="Interactive HTML file"
    )

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
    'Optimal Capital Structure Visualiser&nbsp;|&nbsp;Developed by Prof.&nbsp;Marc&nbsp;Goergen&nbsp;with&nbsp;the&nbsp;help&nbsp;of&nbsp;ChatGPT'
    '</div>',
    unsafe_allow_html=True,
)
