import streamlit as st
from matplotlib.animation import FuncAnimation


def make_ani(fig, update_fun, time_range, window, step, filename, fargs):
    assert fargs[0] is fig, "Please check your input arguments :)"
    ani = FuncAnimation(
        fig,
        update_fun,
        frames=range(time_range[1], time_range[0] + window - step, -step),
        fargs=fargs,
        repeat=False,
    )
    ani.save(filename, fps=8)

    video_file = open(filename, "rb")
    video_bytes = video_file.read()

    st.video(video_bytes)
    # let the user know where the video is saved
    st.write(f"**Video saved locally: {filename}**")
