#!/usr/bin/env python3
"""
app.py

Description:
This program will run a website, and according to user's choice, generate a single mordern genetic heatmap,
multiple ancient genetic heatmaps across time bins, and/or an animation of ancient genetic heatmaps
using algorithms from corresponding imported scripts.
All the genetic distances are calculated with reference to Icelandic Vikings.

User-defined module: animation, immortal, interpolation, modern, moving, multimap
Non-standard modules: matplotlib, pandas, streamlit

Procedure:
0. Open internal data and offer options on the web page
1. Execute different logics (modern map, multiple maps, animation) based on the user's choice
    1.5. If animation is chosen, allow the user customize parameters
2. Display the generated plots or video on the web page

Input: None
Output: A web app, animation videos [optional]

Usage : source .venv/bin/activate
        streamlit run Scripts/app.py

Version: 1.1
Date: 2026-04-08
Name: Xintian Liu
"""

import animation
import immortal
import interpolation
import matplotlib.pyplot as plt
import modern
import moving
import multimap
import pandas as pd
import streamlit as st

# Open data and collect all the genetic pool columns
df_aDNA = pd.read_excel("Dataset/Vikings_aDNA.xlsx")
df_modern = pd.read_excel("Dataset/ModernSamples/GeneticDistances.xlsx")

st.title("Viking Genetic Heatmap Navigator")

if st.button("Modern Dataset"):
    fig = modern.plot_heatmap(df_modern)
    st.pyplot(fig)

if st.button("Acient Dataset - Multiple Maps"):
    df_aDNA = multimap.aDNA_pre_process(df_aDNA)
    with st.spinner("Calculating Heatmaps..."):
        # Assign individuals to time bins (use the middle point of each 100 year)
        df_aDNA["Time_Bin"] = (df_aDNA["Mean date (BP)"] // 100) * 100 + 50
        # Loop over the time bins
        # for t in sorted(df_aDNA["Time_Bin"].unique()):
        # current_bin = df_aDNA[df_aDNA["Time_Bin"] == t]
        # Call the plotting function
        # fig = alg.plot_acient_bin(current_bin, int(1950 - t))
        # st.pyplot(fig)

        # Create as many columns as there are years
        cols = st.columns(2)
        n_plot = 0
        skipped = []

        for t in sorted(df_aDNA["Time_Bin"].unique()):
            current_bin = df_aDNA[df_aDNA["Time_Bin"] == t]
            # 1. Generate the fig using your logic function
            yr = int(1950 - t)
            fig = multimap.plot_acient_bin(current_bin, yr)
            if fig:
                with cols[n_plot % 2]:
                    # 2. Display in the specific column
                    st.subheader(f"Year: {yr}")
                    st.pyplot(fig)
                n_plot += 1
            else:
                skipped.append(yr)
                # st.markdown(f"Skipping {yr}: Too few data points.")
        if skipped:
            st.write(f":large_orange_diamond: **Skipped {len(skipped)} time bins due to too few data points:** " + ", ".join(map(str, skipped)))

if "show_animation_ui" not in st.session_state:
    st.session_state.show_animation_ui = False

if st.button("Ancient Dataset - Animation"):
    st.session_state.show_animation_ui = True

# 3. App runs the logic and shows the plot
if st.session_state.show_animation_ui:
    df_aDNA = multimap.aDNA_pre_process(df_aDNA)
    # 1. User selects algorithm in sidebar
    algo = st.selectbox(
        "Please Choose Algorithm",
        ("3D-RBF", "Immortal individual", "Moving individual"),
        index=None,
        placeholder="Select to continue",
    )

    # 2. User selects timeframe
    time_range = st.slider("BP Range", 700, 1300, (750, 1250), step=5)
    st.caption(":red-background[NOTE:] *BP = the number of years before 1950*")
    window = st.number_input(
        "Specify window size (defualt 100)",
        min_value=10,
        max_value=time_range[1] - time_range[0],
        value=100,
    )
    step = st.number_input("Specify step size (defualt 10)", min_value=1, max_value=100, value=10)

    if algo == "3D-RBF" and st.button("Generate Animation"):
        with st.spinner("Calculating Heatmaps..."):
            rbf_3d = interpolation.create_3drbf(df_aDNA)
            fig = plt.figure(figsize=(10, 7))
            animation.make_ani(
                fig,
                interpolation.update,
                time_range,
                step,
                "viking_migration_3drbf.mp4",
                (fig, df_aDNA, rbf_3d, window),
            )

    if algo == "Immortal individual" and st.button("Generate Animation"):
        with st.spinner("Calculating Heatmaps..."):
            df_aDNA["Site_ID"] = df_aDNA["Lat"].astype(str) + "_" + df_aDNA["Long"].astype(str)
            fig = plt.figure(figsize=(10, 7))
            latest_world_state = {}

            animation.make_ani(
                fig,
                immortal.update,
                time_range,
                step,
                "viking_migration_immortal.mp4",
                (fig, df_aDNA, window, latest_world_state),
            )

    if algo == "Moving individual" and st.button("Generate Animation"):
        with st.spinner("Calculating Heatmaps..."):
            fig = plt.figure(figsize=(10, 7))
            latest_world_state = {}
            animation.make_ani(
                fig,
                moving.update,
                time_range,
                step,
                "viking_migration_moving.mp4",
                (fig, df_aDNA, window, latest_world_state),
            )
