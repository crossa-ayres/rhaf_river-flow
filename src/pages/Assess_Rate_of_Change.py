import streamlit as st
import pandas as pd
from PIL import Image
st.set_page_config(layout='wide')
from utils.rate_change.rateChange_utils import rate_change_main

image = Image.open(r'src\Images\roc.jpg')
st.image(image, use_container_width=True)
 
st.title("Rate of Change Data Analysis")
st.subheader("This application allows the user to evaluate river health on the basis of flow rate of change. Flow data used for this analysis can either be downloaded from the USGS website or manually uploaded as a txt file.")

st.markdown("##### The application requires the following inputs:")
st.markdown("- USGS Station ID")
st.markdown("- Begin Year: The year from which to start the analysis. If the Download Data option is selected, the application will download data from the USGS website starting from this year.")

st.markdown("- Number of Outliers to Display")

st.sidebar.header("Input Parameters")
#add checkbox to determine if the user wants to manually upload data or allow the tool to download it from the USGS website

if st.sidebar.checkbox("Download data from USGS website", value=False, key="download_data"):
    usgs_station_id = st.sidebar.text_input("USGS Station ID")
    begin_year = st.sidebar.text_input("Begin Year")
    number_outliers = st.sidebar.number_input("Number of Outliers to Display", min_value=1, value=10)

elif st.sidebar.checkbox("Manually upload peak flow data", value=False, key="upload_data"):
    uploaded_file = st.sidebar.file_uploader("Upload Peak Flow Data txt file", type=["txt"])
    
st.sidebar.markdown("### Note:")
st.sidebar.markdown("The application will download mean daily flow data from the USGS website and analyze it based on the specified parameters.")

if st.sidebar.button("Analyze Rate of Change of Flow Data"):

    st.write(f"Analyzing base flow data for USGS Station ID: {usgs_station_id}, analysis starting in {begin_year}")
    
    flow_derivative_df = rate_change_main(usgs_station_id, begin_year)
    flow_derivative_df['datetime'] = flow_derivative_df['date']
    flow_derivative_df['date'] = pd.to_datetime(flow_derivative_df['date']).dt.date
    
    if not flow_derivative_df.empty:
        #find the last year data was collected
        last_year = str(flow_derivative_df['date'].max())
        last_year = last_year.split(" ")[0]
        st.write(f"### Gage ID {usgs_station_id} contains data up until {last_year}")
        st.write("### Average Daily Flow Data with Derivatives and Outliers Identified")
        st.write(flow_derivative_df)
        st.header(f"Average daily flow data for gage {usgs_station_id}")
        st.line_chart(flow_derivative_df.set_index('date')['avg_flow'],x_label="Date", y_label="Average Daily Flow (cfs)", use_container_width=True)

        st.header("Flow Derivatives")
        st.subheader("Flow derivatives represent the day-to-day change in average flow across the period of gage record. Derivative outliers are identified " \
        "as those that are more than 3 standard deviations from the median day-to-day rate of change across the period of record for the gage.")
        st.line_chart(flow_derivative_df.set_index('date')['flow_derivative'],x_label="Date", y_label="Flow Derivative", use_container_width=True)
        #extract the date associated with the outliers
        outliers = flow_derivative_df[flow_derivative_df['is_outlier']]
        if not outliers.empty:
            st.header("Outliers Identified in Flow Derivatives")
            st.write(outliers[['date', 'avg_flow']])
            
            #identify the top n number of outliers
            top_outliers = outliers.nlargest(number_outliers, 'flow_derivative')
            st.write(f"### Top {number_outliers} Outliers Identified in Flow Derivatives")
            st.write(top_outliers[['date', 'avg_flow', 'flow_derivative']])
            #find the index in df of the top outliers and plot 5 days before and after the outlier
            st.subheader("Flow Derivative Outlier Analysis")
            st.write("The following plots show the average daily flow data for the 60 days before and after each outlier identified in flow derivatives.")
            for index, row in top_outliers.iterrows():
                date = row['date']
                st.write(f"### Outlier Identified on {date}")
                #get the 5 days before and after the outlier
                start_date = date - pd.Timedelta(days=60)
                end_date = date + pd.Timedelta(days=60)
                outlier_data = flow_derivative_df[(flow_derivative_df['date'] >= start_date) & (flow_derivative_df['date'] <= end_date)]
                with st.expander(f"{date} +/- 60 Days: Average Daily Flow Data"):
                    st.line_chart(outlier_data.set_index('date')['avg_flow'],x_label="Date", y_label="Average Daily Flow (cfs)", use_container_width=True)
                    st.line_chart(outlier_data.set_index('date')['flow_derivative'],x_label="Date", y_label="Flow Derivative", use_container_width=True)
                    year = date.year
                    st.write(f"### Insights for Outlier on {date}")
                    
                    before_outlier = flow_derivative_df[(flow_derivative_df['datetime'].dt.year >= year - 5) & (flow_derivative_df['datetime'].dt.year < year)]
                    after_outlier = flow_derivative_df[(flow_derivative_df['datetime'].dt.year > year) & (flow_derivative_df['datetime'].dt.year <= year + 5)]
                    avg_before = before_outlier['flow_derivative'].mean()
                    avg_after = after_outlier['flow_derivative'].mean()
                    st.write(f"- Average Flow Derivative 5 Years Before Outlier: {avg_before:.2f}")
                    st.write(f"- Average Flow Derivative 5 Years After Outlier: {avg_after:.2f}")
                    try:
                        if avg_after > avg_before:
                            st.write("- Observation: The average flow derivative increased after the outlier event, indicating a potential shift in flow dynamics.")
                        else:
                            st.write("- Observation: The average flow derivative decreased after the outlier event, suggesting a return to previous flow patterns.")
                    except:
                        st.write("- Not enough data available to calculate 5 years before and after the outlier.")
                    #plot the before_outlier and after_outlier data
                    st.subheader("Flow Derivative Analysis Before and After Outlier")
                    
                    st.write("#### Average Daily Flow Data 5 Years Before Outlier")
                    st.line_chart(before_outlier.set_index('date')['avg_flow'],x_label="Date", y_label="Average Daily Flow (cfs)", use_container_width=True)
                    st.write("#### Flow Derivatives 5 Years Before Outlier")
                    st.line_chart(before_outlier.set_index('date')['flow_derivative'],x_label="Date", y_label="Flow Derivative", use_container_width=True)
                    st.write("#### Average Daily Flow Data 5 Years After Outlier")
                    st.line_chart(after_outlier.set_index('date')['avg_flow'],x_label="Date", y_label="Average Daily Flow (cfs)", use_container_width=True)
                    st.write("#### Flow Derivatives 5 Years After Outlier")
                    st.line_chart(after_outlier.set_index('date')['flow_derivative'],x_label="Date", y_label="Flow Derivative", use_container_width=True)

            
                
            

        
        else:
            st.write("No outliers detected in flow derivatives.")
    else:
        st.warning("No data available for the selected parameters.")