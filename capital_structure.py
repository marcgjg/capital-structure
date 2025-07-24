import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.io as pio
import os

# ─────────────────  PAGE CONFIG  ───────────────── #
st.set_page_config(page_title="Optimal Capital Structure",
                   page_icon="📐", layout="wide")
st.markdown('<h1 style="text-align:center; color:#1E3A8A;">📐 Optimal Capital Structure</h1>',
            unsafe_allow_html=True)

def create_production_svg(d_pct, V_L, V_tax, V_U, opt_d_pct, VL_top, T_c, FD_total):
    """Create high-quality SVG manually - publication ready"""
    
    # Chart dimensions and styling
    width, height = 1200, 800
    margin = {"top": 80, "right": 120, "bottom": 100, "left": 120}
    chart_width = width - margin["left"] - margin["right"]
    chart_height = height - margin["top"] - margin["bottom"]
    
    # Data scaling
    x_min, x_max = 0, 100
    y_min = min(min(V_L), V_U) * 0.9
    y_max = max(max(V_tax), V_U) * 1.1
    
    def scale_x(x): return margin["left"] + (x - x_min) * chart_width / (x_max - x_min)
    def scale_y(y): return height - margin["bottom"] - (y - y_min) * chart_height / (y_max - y_min)
    
    # Create smooth paths
    def create_smooth_path(x_data, y_data):
        points = [(scale_x(x), scale_y(y)) for x, y in zip(x_data, y_data)]
        path = f"M {points[0][0]},{points[0][1]}"
        for i in range(1, len(points)):
            path += f" L {points[i][0]},{points[i][1]}"
        return path
    
    vl_path = create_smooth_path(d_pct, V_L)
    vtax_path = create_smooth_path(d_pct, V_tax)
    
    # Grid lines
    x_grid_lines = ""
    for x in range(0, 101, 20):
        x_pos = scale_x(x)
        x_grid_lines += f'<line x1="{x_pos}" y1="{margin["top"]}" x2="{x_pos}" y2="{height - margin["bottom"]}" class="grid"/>\n'
    
    y_ticks = np.linspace(y_min, y_max, 6)
    y_grid_lines = ""
    y_labels = ""
    for y in y_ticks:
        y_pos = scale_y(y)
        y_grid_lines += f'<line x1="{margin["left"]}" y1="{y_pos}" x2="{width - margin["right"]}" y2="{y_pos}" class="grid"/>\n'
        y_labels += f'<text x="{margin["left"] - 15}" y="{y_pos + 5}" class="axis-label">{y:.0f}</text>\n'
    
    # X-axis labels
    x_labels = ""
    for x in range(0, 101, 20):
        x_pos = scale_x(x)
        x_labels += f'<text x="{x_pos}" y="{height - margin["bottom"] + 25}" class="axis-label">{x}%</text>\n'
    
    # Key points
    opt_x, opt_y = scale_x(opt_d_pct), scale_y(VL_top)
    vu_y = scale_y(V_U)
    
    # Annotations
    x_left = max(0, opt_d_pct - 7)
    x_right = min(100, opt_d_pct + 7)
    x_dist = min(100, x_right + 3)
    
    pvts_y = scale_y(V_U + (T_c/100) * V_U * (x_left/100) * np.exp(-2.0 * (x_left/100)))
    vl_annotation_y = scale_y(V_L[x_right])
    
    # SVG content
    svg_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg">
    <defs>
        <style>
            .line-vl {{ stroke: #000000; stroke-width: 3; fill: none; stroke-linecap: round; stroke-linejoin: round; }}
            .line-vtax {{ stroke: #d62728; stroke-width: 2.5; fill: none; stroke-linecap: round; stroke-linejoin: round; }}
            .line-vu {{ stroke: #6366F1; stroke-width: 2; stroke-dasharray: 8,5; fill: none; }}
            .line-opt {{ stroke: #666666; stroke-width: 1.5; stroke-dasharray: 5,5; fill: none; }}
            .grid {{ stroke: #e5e5e5; stroke-width: 0.5; }}
            .axis {{ stroke: #333333; stroke-width: 1.5; }}
            .axis-label {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; font-size: 13px; fill: #444; text-anchor: middle; }}
            .axis-title {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; font-size: 16px; fill: #333; text-anchor: middle; font-weight: 500; }}
            .title {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; font-size: 24px; font-weight: bold; fill: #1E3A8A; text-anchor: middle; }}
            .legend-text {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; font-size: 14px; fill: #333; }}
            .annotation {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; font-size: 12px; fill: #666; text-anchor: middle; }}
            .optimal-point {{ fill: #ff4444; stroke: white; stroke-width: 2; }}
        </style>
    </defs>
    
    <!-- Background -->
    <rect width="{width}" height="{height}" fill="white"/>
    
    <!-- Title -->
    <text x="{width/2}" y="40" class="title">📐 Optimal Capital Structure</text>
    
    <!-- Grid -->
    {x_grid_lines}
    {y_grid_lines}
    
    <!-- Chart border -->
    <rect x="{margin['left']}" y="{margin['top']}" width="{chart_width}" height="{chart_height}" 
          fill="none" stroke="#ddd" stroke-width="1"/>
    
    <!-- Axes -->
    <line x1="{margin['left']}" y1="{height - margin['bottom']}" x2="{width - margin['right']}" y2="{height - margin['bottom']}" class="axis"/>
    <line x1="{margin['left']}" y1="{margin['top']}" x2="{margin['left']}" y2="{height - margin['bottom']}" class="axis"/>
    
    <!-- Data lines -->
    <path d="{vtax_path}" class="line-vtax"/>
    <path d="{vl_path}" class="line-vl"/>
    
    <!-- V_U horizontal line -->
    <line x1="{margin['left']}" y1="{vu_y}" x2="{width - margin['right']}" y2="{vu_y}" class="line-vu"/>
    
    <!-- Optimal debt vertical line -->
    <line x1="{opt_x}" y1="{margin['top']}" x2="{opt_x}" y2="{height - margin['bottom']}" class="line-opt"/>
    
    <!-- Optimal point -->
    <circle cx="{opt_x}" cy="{opt_y}" r="5" class="optimal-point"/>
    
    <!-- Axis labels -->
    {x_labels}
    {y_labels}
    
    <!-- Axis titles -->
    <text x="{width/2}" y="{height - 25}" class="axis-title">Debt/Equity (%)</text>
    <text x="25" y="{height/2}" class="axis-title" transform="rotate(-90 25 {height/2})">Firm value (€ million)</text>
    
    <!-- Legend -->
    <g transform="translate({width - margin['right'] + 20}, {margin['top'] + 40})">
        <rect x="-15" y="-15" width="140" height="120" fill="white" stroke="#ddd" stroke-width="1" rx="5"/>
        <text x="0" y="0" class="legend-text" style="font-weight: 600;">Legend</text>
        <line x1="0" y1="20" x2="25" y2="20" class="line-vl"/>
        <text x="30" y="25" class="legend-text">V<tspan baseline-shift="sub" font-size="11">L</tspan> (levered)</text>
        <line x1="0" y1="40" x2="25" y2="40" class="line-vtax"/>
        <text x="30" y="45" class="legend-text">V (tax benefit only)</text>
        <line x1="0" y1="60" x2="25" y2="60" class="line-vu"/>
        <text x="30" y="65" class="legend-text">V<tspan baseline-shift="sub" font-size="11">U</tspan> (unlevered)</text>
        <line x1="0" y1="80" x2="25" y2="80" class="line-opt"/>
        <text x="30" y="85" class="legend-text">Optimal debt</text>
    </g>
    
    <!-- Annotations -->
    <text x="{opt_x}" y="{margin['top'] - 10}" class="annotation">Optimal: {opt_d_pct}% debt</text>
    <text x="{opt_x + 60}" y="{opt_y - 15}" class="annotation">€{VL_top:,.1f}M</text>
    
    <!-- V_U label -->
    <text x="{width - margin['right'] - 50}" y="{vu_y - 8}" class="annotation">V<tspan baseline-shift="sub" font-size="10">U</tspan></text>
    
    <!-- Parameter info -->
    <g transform="translate(30, {height - 60})">
        <text x="0" y="0" class="annotation" style="font-weight: 600;">Parameters:</text>
        <text x="0" y="15" class="annotation">Tax rate: {T_c}%</text>
        <text x="0" y="30" class="annotation">V<tspan baseline-shift="sub" font-size="10">U</tspan>: €{V_U:,.0f}M</text>
        <text x="120" y="15" class="annotation">Max distress cost: €{FD_total:,.0f}M</text>
    </g>
    
    <!-- Footer -->
    <text x="{width/2}" y="{height - 8}" class="annotation">
        Developed by Prof. Marc Goergen with the help of ChatGPT
    </text>
</svg>'''
    
    return svg_content.encode()

def create_editable_svg(d_pct, V_L, V_tax, V_U, opt_d_pct, VL_top, T_c, FD_total):
    """Create fully editable SVG with proper grouping and no clipping"""
    
    # Increased dimensions and margins to prevent clipping
    width, height = 1400, 900
    margin = {"top": 100, "right": 200, "bottom": 120, "left": 150}
    chart_width = width - margin["left"] - margin["right"]
    chart_height = height - margin["top"] - margin["bottom"]
    
    # Data scaling with padding to prevent clipping
    x_min, x_max = 0, 100
    y_min = min(min(V_L), V_U) * 0.85  # More padding
    y_max = max(max(V_tax), V_U) * 1.15  # More padding
    
    def scale_x(x): return margin["left"] + (x - x_min) * chart_width / (x_max - x_min)
    def scale_y(y): return height - margin["bottom"] - (y - y_min) * chart_height / (y_max - y_min)
    
    # Create individual data points for better editability
    def create_data_points(x_data, y_data, group_name, color, stroke_width):
        points_list = []
        path_data = []
        
        for i, (x, y) in enumerate(zip(x_data, y_data)):
            x_pos, y_pos = scale_x(x), scale_y(y)
            points_list.append(f'<circle cx="{x_pos}" cy="{y_pos}" r="1" fill="{color}" class="{group_name}-point" id="{group_name}-point-{i}"/>')
            if i == 0:
                path_data.append(f"M {x_pos},{y_pos}")
            else:
                path_data.append(f"L {x_pos},{y_pos}")
        
        path_string = " ".join(path_data)
        
        return f'''
    <g id="{group_name}-group" class="{group_name}">
        <path d="{path_string}" stroke="{color}" stroke-width="{stroke_width}" fill="none" 
              stroke-linecap="round" stroke-linejoin="round" id="{group_name}-line"/>
        <!-- Data points for editing -->
        {chr(10).join(points_list)}
    </g>'''
    
    # Generate line groups
    vl_group = create_data_points(d_pct, V_L, "levered-firm", "#000000", 3)
    vtax_group = create_data_points(d_pct, V_tax, "tax-benefit", "#d62728", 2.5)
    
    # Key coordinates
    opt_x, opt_y = scale_x(opt_d_pct), scale_y(VL_top)
    vu_y = scale_y(V_U)
    
    # Grid generation
    x_grid_lines = []
    x_labels = []
    for x in range(0, 101, 10):  # More grid lines
        x_pos = scale_x(x)
        x_grid_lines.append(f'<line x1="{x_pos}" y1="{margin["top"]}" x2="{x_pos}" y2="{height - margin["bottom"]}" class="grid-x" id="grid-x-{x}"/>')
        if x % 20 == 0:  # Labels every 20%
            x_labels.append(f'<text x="{x_pos}" y="{height - margin["bottom"] + 25}" class="axis-label" id="x-label-{x}">{x}%</text>')
    
    y_ticks = np.linspace(y_min, y_max, 8)  # More ticks
    y_grid_lines = []
    y_labels = []
    for i, y in enumerate(y_ticks):
        y_pos = scale_y(y)
        y_grid_lines.append(f'<line x1="{margin["left"]}" y1="{y_pos}" x2="{width - margin["right"]}" y2="{y_pos}" class="grid-y" id="grid-y-{i}"/>')
        y_labels.append(f'<text x="{margin["left"] - 15}" y="{y_pos + 5}" class="axis-label" id="y-label-{i}">{y:.0f}</text>')
    
    # Create CSS as a separate string to avoid f-string conflicts
    css_styles = """
            /* Chart Lines */
            .levered-firm { stroke: #000000; stroke-width: 3; fill: none; }
            .tax-benefit { stroke: #d62728; stroke-width: 2.5; fill: none; }
            .unlevered-line { stroke: #6366F1; stroke-width: 2; stroke-dasharray: 8,5; fill: none; }
            .optimal-line { stroke: #666666; stroke-width: 1.5; stroke-dasharray: 5,5; fill: none; }
            
            /* Grid and Axes */
            .grid-x, .grid-y { stroke: #e5e5e5; stroke-width: 0.5; }
            .axis { stroke: #333333; stroke-width: 1.5; }
            
            /* Text Styles */
            .axis-label { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; font-size: 13px; fill: #444444; text-anchor: middle; }
            .axis-title { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; font-size: 16px; fill: #333333; text-anchor: middle; font-weight: 500; }
            .title { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; font-size: 24px; font-weight: bold; fill: #1E3A8A; text-anchor: middle; }
            .legend-text { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; font-size: 14px; fill: #333333; }
            .annotation { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; font-size: 12px; fill: #666666; }
            
            /* Interactive Elements */
            .optimal-point { fill: #ff4444; stroke: white; stroke-width: 2; }
            .levered-firm-point, .tax-benefit-point { opacity: 0; } /* Hidden but selectable */
            .levered-firm-point:hover, .tax-benefit-point:hover { opacity: 1; }
    """
    
    # SVG with proper structure for editing
    svg_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg width="{width}" height="{height}" viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg">
    <defs>
        <style>{css_styles}</style>
    </defs>
    
    <!-- Background -->
    <rect width="{width}" height="{height}" fill="white" id="background"/>
    
    <!-- Title Group -->
    <g id="title-group">
        <text x="{width/2}" y="50" class="title" id="main-title">📐 Optimal Capital Structure</text>
    </g>
    
    <!-- Grid Group -->
    <g id="grid-group">
        {chr(10).join(x_grid_lines)}
        {chr(10).join(y_grid_lines)}
    </g>
    
    <!-- Chart Border -->
    <g id="chart-border-group">
        <rect x="{margin['left']}" y="{margin['top']}" width="{chart_width}" height="{chart_height}" 
              fill="none" stroke="#dddddd" stroke-width="1" id="chart-border"/>
    </g>
    
    <!-- Axes Group -->
    <g id="axes-group">
        <line x1="{margin['left']}" y1="{height - margin['bottom']}" x2="{width - margin['right']}" y2="{height - margin['bottom']}" class="axis" id="x-axis"/>
        <line x1="{margin['left']}" y1="{margin['top']}" x2="{margin['left']}" y2="{height - margin['bottom']}" class="axis" id="y-axis"/>
    </g>
    
    <!-- Reference Lines Group -->
    <g id="reference-lines-group">
        <!-- V_U horizontal line -->
        <line x1="{margin['left']}" y1="{vu_y}" x2="{width - margin['right']}" y2="{vu_y}" 
              class="unlevered-line" id="unlevered-line"/>
        <!-- Optimal debt vertical line -->
        <line x1="{opt_x}" y1="{margin['top']}" x2="{opt_x}" y2="{height - margin['bottom']}" 
              class="optimal-line" id="optimal-debt-line"/>
    </g>
    
    <!-- Data Lines Group -->
    <g id="data-lines-group">
        {vtax_group}
        {vl_group}
    </g>
    
    <!-- Optimal Point Group -->
    <g id="optimal-point-group">
        <circle cx="{opt_x}" cy="{opt_y}" r="5" class="optimal-point" id="optimal-point"/>
    </g>
    
    <!-- Labels Group -->
    <g id="labels-group">
        <!-- X-axis labels -->
        <g id="x-labels-group">
            {chr(10).join(x_labels)}
        </g>
        <!-- Y-axis labels -->  
        <g id="y-labels-group">
            {chr(10).join(y_labels)}
        </g>
    </g>
    
    <!-- Axis Titles Group -->
    <g id="axis-titles-group">
        <text x="{width/2}" y="{height - 30}" class="axis-title" id="x-axis-title">Debt/Equity (%)</text>
        <text x="30" y="{height/2}" class="axis-title" id="y-axis-title" transform="rotate(-90 30 {height/2})">Firm value (€ million)</text>
    </g>
    
    <!-- Legend Group -->
    <g id="legend-group" transform="translate({width - margin['right'] + 30}, {margin['top'] + 50})">
        <rect x="-20" y="-20" width="160" height="140" fill="white" stroke="#dddddd" stroke-width="1" rx="5" id="legend-background"/>
        <text x="0" y="0" class="legend-text" id="legend-title" style="font-weight: 600;">Legend</text>
        
        <g id="legend-levered">
            <line x1="0" y1="25" x2="30" y2="25" class="levered-firm" id="legend-levered-line"/>
            <text x="35" y="30" class="legend-text" id="legend-levered-text">V<tspan baseline-shift="sub" font-size="11">L</tspan> (levered)</text>
        </g>
        
        <g id="legend-tax">
            <line x1="0" y1="50" x2="30" y2="50" class="tax-benefit" id="legend-tax-line"/>
            <text x="35" y="55" class="legend-text" id="legend-tax-text">V (tax benefit only)</text>
        </g>
        
        <g id="legend-unlevered">
            <line x1="0" y1="75" x2="30" y2="75" class="unlevered-line" id="legend-unlevered-line"/>
            <text x="35" y="80" class="legend-text" id="legend-unlevered-text">V<tspan baseline-shift="sub" font-size="11">U</tspan> (unlevered)</text>
        </g>
        
        <g id="legend-optimal">
            <line x1="0" y1="100" x2="30" y2="100" class="optimal-line" id="legend-optimal-line"/>
            <text x="35" y="105" class="legend-text" id="legend-optimal-text">Optimal debt</text>
        </g>
    </g>
    
    <!-- Annotations Group -->
    <g id="annotations-group">
        <text x="{opt_x}" y="{margin['top'] - 15}" class="annotation" id="optimal-annotation" text-anchor="middle">
            Optimal: {opt_d_pct}% debt
        </text>
        <text x="{opt_x + 80}" y="{opt_y - 15}" class="annotation" id="value-annotation">
            €{VL_top:,.1f}M
        </text>
        <text x="{width - margin['right'] - 60}" y="{vu_y - 12}" class="annotation" id="vu-annotation">
            V<tspan baseline-shift="sub" font-size="10">U</tspan>
        </text>
    </g>
    
    <!-- Parameters Group -->
    <g id="parameters-group" transform="translate(40, {height - 80})">
        <text x="0" y="0" class="annotation" id="params-title" style="font-weight: 600;">Parameters:</text>
        <text x="0" y="18" class="annotation" id="tax-rate-param">Tax rate: {T_c}%</text>
        <text x="0" y="36" class="annotation" id="vu-param">V<tspan baseline-shift="sub" font-size="10">U</tspan>: €{V_U:,.0f}M</text>
        <text x="150" y="18" class="annotation" id="distress-param">Max distress cost: €{FD_total:,.0f}M</text>
    </g>
    
    <!-- Footer Group -->
    <g id="footer-group">
        <text x="{width/2}" y="{height - 15}" class="annotation" id="footer-text" text-anchor="middle">
            Developed by Prof. Marc Goergen with the help of ChatGPT
        </text>
    </g>
</svg>'''
    
    return svg_content.encode()
    """Create high-quality SVG manually - publication ready"""
    
    # Chart dimensions and styling
    width, height = 1200, 800
    margin = {"top": 80, "right": 120, "bottom": 100, "left": 120}
    chart_width = width - margin["left"] - margin["right"]
    chart_height = height - margin["top"] - margin["bottom"]
    
    # Data scaling
    x_min, x_max = 0, 100
    y_min = min(min(V_L), V_U) * 0.9
    y_max = max(max(V_tax), V_U) * 1.1
    
    def scale_x(x): return margin["left"] + (x - x_min) * chart_width / (x_max - x_min)
    def scale_y(y): return height - margin["bottom"] - (y - y_min) * chart_height / (y_max - y_min)
    
    # Create smooth paths
    def create_smooth_path(x_data, y_data):
        points = [(scale_x(x), scale_y(y)) for x, y in zip(x_data, y_data)]
        path = f"M {points[0][0]},{points[0][1]}"
        for i in range(1, len(points)):
            path += f" L {points[i][0]},{points[i][1]}"
        return path
    
    vl_path = create_smooth_path(d_pct, V_L)
    vtax_path = create_smooth_path(d_pct, V_tax)
    
    # Grid lines
    x_grid_lines = ""
    for x in range(0, 101, 20):
        x_pos = scale_x(x)
        x_grid_lines += f'<line x1="{x_pos}" y1="{margin["top"]}" x2="{x_pos}" y2="{height - margin["bottom"]}" class="grid"/>\n'
    
    y_ticks = np.linspace(y_min, y_max, 6)
    y_grid_lines = ""
    y_labels = ""
    for y in y_ticks:
        y_pos = scale_y(y)
        y_grid_lines += f'<line x1="{margin["left"]}" y1="{y_pos}" x2="{width - margin["right"]}" y2="{y_pos}" class="grid"/>\n'
        y_labels += f'<text x="{margin["left"] - 15}" y="{y_pos + 5}" class="axis-label">{y:.0f}</text>\n'
    
    # X-axis labels
    x_labels = ""
    for x in range(0, 101, 20):
        x_pos = scale_x(x)
        x_labels += f'<text x="{x_pos}" y="{height - margin["bottom"] + 25}" class="axis-label">{x}%</text>\n'
    
    # Key points
    opt_x, opt_y = scale_x(opt_d_pct), scale_y(VL_top)
    vu_y = scale_y(V_U)
    
    # Annotations
    x_left = max(0, opt_d_pct - 7)
    x_right = min(100, opt_d_pct + 7)
    x_dist = min(100, x_right + 3)
    
    pvts_y = scale_y(V_U + (T_c/100) * V_U * (x_left/100) * np.exp(-2.0 * (x_left/100)))
    vl_annotation_y = scale_y(V_L[x_right])
    
    # SVG content
    svg_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg">
    <defs>
        <style>
            .line-vl {{ stroke: #000000; stroke-width: 3; fill: none; stroke-linecap: round; stroke-linejoin: round; }}
            .line-vtax {{ stroke: #d62728; stroke-width: 2.5; fill: none; stroke-linecap: round; stroke-linejoin: round; }}
            .line-vu {{ stroke: #6366F1; stroke-width: 2; stroke-dasharray: 8,5; fill: none; }}
            .line-opt {{ stroke: #666666; stroke-width: 1.5; stroke-dasharray: 5,5; fill: none; }}
            .grid {{ stroke: #e5e5e5; stroke-width: 0.5; }}
            .axis {{ stroke: #333333; stroke-width: 1.5; }}
            .axis-label {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; font-size: 13px; fill: #444; text-anchor: middle; }}
            .axis-title {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; font-size: 16px; fill: #333; text-anchor: middle; font-weight: 500; }}
            .title {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; font-size: 24px; font-weight: bold; fill: #1E3A8A; text-anchor: middle; }}
            .legend-text {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; font-size: 14px; fill: #333; }}
            .annotation {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; font-size: 12px; fill: #666; text-anchor: middle; }}
            .optimal-point {{ fill: #ff4444; stroke: white; stroke-width: 2; }}
        </style>
    </defs>
    
    <!-- Background -->
    <rect width="{width}" height="{height}" fill="white"/>
    
    <!-- Title -->
    <text x="{width/2}" y="40" class="title">📐 Optimal Capital Structure</text>
    
    <!-- Grid -->
    {x_grid_lines}
    {y_grid_lines}
    
    <!-- Chart border -->
    <rect x="{margin['left']}" y="{margin['top']}" width="{chart_width}" height="{chart_height}" 
          fill="none" stroke="#ddd" stroke-width="1"/>
    
    <!-- Axes -->
    <line x1="{margin['left']}" y1="{height - margin['bottom']}" x2="{width - margin['right']}" y2="{height - margin['bottom']}" class="axis"/>
    <line x1="{margin['left']}" y1="{margin['top']}" x2="{margin['left']}" y2="{height - margin['bottom']}" class="axis"/>
    
    <!-- Data lines -->
    <path d="{vtax_path}" class="line-vtax"/>
    <path d="{vl_path}" class="line-vl"/>
    
    <!-- V_U horizontal line -->
    <line x1="{margin['left']}" y1="{vu_y}" x2="{width - margin['right']}" y2="{vu_y}" class="line-vu"/>
    
    <!-- Optimal debt vertical line -->
    <line x1="{opt_x}" y1="{margin['top']}" x2="{opt_x}" y2="{height - margin['bottom']}" class="line-opt"/>
    
    <!-- Optimal point -->
    <circle cx="{opt_x}" cy="{opt_y}" r="5" class="optimal-point"/>
    
    <!-- Axis labels -->
    {x_labels}
    {y_labels}
    
    <!-- Axis titles -->
    <text x="{width/2}" y="{height - 25}" class="axis-title">Debt/Equity (%)</text>
    <text x="25" y="{height/2}" class="axis-title" transform="rotate(-90 25 {height/2})">Firm value (€ million)</text>
    
    <!-- Legend -->
    <g transform="translate({width - margin['right'] + 20}, {margin['top'] + 40})">
        <rect x="-15" y="-15" width="140" height="120" fill="white" stroke="#ddd" stroke-width="1" rx="5"/>
        <text x="0" y="0" class="legend-text" style="font-weight: 600;">Legend</text>
        <line x1="0" y1="20" x2="25" y2="20" class="line-vl"/>
        <text x="30" y="25" class="legend-text">V<tspan baseline-shift="sub" font-size="11">L</tspan> (levered)</text>
        <line x1="0" y1="40" x2="25" y2="40" class="line-vtax"/>
        <text x="30" y="45" class="legend-text">V (tax benefit only)</text>
        <line x1="0" y1="60" x2="25" y2="60" class="line-vu"/>
        <text x="30" y="65" class="legend-text">V<tspan baseline-shift="sub" font-size="11">U</tspan> (unlevered)</text>
        <line x1="0" y1="80" x2="25" y2="80" class="line-opt"/>
        <text x="30" y="85" class="legend-text">Optimal debt</text>
    </g>
    
    <!-- Annotations -->
    <text x="{opt_x}" y="{margin['top'] - 10}" class="annotation">Optimal: {opt_d_pct}% debt</text>
    <text x="{opt_x + 60}" y="{opt_y - 15}" class="annotation">€{VL_top:,.1f}M</text>
    
    <!-- V_U label -->
    <text x="{width - margin['right'] - 50}" y="{vu_y - 8}" class="annotation">V<tspan baseline-shift="sub" font-size="10">U</tspan></text>
    
    <!-- Parameter info -->
    <g transform="translate(30, {height - 60})">
        <text x="0" y="0" class="annotation" style="font-weight: 600;">Parameters:</text>
        <text x="0" y="15" class="annotation">Tax rate: {T_c}%</text>
        <text x="0" y="30" class="annotation">V<tspan baseline-shift="sub" font-size="10">U</tspan>: €{V_U:,.0f}M</text>
        <text x="120" y="15" class="annotation">Max distress cost: €{FD_total:,.0f}M</text>
    </g>
    
    <!-- Footer -->
    <text x="{width/2}" y="{height - 8}" class="annotation">
        Developed by Prof. Marc Goergen with the help of ChatGPT
    </text>
</svg>'''
    
    return svg_content.encode()

def smart_svg_export(fig, d_pct, V_L, V_tax, V_U, opt_d_pct, VL_top, T_c, FD_total):
    """Try kaleido first, fallback to manual SVG"""
    
    # Try kaleido/plotly export first
    try:
        # Configure environment
        chrome_paths = ['/usr/bin/chromium-browser', '/usr/bin/chromium', '/usr/bin/google-chrome']
        for path in chrome_paths:
            if os.path.exists(path):
                os.environ['CHROME_BIN'] = path
                break
        
        svg_bytes = fig.to_image(format="svg", width=1200, height=620, scale=2)
        return svg_bytes, "Plotly/Kaleido"
    except:
        pass
    
    # Fallback to manual high-quality SVG
    manual_svg = create_production_svg(d_pct, V_L, V_tax, V_U, opt_d_pct, VL_top, T_c, FD_total)
    return manual_svg, "Manual"

def smart_svg_export_fixed(fig, d_pct, V_L, V_tax, V_U, opt_d_pct, VL_top, T_c, FD_total):
    """Fixed SVG export with proper scaling and editability"""
    
    # Try kaleido/plotly export first
    try:
        # Configure environment
        chrome_paths = ['/usr/bin/chromium-browser', '/usr/bin/chromium', '/usr/bin/google-chrome']
        for path in chrome_paths:
            if os.path.exists(path):
                os.environ['CHROME_BIN'] = path
                break
        
        svg_bytes = fig.to_image(format="svg", width=1400, height=900, scale=2)
        return svg_bytes, "Plotly/Kaleido"
    except:
        pass
    
    # Fallback to improved manual SVG
    manual_svg = create_editable_svg(d_pct, V_L, V_tax, V_U, opt_d_pct, VL_top, T_c, FD_total)
    return manual_svg, "Manual (Editable)"

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

# ───────────  PRODUCTION DOWNLOAD SECTION  ─────────── #
st.subheader("📥 Export Options")

col1, col2, col3 = st.columns(3)

with col1:
    # Smart SVG export with improved scaling and editability
    svg_data, svg_method = smart_svg_export_fixed(fig, d_pct, V_L, V_tax, V_U, opt_d_pct, VL_top, T_c, FD_total)
    st.download_button(
        "⬇️ Download SVG",
        svg_data,
        file_name="capital_structure.svg",
        mime="image/svg+xml",
        help=f"Fully editable SVG ({svg_method}) - No clipping, grouped elements"
    )

with col2:
    # PNG export
    try:
        png_bytes = fig.to_image(format="png", width=1200, height=620, scale=2)
        st.download_button(
            "⬇️ Download PNG",
            png_bytes,
            file_name="capital_structure.png",
            mime="image/png",
            help="High-resolution PNG image"
        )
    except:
        st.info("💡 Use the camera icon in the chart toolbar for PNG download")

with col3:
    # HTML export
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
