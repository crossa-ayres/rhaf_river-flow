import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
st.set_page_config(layout='wide')
from utils.base_flow.baseFlow_utils import baseFlow_main as bfm,generate_summary_df
from utils.common_utils.utils import subset_by_season, plot_seasonal_data

st.title("Base Flow Data Analysis")
st.subheader("This application allows you to download and analyze base flow data from the USGS website.")
st.markdown("##### The application requires the following inputs:")
st.markdown("- USGS Station ID")
st.markdown("- Begin Year")
#st.markdown("- Average Daily Flow Threshold (cfs)")
st.sidebar.header("Input Parameters")
#add checkbox to determine if the user wants to manually upload data or allow the tool to download it from the USGS website

if st.sidebar.checkbox("Manually upload peak flow data", value=False, key="upload_data"):
    uploaded_file = st.sidebar.file_uploader("Upload Peak Flow Data txt file", type=["txt"])
elif st.sidebar.checkbox("Download data from USGS website", value=False, key="download_data"):
    usgs_station_id = st.sidebar.text_input("USGS Station ID")
    begin_year = st.sidebar.text_input("Begin Year")
    trout_threshold = st.sidebar.number_input("Stable Flow Threshold (cfs)", min_value=0, value=35)
    min_threshold = st.sidebar.number_input("Minimum Flow Threshold (cfs)", min_value=0, value=10)
    #pf_threshold = st.sidebar.number_input("Mean Daily Flow Threshold (cfs)", min_value=0, value=500)
st.sidebar.markdown("### Note:")
st.sidebar.markdown("The application will download mean daily flow data from the USGS website and analyze it based on the specified parameters.")

if st.sidebar.button("Analyze Base Flow Data"):

    st.write(f"Analyzing base flow data for USGS Station ID: {usgs_station_id}, analysis starting in {begin_year}")
    df, trout_analysis, min_analysis = bfm(usgs_station_id,begin_year,trout_threshold, min_threshold)
    #convert trout_analysis to a dataframe
    trout_analysis_df = pd.DataFrame.from_dict(trout_analysis, orient='index').reset_index()
    trout_analysis_df.columns = ['year', 'Total Days Below Threshold', 'Years After Previous', 'Average Flow Below Threshold', 'Max Flow Below Threshold', 'Min Flow Below Threshold']
    min_analysis_df = pd.DataFrame.from_dict(min_analysis, orient='index').reset_index()
    min_analysis_df.columns = ['year', 'Total Days Below Min Threshold', 'Years After Previous', 'Average Flow Below Min Threshold', 'Max Flow Below Min Threshold', 'Min Flow Below Min Threshold']
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
            with st.expander(f"{season} Average Annual Flow Data"):
                fig = plot_seasonal_data(season_df, usgs_station_id, season)
                st.pyplot(fig)
    
    if not trout_analysis_df.empty:
        
    
        st.title(f"Threshold Analysis of Gage Data - Stable Flow Threshold ({trout_threshold} cfs)")
        
        #subset df dataframe by winter in the season column
        spring_df = df[df['season'] == 'Spring']
        summer_df = df[df['season'] == 'Summer']
        fall_df = df[df['season'] == 'Fall']
        winter_df = df[df['season'] == 'Winter']
        
       
        #calculate percent of days in winter_df where flow is below trout_threshold
        winter_below_threshold = (winter_df[winter_df['avg_flow'] < trout_threshold].shape[0] / winter_df.shape[0]) * 100
        spring_below_threshold = (spring_df[spring_df['avg_flow'] < trout_threshold].shape[0] / spring_df.shape[0]) * 100
        summer_below_threshold = (summer_df[summer_df['avg_flow'] < trout_threshold].shape[0] / summer_df.shape[0]) * 100
        fall_below_threshold = (fall_df[fall_df['avg_flow'] < trout_threshold].shape[0] / fall_df.shape[0]) * 100
    
        st.markdown(f'<h2 style="color:red;">Seasonal Analysis of Flow Below Stable Threshold ({trout_threshold} cfs)</h2>', unsafe_allow_html=True)
        st.write(f"##### Percentage of Days Below {trout_threshold} cfs by Season:")
        if winter_below_threshold > 50:
            st.markdown(f'<h3 style="color:red;">Winter: {winter_below_threshold:.2f}%</h3>', unsafe_allow_html=True)
        else:
            st.write(f"Winter: {winter_below_threshold:.2f}%")
        st.write(f"Spring: {spring_below_threshold:.2f}%")
        st.write(f"Summer: {summer_below_threshold:.2f}%")
        st.write(f"Fall: {fall_below_threshold:.2f}%")
        #write the yearly analysis
        st.subheader("Yearly Analysis:")
        st.write(f"##### Yearly Analysis of Average Daily Flow Data Below {trout_threshold} cfs:")

        summary_df = generate_summary_df(trout_analysis, trout_threshold)

        
        st.dataframe(summary_df)
        #create streamlit bar chart for summary df data
  
        st.markdown(f'<h3 style="color:blue;">Bar Chart of Total Days per Year Below {trout_threshold} cfs</h3>', unsafe_allow_html=True)
        with st.expander(f"Flow Below Stable Threshold ({trout_threshold} cfs) Yearly Summary - Figure"):
            st.bar_chart(summary_df[f"Total Days Below {trout_threshold} cfs"], use_container_width=True)

        
    else:
        st.write(f"No data available below the stable flow threshold of {trout_threshold} cfs.")
    if not min_analysis_df.empty:
        st.title(f"Threshold Analysis of Gage Data - Minimum Flow Threshold ({min_threshold} cfs)")
        
         #calculate percent of days in winter_df where flow is below trout_threshold
        winter_below_threshold = (winter_df[winter_df['avg_flow'] < min_threshold].shape[0] / winter_df.shape[0]) * 100
        spring_below_threshold = (spring_df[spring_df['avg_flow'] < min_threshold].shape[0] / spring_df.shape[0]) * 100
        summer_below_threshold = (summer_df[summer_df['avg_flow'] < min_threshold].shape[0] / summer_df.shape[0]) * 100
        fall_below_threshold = (fall_df[fall_df['avg_flow'] < min_threshold].shape[0] / fall_df.shape[0]) * 100
    
        st.markdown(f'<h2 style="color:red;">Seasonal Analysis of Flow Below Minimum Threshold ({min_threshold} cfs)</h2>', unsafe_allow_html=True)
        st.write(f"##### Percentage of Days Below {min_threshold} cfs by Season:")
        if winter_below_threshold > 10:
            st.markdown(f'<h3 style="color:red;">Winter: {winter_below_threshold:.2f}%</h3>', unsafe_allow_html=True)
        else:
            st.write(f"Winter: {winter_below_threshold:.2f}%")
        st.write(f"Spring: {spring_below_threshold:.2f}%")
        st.write(f"Summer: {summer_below_threshold:.2f}%")
        st.write(f"Fall: {fall_below_threshold:.2f}%")

        st.subheader("Yearly Analysis:")
        st.write(f"##### Yearly Analysis of Average Daily Flow Data Below {min_threshold} cfs:")

        summary_df = generate_summary_df(min_analysis, min_threshold)

        
        st.dataframe(summary_df)
        #create streamlit bar chart for summary df data
        #st.subheader(f"Bar Chart of Total Days per Year Below {min_threshold} cfs")
        st.markdown(f'<h3 style="color:#ffaa00;">Bar Chart of Total Days per Year Below {min_threshold} cfs</h3>', unsafe_allow_html=True)
        with st.expander(f"Flow Below Minimum Threshold ({min_threshold} cfs) Yearly Summary - Figure"):
            st.bar_chart(summary_df[f"Total Days Below {min_threshold} cfs"], use_container_width=True, color="#ffaa00")

       
    else:
        st.write(f"No data available below the minimum flow threshold of {min_threshold} cfs.")
  
    