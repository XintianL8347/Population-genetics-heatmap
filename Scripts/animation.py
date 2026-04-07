import streamlit as st
from matplotlib.animation import FuncAnimation


def make_ani(fig, update_fun, time_range, step, filename, fargs):
    assert fargs[0] is fig, "Please check your input arguments :)"
    ani = FuncAnimation(
        fig,
        update_fun,
        frames=range(time_range[1], time_range[0], -step),
        fargs=fargs,
        repeat=False,
    )
    ani.save(filename, fps=8)

    video_file = open(filename, "rb")
    video_bytes = video_file.read()

    st.video(video_bytes)
    # st.download_button("Download Video", video_file, "viking_migration.mp4")
    st.write(f"Video saved locally: {filename}")
