import streamlit as st
import pandas as pd
import immortal
import moving

# import numpy as np
import multimap
import modern
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import interpolation

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

        for i, t in enumerate(sorted(df_aDNA["Time_Bin"].unique())):
            with cols[i % 2]:
                current_bin = df_aDNA[df_aDNA["Time_Bin"] == t]
                # 1. Generate the fig using your logic function
                yr = int(1950 - t)
                fig = multimap.plot_acient_bin(current_bin, yr)
                if fig:
                    # 2. Display in the specific column
                    st.subheader(f"Year: {yr} BP")
                    st.pyplot(fig)
                else:
                    st.markdown(f"Skipping {yr} BP: Too few data points.")

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
    st.write("NOTE: BP = the number of years before 1950")
    window = st.number_input(
        "Specify window size (defualt 100)",
        min_value=10,
        max_value=time_range[1] - time_range[0],
        value=100,
    )
    step = st.number_input(
        "Specify step size (defualt 10)", min_value=1, max_value=100, value=10
    )

    if algo == "3D-RBF":
        if st.button("Generate Animation"):
            with st.spinner("Calculating Heatmaps..."):
                rbf_3d = interpolation.create_3drbf(df_aDNA)
                fig = plt.figure(figsize=(10, 7))
                ani = FuncAnimation(
                    fig,
                    interpolation.update,
                    frames=range(time_range[1], time_range[0], -step),
                    fargs=(fig, df_aDNA, rbf_3d, window),
                    repeat=False,
                )
                ani.save("viking_migration_3drbf.mp4", fps=10)

                # 4. Display it in the Streamlit video player
                # st.video("viking_migration_3drbf.mp4")

                # 5. Provide a download button for the video file
                # with open("viking_migration_3drbf.mp4", "rb") as f:
                # st.video(f.read())
                video_file = open("viking_migration_3drbf.mp4", "rb")
                video_bytes = video_file.read()

                st.video(video_bytes)
                # st.download_button("Download Video", video_file, "viking_migration.mp4")
                st.write("Video saved locally: viking_migration_3drbf.mp4")

    if algo == "Immortal individual":
        if st.button("Generate Animation"):
            with st.spinner("Calculating Heatmaps..."):
                df_aDNA["Site_ID"] = (
                    df_aDNA["Lat"].astype(str) + "_" + df_aDNA["Long"].astype(str)
                )
                fig = plt.figure(figsize=(10, 7))
                latest_world_state = {}
                ani = FuncAnimation(
                    fig,
                    immortal.update,
                    frames=range(time_range[1], time_range[0], -step),
                    fargs=(fig, df_aDNA, window, latest_world_state),
                    repeat=False,
                )
                ani.save("viking_migration_immortal.mp4", fps=10)

                # 4. Display it in the Streamlit video player
                # st.video("viking_migration_3drbf.mp4")

                # 5. Provide a download button for the video file
                # with open("viking_migration_3drbf.mp4", "rb") as f:
                # st.video(f.read())
                video_file = open("viking_migration_immortal.mp4", "rb")
                video_bytes = video_file.read()

                st.video(video_bytes)
                # st.download_button("Download Video", video_file, "viking_migration.mp4")
                st.write("Video saved locally: viking_migration_immortal.mp4")

    if algo == "Moving individual":
        if st.button("Generate Animation"):
            with st.spinner("Calculating Heatmaps..."):
                fig = plt.figure(figsize=(10, 7))
                latest_world_state = {}
                ani = FuncAnimation(
                    fig,
                    moving.update,
                    frames=range(time_range[1], time_range[0], -step),
                    fargs=(fig, df_aDNA, window, latest_world_state),
                    repeat=False,
                )
                ani.save("viking_migration_moving.mp4", fps=10)

                # 4. Display it in the Streamlit video player
                # st.video("viking_migration_3drbf.mp4")

                # 5. Provide a download button for the video file
                # with open("viking_migration_3drbf.mp4", "rb") as f:
                # st.video(f.read())
                video_file = open("viking_migration_moving.mp4", "rb")
                video_bytes = video_file.read()

                st.video(video_bytes)
                # st.download_button("Download Video", video_file, "viking_migration.mp4")
                st.write("Video saved locally: viking_migration_moving.mp4")
