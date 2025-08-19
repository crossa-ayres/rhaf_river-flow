import streamlit as st
from PIL import Image
from utils.peak_flow.peakFlow_utils import peakFlow_main as pfm, generate_summary_df
from utils.common_utils.utils import subset_by_season, plot_seasonal_data, manual_upload_daily_flow_data



st.set_page_config(layout='wide')
image = Image.open('./src/Images/peakflow.jpg')
st.image(image, use_container_width=True)
st.title("Peak Flow Data Analysis")
st.subheader("This application allows the user to evaluate river health on the basis of flow magnitude. Flow data used for this analysis can either be downloaded from the USGS website or manually uploaded as a txt file.")

st.markdown("##### The application requires the following inputs:")
st.markdown("- **USGS Station ID**")
st.markdown("- **Begin Analysis On (year)**: The year from which to start the analysis. If the Download Data option is selected, the application will download data from the USGS website starting from this year.")
st.markdown("- **Average Daily Flow Threshold (cfs)**: The threshold for average daily flow to determine relevant flow events. This is used to identify flow events that exceed the specified threshold. The default value is 500 cfs, but it can be adjusted based on the user's needs.")
st.sidebar.header("Input Parameters")
#add checkbox to determine if the user wants to manually upload data or allow the tool to download it from the USGS website


if st.sidebar.checkbox("**Download data from USGS website**", value=False, key="download_data"):
    usgs_station_id = st.sidebar.text_input("**USGS Station ID**")
    begin_year = st.sidebar.text_input("**Begin Analysis On (year)**")
    pf_threshold = st.sidebar.number_input("**Mean Daily Flow Threshold (cfs)**", min_value=0, value=500)
    upload_type = "downloaded"

elif st.sidebar.checkbox("**Manually upload peak flow data**", value=False, key="upload_data"):
    uploaded_file = st.sidebar.file_uploader("Upload Peak Flow Data txt file", type=["txt"])
    begin_year = st.sidebar.text_input("**Begin Analysis On (year)**")
    pf_threshold = st.sidebar.number_input("**Mean Daily Flow Threshold (cfs)**", min_value=0, value=500)
    upload_type = "uploaded"

st.sidebar.markdown("### Note:")
st.sidebar.markdown("The application will use the mean daily flow data (either downloaded from the USGS website or uploaded by the user) and analyze it based on the specified parameters.")
st.markdown("""
    <style>
    div.stButton > button {
        background-color: grey;
        color: white;
        border-radius: 10px;
        border: black;
    }
    div.stButton > button:hover {
        background-color: dark grey;
        color: black;
    }
    </style>
""", unsafe_allow_html=True)
if st.sidebar.button("Analyze Peak Flow Data"):

    #st.write(f"Analyzing peak flow data for USGS Station ID: {usgs_station_id}, starting in {begin_year}, Mean Daily Flow Threshold: {pf_threshold} cfs")
    if upload_type == "uploaded":
        df, above_thresh_df,yearly_analysis,usgs_station_id = pfm(usgs_station_id="000000", begin_year=begin_year, pf_threshold=pf_threshold,upload_type=upload_type,uploaded_file=uploaded_file)
    else:
        df, above_thresh_df,yearly_analysis,_ = pfm(usgs_station_id=usgs_station_id, begin_year=begin_year, pf_threshold=pf_threshold,upload_type=upload_type)

    if df is not None:
        st.write("### Average Daily Flow Data")
        st.write(df)
       
        #find the last year data was collected
        last_year = str(df['date'].max())
        last_year = last_year.split(" ")[0]
        st.write(f"### Gage ID {usgs_station_id} contains data up until {last_year}")
        st.subheader(f"Plotted average daily flow values for gage {usgs_station_id}")
        st.line_chart(df.set_index('date')['avg_flow'], use_container_width=True)

        df_group = subset_by_season(df)

        #generate matplotlib figure for spring data
        st.subheader("Seasonal Flow Data:")
        
        for season, season_df in zip(["Spring", "Summer", "Fall", "Winter"], df_group):
            #plot the seasonal data
            with st.expander(f"{season} Average Annual Flow Data"):
                fig = plot_seasonal_data(season_df, usgs_station_id, season)
            
                st.pyplot(fig)
     
    if not above_thresh_df.empty:
        
        
        #write the unique years present in the above_thresh_df
        unique_years = above_thresh_df['year'].unique()
        st.header("Threshold Analysis of Gage Data")
        
        
        #write the yearly analysis
        st.subheader("Yearly Summary:")
        st.write(f"##### Summary of Peak Flow Data Above {pf_threshold} cfs by Year:")

        summary_df = generate_summary_df(yearly_analysis, pf_threshold)

        #col1, col2 = st.columns(2)
        #col2.dataframe( unique_years)
        st.dataframe(summary_df)
        #create streamlit bar chart for summary df data
        st.subheader(f"Bar Chart Showing Total Days per Year Above {pf_threshold} cfs")
        st.bar_chart(summary_df[f"Total Days Above {pf_threshold} cfs"], use_container_width=True)
      
        
    else:
        st.header("No dates found with flow above the specified threshold.")