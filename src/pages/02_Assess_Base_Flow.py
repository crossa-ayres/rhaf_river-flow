import streamlit as st
import pandas as pd
from PIL import Image
import altair as alt
st.set_page_config(layout='wide')
from utils.base_flow.baseFlow_utils import baseFlow_main as bfm,generate_summary_df
from utils.common_utils.utils import subset_by_season, plot_seasonal_data, water_year_flows, return_waterYr_dict


image = Image.open('./src/Images/baseflow.png')
st.image(image, width='stretch')
logo = Image.open('./src/Images/logo.png')
st.sidebar.image(logo)
st.sidebar.divider()
st.divider()

st.title("Base Flow Data Analysis")
st.subheader("This application allows the user to analyze base flow data using average daily flow. Flow data can either be downloaded from the USGS website or manually uploaded as a txt file.")
st.markdown("##### The application requires the following inputs:")
st.markdown("- **USGS Station ID**")
st.markdown("- **Begin Analysis On (year)**: The year from which to start the analysis. If the Download Data option is selected, the application will download data from the USGS website starting from this year.")
st.divider()
#st.markdown("- Average Daily Flow Threshold (cfs)")
st.sidebar.title("Input Parameters")
#add checkbox to determine if the user wants to manually upload data or allow the tool to download it from the USGS website


if st.sidebar.checkbox("**Download data from USGS website**", value=False, key="download_data"):
    usgs_station_id = st.sidebar.text_input("USGS Station ID")
    begin_year = st.sidebar.text_input("Begin Analysis On (year)")
    
    min_threshold = st.sidebar.number_input("Minimum Flow Threshold (cfs)", min_value=0, value=10)
    trout_threshold = min_threshold 
    #pf_threshold = st.sidebar.number_input("Mean Daily Flow Threshold (cfs)", min_value=0, value=500)

#elif st.sidebar.checkbox("**Manually upload peak flow data**", value=False, key="upload_data"):
#    uploaded_file = st.sidebar.file_uploader("Upload Peak Flow Data txt file", type=["txt"])

st.sidebar.markdown("### Note:")
st.sidebar.markdown("The application will download mean daily flow data from the USGS website and analyze it based on the specified parameters.")
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
if st.sidebar.button("Analyze Base Flow Data"):

    st.write(f"Analyzing base flow data for USGS Station ID: {usgs_station_id}, analysis starting in {begin_year}")
    df, trout_analysis, min_analysis = bfm(usgs_station_id,begin_year,trout_threshold, min_threshold)
    st.divider()
    st.write("### Average Daily Flow Data")
    with st.expander("Average Daily Flow Data - Raw Data"):
        st.write(df)
    trout_analysis_df = pd.DataFrame.from_dict(trout_analysis, orient='index').reset_index()
    min_analysis_df = pd.DataFrame.from_dict(min_analysis, orient='index').reset_index()
    if trout_analysis_df.empty:
        st.header(f"No flow events exist below the stable flow threshold of {trout_threshold} cfs, skipping analysis.")
    
    else:
        #convert trout_analysis to a dataframe
        
        
        trout_analysis_df.columns = ['year', 'Total Days Below Threshold', 'Years After Previous', 'Average Flow Below Threshold', 'Max Flow Below Threshold', 'Min Flow Below Threshold']
        
        
        
        #st.dataframe(df)
        #find the last year data was collected
        last_year = str(df['date'].max())
        last_year = last_year.split(" ")[0]
        st.write(f"### Gage ID {usgs_station_id} contains data up until {last_year}")
        st.subheader(f"Average daily flow data for gage {usgs_station_id}")

        st.line_chart(df.set_index('date')['avg_flow'], use_container_width=True, height = 1200, x_label='Date', y_label='Average Daily Flow (cfs)')
        st.divider()
        
        #generate a boxplot showing average monthly flow data for all years with labels above the bar showing the month
        st.subheader("Average Monthly Flow Data")
        
        month_dict = return_waterYr_dict()
        
        
        
        monthly_average_flow = df.groupby('month')['avg_flow'].mean().reset_index()
        monthly_average_flow['month_txt'] = monthly_average_flow['month'].map(month_dict)
        monthly_bar_chart = alt.Chart(monthly_average_flow).mark_bar(opacity=0.6,color = 'blue').encode(
        x=alt.X('month:O',title='Month'),
        y=alt.Y('avg_flow:Q', title='Average Monthly Flow (cfs)')
        ).properties(
        width=600,
        height=800
        )
        #set the x axis labels to be the month text
        labels = alt.Chart(monthly_average_flow).mark_text(
            align='center',
            dy=-10  # Adjust vertical position
        ).encode(
            x='month:O',
            y='avg_flow:Q',
            text='month_txt:N'
        )
        
        bar_chart = monthly_bar_chart + labels
        st.altair_chart(bar_chart, use_container_width=True)

        water_year_df = water_year_flows(df)
        winter_waterYear_df = water_year_df[water_year_df['season'] == 'Winter']

        #average annual flow for winter months for each year
        annual_winter_flow = winter_waterYear_df.groupby('water_year')['avg_flow'].mean().reset_index()
        with st.expander("Average Winter Monthly Flow Data by Year - Raw Data"):
            st.write(annual_winter_flow)
        

        
        #calculate the average flow in winter months across all years
        
        

        #minimum flow in winter months across all years
        
        min_winter_flow = winter_waterYear_df.groupby('water_year')['avg_flow'].min().reset_index()
        st.divider()
        
        #combine the two dataframes annual_winter_flow and min_winter_flow into one dataframe and plot as a stacked bar chart using altair
        st.title("Comparison of Average (grey) and Minimum (blue) Winter Monthly Flow Data by Year")

        combined_winter_flow = pd.merge(annual_winter_flow, min_winter_flow, on='water_year', suffixes=('_avg', '_min'))
        #add a column to combined winter flow that is the water year + min as a string
        combined_winter_flow['water_year_label'] = combined_winter_flow['water_year'].astype(str) + " Low Flow"
        combined_winter_flow['Flow (cfs)'] = combined_winter_flow['avg_flow_avg']

        average_winter_flow = winter_waterYear_df['avg_flow'].mean()
        average_min_winter_flow = combined_winter_flow['avg_flow_min'].mean()
        combined_winter_flow['average_flow_winter'] = average_winter_flow
        combined_winter_flow['average_min_flow_winter'] = average_min_winter_flow


        with st.expander("Average and Minimum Winter Monthly Flow Data by Year - Raw Data"):
            st.write(combined_winter_flow)

        avg_points = alt.Chart(combined_winter_flow).mark_point(filled=True, color='black', size=100).encode(
            x=alt.X('water_year:O',title='Water Year'),
            y=alt.Y('Flow (cfs):Q', title='Flow (cfs)')
        )
        min_points = alt.Chart(combined_winter_flow).mark_point(filled=True,color='blue', size=100).encode(
            x='water_year:O',
            y='avg_flow_min:Q'
        )
        average_line = alt.Chart(combined_winter_flow).mark_area(opacity=0.4,color = 'black').encode(
        x=alt.X('water_year:O',title=''),
        y=alt.Y('avg_flow_avg:Q', title='')
        ).properties(
        width=600,
        height=800
        )
        min_line = alt.Chart(combined_winter_flow).mark_area(opacity=0.6,color = 'blue').encode(
        x=alt.X('water_year:O',title=''),
        y=alt.Y('avg_flow_min:Q', title='')
        ).properties(
        width=600,
        height=800,
        

        )
        min_line_avg = alt.Chart(combined_winter_flow).mark_line(color = 'blue').encode(
        x=alt.X('water_year:O',title=''),
        y=alt.Y('average_min_flow_winter:Q', title='')
        ).properties(
        width=600,
        height=800,
        )
        min_labels = alt.Chart(combined_winter_flow).mark_text(
            align='left',
            dx=3,  # Adjust horizontal position
            dy=-10  # Adjust vertical position
        ).encode(
            x=alt.X('water_year:O',title=''),
            y=alt.Y('average_min_flow_winter:Q', title=''),
            text=alt.Text('average_min_flow_winter:Q', format='.0f')
        )
        avg_line_avg = alt.Chart(combined_winter_flow).mark_line(color = 'black').encode(
        x=alt.X('water_year:O',title=''),
        y=alt.Y('average_flow_winter:Q', title='')
        ).properties(
        width=600,
        height=800,
        )
        
        line = average_line + min_line + avg_points + min_points+ min_line_avg + avg_line_avg 
        st.altair_chart(line, use_container_width=True)

        #average minimum flow in winter across all years
        st.divider()
        st.header("Winter Monthly Flow Analysis Summary")
        st.subheader(f"The average flow during winter months across all years is {average_winter_flow:.0f} cfs - shown as the black line on the chart above.")
        
        st.subheader(f"The average minimum flow during winter months across all years is {average_min_winter_flow:.0f} cfs - shown as the blue line on the chart above.")
        st.divider()
        if min_analysis_df.empty:
            st.header(f"No flow events exist below the minimum flow threshold of {min_threshold} cfs, skipping analysis.")
        else:
            min_analysis_df.columns = ['year', 'Total Days Below Min Threshold', 'Years After Previous', 'Average Flow Below Min Threshold', 'Max Flow Below Min Threshold', 'Min Flow Below Min Threshold']
            
            st.title(f"Threshold Analysis of Gage Data - Minimum Flow Threshold ({min_threshold} cfs)")
            #drop na values from df
            try:
                spring_df = df[df['season'] == 'Spring']
                summer_df = df[df['season'] == 'Summer']
                fall_df = df[df['season'] == 'Fall']
                winter_df = df[df['season'] == 'Winter']
                #calculate percent of days in winter_df where flow is below trout_threshold
                #number of days in winter below the min_threshold 
                winter_below_num_days = winter_df[winter_df['avg_flow'] < min_threshold].shape[0]
                winter_below_threshold = (winter_df[winter_df['avg_flow'] < min_threshold].shape[0] / winter_df.shape[0]) * 100
                spring_below_threshold = (spring_df[spring_df['avg_flow'] < min_threshold].shape[0] / spring_df.shape[0]) * 100
                summer_below_threshold = (summer_df[summer_df['avg_flow'] < min_threshold].shape[0] / summer_df.shape[0]) * 100
                fall_below_threshold = (fall_df[fall_df['avg_flow'] < min_threshold].shape[0] / fall_df.shape[0]) * 100
            
                #st.markdown(f'<h2 style="color:black;">Seasonal Analysis of Flow Below Minimum Threshold ({min_threshold} cfs)</h2>', unsafe_allow_html=True)
                st.write(f"##### Percentage of Days Below {min_threshold} cfs by Season:")
                if winter_below_threshold > 10:
                    st.markdown(f'<h3 style="color:red;">Winter: {winter_below_threshold:.2f}%</h3>', unsafe_allow_html=True)
                    st.write("The total number of days in winter below the minimum threshold is " + str(winter_below_num_days) + ". There are " + str(len(winter_df)) + " total days in winter over the period of analysis.")
                    st.write("The number of days in winter where flow is below the minimum threshold is greater than 10%. This may indicate that the stream is not suitable for aquatic life during winter months.")
                else:
                    st.write(f"Winter: {winter_below_threshold:.2f}%")
                st.write(f"Spring: {spring_below_threshold:.2f}%")
                st.write(f"Summer: {summer_below_threshold:.2f}%")
                st.write(f"Fall: {fall_below_threshold:.2f}%")
                st.divider()
                st.header("Yearly Summary Data")
                st.write(f"##### Summary of Average Daily Flow Data Below {min_threshold} cfs by Year:")

                summary_df = generate_summary_df(min_analysis, min_threshold)

                with st.expander("Flow Below Minimum Threshold Data - Raw Data"):
                    st.dataframe(summary_df)
                #create streamlit bar chart for summary df data
                #st.subheader(f"Bar Chart of Total Days per Year Below {min_threshold} cfs")
                st.markdown(f'<h3 style="color:#ffaa00;">Bar Chart of Total Days per Year Below {min_threshold} cfs</h3>', unsafe_allow_html=True)
                with st.expander(f"Flow Below Minimum Threshold ({min_threshold} cfs) Yearly Summary - Figure"):
                    st.bar_chart(summary_df[f"Total Days Below {min_threshold} cfs"], use_container_width=True, color="#ffaa00")
            except Exception as e:
                st.write("Error subsetting data by season:", e, ". Try using a begin analysis date within the date range of the gage data.")
        
        #df_group = subset_by_season(df)

        #generate matplotlib figure for spring data
        #st.subheader("Seasonal Flow Data:")
        
        #for season, season_df in zip(["Spring", "Summer", "Fall", "Winter"], df_group):
            #plot the seasonal data
        #    with st.expander(f"{season} Average Annual Flow Data"):
        #        fig = plot_seasonal_data(season_df, usgs_station_id, season)
        #        st.pyplot(fig)
    
    
        
    
        #st.title(f"Threshold Analysis of Gage Data - Stable Flow Threshold ({trout_threshold} cfs)")
        
        #subset df dataframe by winter in the season column
        #spring_df = df[df['season'] == 'Spring']
        ##summer_df = df[df['season'] == 'Summer']
        #fall_df = df[df['season'] == 'Fall']
        #winter_df = df[df['season'] == 'Winter']
        
       
        #calculate percent of days in winter_df where flow is below trout_threshold
        #winter_below_threshold = (winter_df[winter_df['avg_flow'] < trout_threshold].shape[0] / winter_df.shape[0]) * 100
        #spring_below_threshold = (spring_df[spring_df['avg_flow'] < trout_threshold].shape[0] / spring_df.shape[0]) * 100
        #summer_below_threshold = (summer_df[summer_df['avg_flow'] < trout_threshold].shape[0] / summer_df.shape[0]) * 100
        #fall_below_threshold = (fall_df[fall_df['avg_flow'] < trout_threshold].shape[0] / fall_df.shape[0]) * 100
    
        #st.markdown(f'<h2 style="color:black;">Seasonal Analysis of Flow Below Stable Threshold ({trout_threshold} cfs)</h2>', unsafe_allow_html=True)
        #st.write(f"##### Percentage of Days Below {trout_threshold} cfs by Season:")
        #if winter_below_threshold > 50:
        #    st.markdown(f'<h3 style="color:red;">Winter: {winter_below_threshold:.2f}%</h3>', unsafe_allow_html=True)
        #    st.write("The number of days in winter where flow is below the stable threshold is greater than 50%. This may indicate that the stream is not suitable for trout during winter months.")
        #else:
        #    st.write(f"Winter: {winter_below_threshold:.2f}%")
        #st.write(f"Spring: {spring_below_threshold:.2f}%")
        #st.write(f"Summer: {summer_below_threshold:.2f}%")
        #st.write(f"Fall: {fall_below_threshold:.2f}%")
        #write the yearly analysis
        #st.subheader("Yearly Summary Data:")
        #st.write(f"##### Summary of Average Daily Flow Data Below {trout_threshold} cfs by Year:")

        #summary_df = generate_summary_df(trout_analysis, trout_threshold)

        
        #st.dataframe(summary_df)
        #create streamlit bar chart for summary df data
  
        #st.markdown(f'<h3 style="color:blue;">Bar Chart of Total Days per Year Below {trout_threshold} cfs</h3>', unsafe_allow_html=True)
        #with st.expander(f"Flow Below Stable Threshold ({trout_threshold} cfs) Yearly Summary - Figure"):
        #    st.bar_chart(summary_df[f"Total Days Below {trout_threshold} cfs"], use_container_width=True)

        
   
    

        

       
   
  
    