#!/usr/bin/env python3
"""
app.py

Description:
This program will run a website, and according to user's choice, generate a single mordern genetic heatmap,
multiple ancient genetic heatmaps across time bins, and/or an animation of ancient genetic heatmaps
using algorithms from corresponding imported scripts.
All the genetic distances are calculated with reference to Icelandic Vikings (CultureID = 1000).

User-defined module: animation, interpolation, linear_migration, modern, multimap, site_turnover
Non-standard modules: matplotlib, pandas, streamlit

Procedure:
0. Load internal data and offer options on the web page
1. Execute different logics (modern map, multiple maps, animation) based on the user's choice
    1.5. If animation is chosen, allow the user to select algorithm and customize parameters
2. Display the generated plots or video on the web page

Input: None (however, internal dataset required)
Output: A web app, visualizations, animation videos [optional]

Usage : source .venv/bin/activate
        streamlit run Scripts/app.py

Version: 1.1
Date: 2026-04-08
Name: Xintian Liu
"""

import animation
import interpolation
import linear_migration
import matplotlib.pyplot as plt
import modern
import multimap
import pandas as pd
import site_turnover
import streamlit as st

## ===== Prepare data =====
df_aDNA = pd.read_excel("Dataset/Vikings_aDNA.xlsx")
df_modern = pd.read_excel("Dataset/ModernSamples/GeneticDistances.xlsx")

st.title("Viking Genetic Heatmap Navigator")

## ===== Mordern dataset (global) =====
if st.button("Modern Dataset"):
    # Call function from modern
    fig = modern.plot_heatmap(df_modern)
    st.pyplot(fig)

## ===== Acient dataset (Europe): static multi-map =====
if st.button("Acient Dataset - Multiple Maps"):
    # Calculate the genetic distances
    df_aDNA = multimap.aDNA_pre_process(df_aDNA)
    with st.spinner("Calculating Heatmaps..."):
        # Assign individuals to time bins (use the midpoint of each 100 year)
        df_aDNA["Time_Bin"] = (df_aDNA["Mean date (BP)"] // 100) * 100 + 50

        # Display plots in a 2-column grid
        cols = st.columns(2)
        n_plot = 0
        skipped = []

        # Loop over the time bins
        for t in sorted(df_aDNA["Time_Bin"].unique()):
            current_bin = df_aDNA[df_aDNA["Time_Bin"] == t]
            yr = int(1950 - t)  # Covert BP to calendar year
            fig = multimap.plot_acient_bin(current_bin, yr)
            if fig:
                with cols[n_plot % 2]:
                    st.subheader(f"Year: {yr}")
                    st.pyplot(fig)
                n_plot += 1
            else:
                # Track skipped bins due to not enough data points
                skipped.append(yr)

        if skipped:
            st.write(f":large_orange_diamond: **Skipped {len(skipped)} time bins due to too few data points:** " + ", ".join(map(str, skipped)))

## ===== Acient dataset (Europe): animation =====

# Use session state to keep the animation UI visible after button click,
# since Streamlit reruns the script on every interaction
if "show_animation_ui" not in st.session_state:
    st.session_state.show_animation_ui = False

if st.button("Ancient Dataset - Animation"):
    st.session_state.show_animation_ui = True

if st.session_state.show_animation_ui:
    # Calculate distances (same as in multimap)
    df_aDNA = multimap.aDNA_pre_process(df_aDNA)

    # Let the user choose algorithm
    algo = st.selectbox(
        "Please Choose Algorithm",
        ("3D-RBF", "Site Turnover", "Linear Migration"),
        index=None,
        placeholder="Select to continue",
    )

    # Specify time range and sliding window parameters
    time_range = st.slider("BP Range", 700, 1300, (750, 1250), step=5)
    st.caption(":red-background[NOTE:] *BP = the number of years before 1950*")

    window = st.number_input(
        "Specify window size (defualt 100)",
        min_value=10,
        max_value=time_range[1] - time_range[0],
        value=100,
    )
    step = st.number_input("Specify step size (defualt 10)", min_value=1, max_value=100, value=10)

    # ===== Algo 1: 3D Rbf =====
    if algo == "3D-RBF" and st.button("Generate Animation"):
        with st.spinner("Calculating Heatmaps..."):
            # Fit a 3D rbf model across (Lat, Long, Time) using the full dataset
            rbf_3d = interpolation.create_3drbf(df_aDNA)
            fig = plt.figure(figsize=(10, 7))

            # Make animation: be careful about input arguments
            animation.make_ani(
                fig,
                interpolation.update,
                time_range,
                window,
                step,
                "viking_genemap_3drbf.mp4",
                (fig, df_aDNA, rbf_3d, window),
            )

    # ===== Algo 2: Site Turnover =====
    if algo == "Site Turnover" and st.button("Generate Animation"):
        with st.spinner("Calculating Heatmaps..."):
            # Create a uniq siteID per geographic location
            df_aDNA["Site_ID"] = df_aDNA["Lat"].astype(str) + "_" + df_aDNA["Long"].astype(str)
            fig = plt.figure(figsize=(10, 7))
            # Track the latest known gen-distance per location across time/frames
            latest_world_state = {}

            animation.make_ani(
                fig,
                site_turnover.update,
                time_range,
                window,
                step,
                "viking_genemap_turnover.mp4",
                (fig, df_aDNA, window, latest_world_state),
            )

    # ===== Algo 3: Linear Migration =====
    if algo == "Linear Migration" and st.button("Generate Animation"):
        with st.spinner("Calculating Heatmaps..."):
            fig = plt.figure(figsize=(10, 7))
            # Track the latest known gen-distance info per cultural group across time/frames
            latest_world_state = {}

            animation.make_ani(
                fig,
                linear_migration.update,
                time_range,
                window,
                step,
                "viking_genemap_migration.mp4",
                (fig, df_aDNA, window, latest_world_state),
            )
