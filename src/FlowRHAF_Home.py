import streamlit as st
from PIL import Image
st.set_page_config(layout='wide')

image = Image.open('./src/Images/river.jpg')
st.image(image, use_container_width=True)

st.title("Welcome to the River Health Asessment Framework (RHAF) Assessment Application")
st.subheader("This application is designed to assist in the assessment of river health by providing tools for analyzing and visualizing daily flow data. This application" \
" contains tools to assess the River Flow component of the RHAF")
st.markdown("The application currently includes the following features:")
st.markdown("- **Peak Flow Analysis**: Analyze peak flow data from USGS stations. This includes peak flow analysis, base flow analysis, and rate of change analysis.")
st.markdown("- **Base Flow Analysis**: Analyze base flow data from USGS stations. This application is used to determine the frequency, duration, and magnitude of dry season flows.")
st.markdown("- **Rate of Change Analysis**: Analyze the rate of change of flow data from USGS stations. This application is used to identify the impact of artifically abrupt changes in flow" \
" on river health.")

st.header("Getting Started")
st.write("To get started, select one of the analysis options from the sidebar. Each analysis tool will guide you through the necessary inputs and provide visualizations and summaries of the results.")
st.write("To test out the tool, the user can use the following USGS Station IDs:")
st.markdown("- Peak Flow Analysis: 06721000 (South Platte River at Fort Lupton, CO.), period of record: 04/29/1929 - 08/12/2025")
st.markdown("- Base Flow Analysis: 06752280 (Cache La Poudre River at Fort Collins, CO.), period of record: 10/01/1979 - 08/12/2025")
st.markdown("- Rate of Change Analysis: 06752260 (Cache La Poudre River at Fort Collins, CO.) 04/08/1975 - 08/12/2025")
st.markdown(f"#### For additional information on the RHAF, please visit the Coalition for the Poudre Watershed website at the following link:"\
                   " https://www.poudrewatershed.org/rhaf")





st.sidebar.markdown("# Home")


