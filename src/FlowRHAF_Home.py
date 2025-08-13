import streamlit as st
from PIL import Image
st.set_page_config(layout='wide')

image = Image.open(r'src\Images\river.jpg')
st.image(image, use_container_width=True)

st.title("Welcome to the River Health Asessment Framework (RHAF) Assessment Application")
st.subheader("This application is designed to assist in the assessment of river health by providing tools for analyzing and visualizing daily flow data. This application" \
" contains tools to assess the River Flow component of the RHAF")
st.markdown("The application currently includes the following features:")
st.markdown("- **Peak Flow Analysis**: Analyze peak flow data from USGS stations. This includes peak flow analysis, base flow analysis, and rate of change analysis.")
st.markdown("- **Base Flow Analysis**: Analyze base flow data from USGS stations. This application is used to determine the frequency, duration, and magnitude of dry season flows.")
st.markdown("- **Rate of Change Analysis**: Analyze the rate of change of flow data from USGS stations. This application is used to identify the impact of artifically abrupt changes in flow" \
" on river health.")





st.sidebar.markdown("# Home")

