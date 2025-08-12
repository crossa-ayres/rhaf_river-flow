import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from utils.peak_flow.peakFlow_utils import peakFlow_main as pfm, generate_summary_df
from utils.common_utils.utils import subset_by_season, plot_seasonal_data

st.title("Peak Flow Data Analysis")
st.subheader("This application allows you to download and analyze peak flow data from the USGS website.")
st.markdown("##### The application requires the following inputs:")
st.markdown("- USGS Station ID")
st.markdown("- Begin Year")
st.markdown("- Average Daily Flow Threshold (cfs)")
st.sidebar.header("Input Parameters")
#add checkbox to determine if the user wants to manually upload data or allow the tool to download it from the USGS website

if st.sidebar.checkbox("Manually upload peak flow data", value=False, key="upload_data"):
    uploaded_file = st.sidebar.file_uploader("Upload Peak Flow Data txt file", type=["txt"])
elif st.sidebar.checkbox("Download data from USGS website", value=False, key="download_data"):
    usgs_station_id = st.sidebar.text_input("USGS Station ID")
    begin_year = st.sidebar.text_input("Begin Year")
    pf_threshold = st.sidebar.number_input("Mean Daily Flow Threshold (cfs)", min_value=0, value=500)
st.sidebar.markdown("### Note:")
st.sidebar.markdown("The application will download mean daily flow data from the USGS website and analyze it based on the specified parameters.")

if st.sidebar.button("Analyze Peak Flow Data"):

    st.write(f"Analyzing peak flow data for USGS Station ID: {usgs_station_id}, Begin Year: {begin_year}, Mean Daily Flow Threshold: {pf_threshold} cfs")
    df, above_thresh_df,yearly_analysis = pfm(site_id=usgs_station_id, begin_year=begin_year, pf_threshold=pf_threshold)

    if df is not None:
        #st.dataframe(df)
        #find the last year data was collected
        last_year = str(df['date'].max())
        last_year = last_year.split(" ")[0]
        st.write(f"### Gage ID {usgs_station_id} contains data up until {last_year}")
        st.subheader(f"Plotted average daily flow data for gage {usgs_station_id}")
        st.line_chart(df.set_index('date')['avg_flow'], use_container_width=True)

        df_group = subset_by_season(df)

        #generate matplotlib figure for spring data
        st.subheader("Seasonal Flow Data:")
        
        for season, season_df in zip(["Spring", "Summer", "Fall", "Winter"], df_group):
            #plot the seasonal data
            fig = plot_seasonal_data(season_df, usgs_station_id, season)
            st.pyplot(fig)
     
    if not above_thresh_df.empty:
        
        
        #write the unique years present in the above_thresh_df
        unique_years = above_thresh_df['year'].unique()
        st.header("Threshold Analysis of Gage Data")
        st.write(f"##### Years where average daily flow exceeded {pf_threshold} cfs:", unique_years, use_container_width=False)
        st.write(f"##### Total number of days with flow above {pf_threshold} cfs:", len(above_thresh_df))
        #write the yearly analysis
        st.subheader("Yearly Analysis:")
        st.write(f"##### Yearly Analysis of Peak Flow Data Above {pf_threshold} cfs:")

        summary_df = generate_summary_df(yearly_analysis, pf_threshold)

        
        st.dataframe(summary_df)
        #create streamlit bar chart for summary df data
        st.subheader(f"Bar Chart of Total Days per Year Above {pf_threshold} cfs")
        st.bar_chart(summary_df[f"Total Days Above {pf_threshold} cfs"], use_container_width=True)
      
        #st.subheader(f"Summary statistics for flow above {pf_threshold} cfs:")
        #st.write(above_thresh_df['avg_flow'].describe())
        #plot the flow data
        #st.subheader("Peak flow plotted data:")
        #st.line_chart(above_thresh_df.set_index('date')['avg_flow'], use_container_width=True)
        
    else:
        st.write("No dates found with flow above the specified threshold.")