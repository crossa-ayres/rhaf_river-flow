import streamlit as st
from PIL import Image
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import altair as alt
from utils.peak_flow.peakFlow_utils import peakFlow_main as pfm, generate_summary_df
from utils.common_utils.utils import subset_by_season, plot_seasonal_data, manual_upload_daily_flow_data,plot_waterYear_data, return_waterYr_dict



st.set_page_config(layout='wide')
#left_co, cent_co,last_co = st.columns(3)
#with cent_co:

image = Image.open('./src/Images/river.png')
st.image(image, width='stretch')
logo = Image.open('./src/Images/logo.png')
st.sidebar.image(logo)
st.sidebar.divider()
st.divider()
st.title("Peak Flow Data Analysis")
st.subheader("This application allows the user to evaluate river health on the basis of flow magnitude. Flow data used for this analysis can either be downloaded from the USGS website or manually uploaded as a txt file.")

st.markdown("##### The application requires the following inputs:")
st.markdown("- **USGS Station ID**")
st.markdown("- **Begin Analysis On (year)**: The year from which to start the analysis. If the Download Data option is selected, the application will download data from the USGS website starting from this year.")
st.markdown("- **Average Daily Flow Threshold (cfs)**: The threshold for average daily flow to determine relevant flow events. This is used to identify flow events that exceed the specified threshold. The default value is 500 cfs, but it can be adjusted based on the user's needs.")
st.divider()
st.sidebar.title("Input Parameters")
#add checkbox to determine if the user wants to manually upload data or allow the tool to download it from the USGS website


if st.sidebar.checkbox("**Download data from USGS website**", value=False, key="download_data"):
    usgs_station_id = st.sidebar.text_input("**USGS Station ID**")
    begin_year = st.sidebar.text_input("**Begin Analysis On (year)**")
    end_year = "2025"
    #pf_threshold = st.sidebar.number_input("**Mean Daily Flow Threshold (cfs)**", min_value=0, value=500)
    pf_threshold = 0
    upload_type = "downloaded"

#elif st.sidebar.checkbox("**Manually upload peak flow data**", value=False, key="upload_data"):
#    uploaded_file = st.sidebar.file_uploader("Upload Peak Flow Data txt file", type=["txt"])
#    begin_year = st.sidebar.text_input("**Begin Analysis On (year)**")
    #pf_threshold = st.sidebar.number_input("**Mean Daily Flow Threshold (cfs)**", min_value=0, value=500)
#    pf_threshold = 0
#    upload_type = "uploaded"

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
        df, above_thresh_df,yearly_analysis,usgs_station_id = pfm(usgs_station_id="000000", begin_year=begin_year,end_year = end_year, pf_threshold=pf_threshold,upload_type=upload_type,uploaded_file=uploaded_file)
    else:
        df, above_thresh_df, yearly_analysis,_,annual_peaks,months_dict,water_year_df = pfm(usgs_station_id=usgs_station_id, begin_year=begin_year, pf_threshold=pf_threshold,upload_type=upload_type)

    if df is not None:
        st.divider()
        st.write("### Average Daily Flow Data")
        with st.expander("View Average Daily Flow Data"):
            st.write(df)
       
        #find the last year data was collected
        last_year = str(df['date'].max())
        last_year = last_year.split(" ")[0]
        st.divider()
        st.write(f"### Gage ID {usgs_station_id} contains data up until {last_year}")
        st.subheader(f"Plotted average daily flow values for gage {usgs_station_id}")
        st.line_chart(df.set_index('date')['avg_flow'], use_container_width=True, height=800, x_label="Year", y_label="Average Daily Flow (cfs)")
        st.divider()
        #set the year column to a datetime object
        

        st.subheader(f"Month in Which the Annual Peak Event Occured")
        scatter = alt.Chart(annual_peaks).mark_line(point=True).encode(
            x='date',
            y=alt.Y('month', scale=alt.Scale(domain=[0, 12]))  # Set y-axis bounds
        )
        labels = alt.Chart(annual_peaks).mark_text(
                            align='left',
                            dx=1,  # Adjust horizontal position
                            dy=-8  # Adjust vertical position
                        ).encode(
                            x='date',
                            y='month',
                            text='month_label'
                        )
        chart = scatter + labels
        # Render the chart in Streamlit
        st.altair_chart(chart, use_container_width=True)
        st.divider()


        x_vals = annual_peaks['month'].unique()
        x_vals.sort()
        
        
        histogram = alt.Chart(annual_peaks).mark_bar().encode(
        alt.X('month', axis=alt.Axis(values=x_vals)),  # Binning the Acceleration column , bin=True
        y='count()'  # Counting the number of occurrences
        )
        hist_labels = alt.Chart(annual_peaks).mark_text(
                            align='left',
                            dx=1,  # Adjust horizontal position
                            dy=-8  # Adjust vertical position
                        ).encode(
                            x='month',
                            y='count()',
                            text='month_label'
                        )
        histogram = histogram + hist_labels
        st.altair_chart(histogram, use_container_width=True)
        st.divider()
       
        #plot the water year flows using individual lines for each water year
        st.subheader(f"Water Year Average Daily Flow Data")
        

        water_year_df['day_month'] = water_year_df['date'].dt.strftime('%m-%d')
        water_year_df = water_year_df.sort_values(by=['day_of_waterYear', 'date'])
        with st.expander("View Water Year Average Daily Flow Data"):
            st.write(water_year_df)
        water_year_dict = return_waterYr_dict()
        #group the water year data by water year
        plt.figure(figsize=(12, 6))
        for year in water_year_df['water_year'].unique():
            if year < int(begin_year):
                pass
            else:
                year_df = water_year_df[water_year_df['water_year'] == year]
                plt.plot(year_df['day_month'], year_df['avg_flow'], label=year)
                #set plot ticks to be the month on the x axis
        plt.xticks(ticks=[f"{i:02d}-01" for i in range(1, 13)], labels=[f"{water_year_dict[i]}" for i in range(1, 13)])
        plt.xticks(rotation=90)
        plt.xlabel("Month-Day")
        plt.ylabel("Average Daily Flow (cfs)")
        plt.title(f"Water Year Average Daily Flow Data for Gage {usgs_station_id}")
        plt.legend(title="Water Year", bbox_to_anchor=(1.05, 1), loc='upper left')
        plt.tight_layout()
        st.pyplot(plt)
        #fig = plot_waterYear_data(water_year_df, usgs_station_id)
            
        #st.pyplot(fig)

        #get the average daily flow in december for each year and plot as a histogram
        
        peak_flow_max_month = annual_peaks['month'].mode()[0]
        peak_flow_max_month_average_val = np.round(annual_peaks[annual_peaks['month'] == peak_flow_max_month]['avg_flow'].mean(),0)
        st.write(f"### The average peak flow value for the month of {months_dict[peak_flow_max_month]} is {peak_flow_max_month_average_val} cfs")
        

        december_flows = np.round(df[df['month'] == 12]['avg_flow'].mean(),0)
        st.write(f"### The average daily flow in December across all years is {december_flows} cfs")
        #set the x axis to be the year in the december flows
        

      
        
        #df_group = subset_by_season(df)

        #generate matplotlib figure for spring data
        #st.subheader("Seasonal Flow Data:")
        
        #for season, season_df in zip(["Spring", "Summer", "Fall", "Winter"], df_group):
            #plot the seasonal data
        #    with st.expander(f"{season} Average Annual Flow Data"):
        #        fig = plot_seasonal_data(season_df, usgs_station_id, season)
            
        #        st.pyplot(fig)
     
    #if not above_thresh_df.empty:
        
        
        #write the unique years present in the above_thresh_df
     #   unique_years = above_thresh_df['year'].unique()
     #   st.header("Threshold Analysis of Gage Data")
        
        
        #write the yearly analysis
     #   st.subheader("Yearly Summary:")
     #   st.write(f"##### Summary of Peak Flow Data by Year:")

     #   summary_df = generate_summary_df(yearly_analysis, pf_threshold)

        #col1, col2 = st.columns(2)
        #col2.dataframe( unique_years)
     #   st.dataframe(summary_df)
        #create streamlit bar chart for summary df data
     #   st.subheader(f"Bar Chart Showing Total Days per Year Above {pf_threshold} cfs")
     #   st.bar_chart(summary_df[f"Total Days Above {pf_threshold} cfs"], use_container_width=True)
      
        
    #else:
    #    st.header("No dates found with flow above the specified threshold.")
    