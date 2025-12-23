import streamlit as st
import pandas as pd
from PIL import Image
from datetime import datetime

st.set_page_config(layout='wide')
from utils.rate_change.rateChange_utils import rate_change_main


flow_derivative_df = None
upload_type = None
usgs_station_id = None
begin_year = None
pf_threshold = None
end_year = None
uploaded_file = None
date_col = None
flow_col = None
data = None


image = Image.open('./src/Images/roc.png')
st.image(image, use_container_width=True)
logo = Image.open('./src/Images/logo.png')
st.sidebar.image(logo)
st.sidebar.divider()
st.divider()
st.title("Rate of Change Data Analysis")
st.subheader("This application allows the user to evaluate river health on the basis of flow rate of change. Flow data used for this analysis can either be downloaded from the USGS website or manually uploaded as a txt file.")

st.markdown("##### The application requires the following inputs:")
st.markdown("- **USGS Station ID**")
st.markdown("- **Begin Analysis On (year)**: The year from which to start the analysis. If the Download Data option is selected, the application will download data from the USGS website starting from this year.")

st.markdown("- **Number of Outliers to Display**: This application will indentify many outliers over the period of record for the gage. " \
"The user can specify how many of the top outliers (greatest magnitude of the derivative) to display in the analysis. The default value is 10, but it can be adjusted based on the user's needs.")
st.divider()

st.sidebar.title("Input Parameters")
#add checkbox to determine if the user wants to manually upload data or allow the tool to download it from the USGS website

if st.sidebar.checkbox("**Download data from USGS website**", value=False, key="download_data"):
    usgs_station_id = st.sidebar.text_input("USGS Station ID", value="06752260")
    begin_year = st.sidebar.text_input("Begin Analysis On (year)", value="2020")
    number_outliers = st.sidebar.number_input("Number of Outliers to Display", min_value=1, value=3)
    upload_type = "downloaded"

elif st.sidebar.checkbox("**Manually upload peak flow data**", value=False, key="upload_data"):
    uploaded_file = st.sidebar.file_uploader("Upload Peak Flow Data csv file", type=["csv"])
    number_outliers = st.sidebar.number_input("Number of Outliers to Display", min_value=1, value=3)
    upload_type = "uploaded"
    
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

# Initialize the persistent state variable
if "sidebar_btn_clicked" not in st.session_state:
    st.session_state.sidebar_btn_clicked = False

# Function to update state when button is clicked
def click_sidebar_button():
    st.session_state.sidebar_btn_clicked = True

# Sidebar button with callback
st.sidebar.button(
    "Analyze Rate of Change of Flow Data",
    on_click=click_sidebar_button
)

# Main app logic

#st.write(f"Analyzing peak flow data for USGS Station ID: {usgs_station_id}, starting in {begin_year}, Mean Daily Flow Threshold: {pf_threshold} cfs")st.sidebar.button("Analyze Peak Flow Data"):

if st.session_state.sidebar_btn_clicked: 
    
    if upload_type == "uploaded" and uploaded_file is not None:
        data = pd.read_csv(uploaded_file,  on_bad_lines='skip', header = 0)
        

        col1, col2 = st.columns(2)
        with col1:
            date_column = st.info("Please select the column that contains the date information.")
            date_col = st.selectbox("Select Date Column", options=data.columns, placeholder=None) 

        with col2:
            flow_column = st.info("Please select the column that contains the average flow information.")
            flow_col = st.selectbox("Select Average Flow Column", options=data.columns, placeholder=None)

        if st.button("Submit Columns"):
            flow_derivative_df = rate_change_main(usgs_station_id, begin_year,data,date_col, flow_col, upload_type)            
            begin_year = flow_derivative_df['date'].dt.year.min()

    elif upload_type == "downloaded":
        flow_derivative_df = rate_change_main(usgs_station_id, begin_year,data,date_col, flow_col, upload_type)

    if flow_derivative_df is not None:
        st.write(f"Analyzing base flow data for USGS Station ID: {usgs_station_id}, analysis starting in {begin_year}")
        st.divider()
    
        
        flow_derivative_df['date'] = pd.to_datetime(flow_derivative_df['date'], errors='coerce')
        flow_derivative_df['datetime'] = flow_derivative_df['date']
        #subset flow_derivative_df to only include dates between august 1 and november 1
        

        
        
        #find the last year data was collected
        last_year = str(flow_derivative_df['date'].max())
        last_year = last_year.split(" ")[0]
        st.write(f"### Gage ID {usgs_station_id} contains data up until {last_year}")
        st.divider()
        st.write("### Average Daily Flow Data with Rate of Change and Outliers Identified")
        with st.expander("View Average Daily Flow Data with Rate of Change and Outliers Identified"):
            st.write(flow_derivative_df)
        st.header(f"Average daily flow data for gage {usgs_station_id}")
        st.line_chart(flow_derivative_df.set_index('date')['avg_flow'],x_label="Date", y_label="Average Daily Flow (cfs)", use_container_width=True)
        st.divider()
        st.header("Flow Rate of Change")
        st.subheader("Flow rate of change represents the day-to-day change in average flow across the period of gage record. Rate of change outliers are identified " \
        "as those that are more than 3 standard deviations from the median day-to-day rate of change across the period of record for the gage. Outliers are only identified between August 1 and October 31")
        st.line_chart(flow_derivative_df.set_index('date')['flow_derivative'],x_label="Date", y_label="Flow Derivative", use_container_width=True)
        #extract the date associated with the outliers
        flow_derivative_df = flow_derivative_df[(flow_derivative_df['date'].dt.month >= 8) & (flow_derivative_df['date'].dt.month <= 10)]
        outliers = flow_derivative_df[flow_derivative_df['is_outlier']]
        if not outliers.empty:
            st.divider()
            st.header("Outliers Identified in Flow Rate of Change")
            with st.expander("View All Outliers Identified in Flow Rate of Change"):
                st.write(outliers[['date', 'avg_flow']])
            
            #identify the top n number of outliers
            top_outliers = outliers.nlargest(number_outliers, 'flow_derivative')
            st.write(f"### Top {number_outliers} Outliers Identified in Flow Rate of Change")
            with st.expander(f"View Top {number_outliers} Outliers Identified in Flow Rate of Change"):
                st.write(top_outliers[['date', 'avg_flow', 'flow_derivative']])
            #find the index in df of the top outliers and plot 5 days before and after the outlier
            st.divider()
            st.header("Rate of Change Outlier Analysis")
            st.write("The following plots show the average daily flow data for the 15 days before and after each outlier identified in flow rate of change.")
            for index, row in top_outliers.iterrows():
                date_current = row['date']
                st.write(f"### Outlier Identified on {date_current}")
                #get the 5 days before and after the outlier
                start_date = date_current - pd.Timedelta(days=15)
                end_date = date_current + pd.Timedelta(days=15)
                outlier_data = flow_derivative_df[(flow_derivative_df['date'] >= start_date) & (flow_derivative_df['date'] <= end_date)]
                with st.expander(f"{date_current} +/- 15 Days: Average Daily Flow Data"):
                    st.line_chart(outlier_data.set_index('date')['avg_flow'],x_label="Date", y_label="Average Daily Flow (cfs)", use_container_width=True)
                    st.line_chart(outlier_data.set_index('date')['flow_derivative'],x_label="Date", y_label="Daily Rate of Change", use_container_width=True)
                    #day = date.datetime.day
                    st.write(f"### Insights for Outlier on {date_current}")
                    
                    before_outlier = flow_derivative_df[(flow_derivative_df['datetime'] >= start_date) & (flow_derivative_df['datetime'] < date_current)]
                    after_outlier = flow_derivative_df[(flow_derivative_df['datetime'] > date_current) & (flow_derivative_df['datetime'] <= end_date)]
                    avg_before = before_outlier['flow_derivative'].mean()
                    avg_after = after_outlier['flow_derivative'].mean()
                    st.write(f"- Average Rate of Change 15 Days Before Outlier: {avg_before:.2f}")
                    st.write(f"- Average Rate of Change 15 Days After Outlier: {avg_after:.2f}")
                    try:
                        if avg_after > avg_before:
                            st.write("- Observation: The average flow rate of change increased after the outlier event, indicating a potential shift in flow dynamics.")
                        else:
                            st.write("- Observation: The average flow rate of change decreased after the outlier event, suggesting a return to previous flow patterns.")
                    except:
                        st.write("- Not enough data available to calculate 15 Days before and after the outlier.")
                    #plot the before_outlier and after_outlier data
                    st.subheader("Rate of Change Analysis Before and After Outlier")
                    
                    st.write("#### Average Daily Flow Data 15 Days Before Outlier")
                    st.line_chart(before_outlier.set_index('date')['avg_flow'],x_label="Date", y_label="Average Daily Flow (cfs)", use_container_width=True)
                    #st.write("#### Flow Derivatives 15 Days Before Outlier")
                    #st.line_chart(before_outlier.set_index('date')['flow_derivative'],x_label="Date", y_label="Daily Rate of Change", use_container_width=True)
                    st.write("#### Average Daily Flow Data 15 Days After Outlier")
                    st.line_chart(after_outlier.set_index('date')['avg_flow'],x_label="Date", y_label="Average Daily Flow (cfs)", use_container_width=True)
                    #st.write("#### Flow Derivatives 15 Days After Outlier")
                    #st.line_chart(after_outlier.set_index('date')['flow_derivative'],x_label="Date", y_label="Daily Rate of Change", use_container_width=True)

            
                
            

        
        else:
            st.write("No outliers detected in flow derivatives.")
   