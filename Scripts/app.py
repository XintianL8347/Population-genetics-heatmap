import streamlit as st
# from logic import VikingPersistenceEngine, Viking3DEngine

st.title("Viking Genetic Navigator")

# 1. User selects algorithm in sidebar
algo = st.sidebar.selectbox("Choose Algorithm", ["3D-RBF", "Persistence"])

# 2. User selects timeframe
time_range = st.sidebar.slider("BP Range", 750, 1250, (750, 1250))

# 3. App runs the logic and shows the plot
if st.button("Generate Map"):
    with st.spinner("Calculating Heatmaps..."):
        # This calls your Class logic
        fig = run_my_engine(algo, time_range) 
        st.pyplot(fig)