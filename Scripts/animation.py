import streamlit as st
from matplotlib.animation import FuncAnimation


# The main function for making animations for the 3 algorithms in app.py
def make_ani(fig, update_fun, time_range, window, step, filename, fargs):
    # Sanity check: fargs[0] must be the figure object, as expected by update_fun
    assert fargs[0] is fig, "Please check your input arguments :)"
    ani = FuncAnimation(
        fig,
        update_fun,
        # Animate from longest to shortest BP, i.e., latest to newest time bin, stepping by "step"
        # The "+ window - step" ensures that timebin in the last frame ends exactly at the BP selected by user.
        frames=range(time_range[1], time_range[0] + window - step, -step),
        fargs=fargs,
        repeat=False,
    )
    # Save animation to disk as a video file
    ani.save(filename, fps=8)

    # Read the saved files and stream it in the Streamlit app
    with open(filename, "rb") as video_file:
        video_bytes = video_file.read()

    st.video(video_bytes)
    # let the user know where the video is saved
    st.write(f"**Video saved locally: {filename}**")
