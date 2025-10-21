
import pandas as pd
import streamlit as st

from utils.common_utils.utils import load_flow_data, clean_temp_files,create_location_plot,manual_upload_daily_flow_data, water_year_flows, return_waterYr_dict
from utils.common_utils.data_processing import download_usgs_data



def subset_flow_above_threshold(df, pf_threshold=200):
    """
    Determines the dates when the flow is above a specified threshold.
    
    Args:
        df (pd.DataFrame): The DataFrame containing peak flow data.
        threshold (float): The flow threshold to check against.
        
    Returns:
        pd.DataFrame: A DataFrame with dates when flow is above the threshold.
    """
    if df is not None:
        above_threshold = df[df['avg_flow'] > pf_threshold]
        return above_threshold[['date','year','month','day', 'avg_flow']]
    else:
        return pd.DataFrame(columns=['date', 'avg_flow'])
    

def yearly_flow_analysis(above_thresh_df):

    years  = above_thresh_df['year'].unique()
    yearly_analysis = {}
    i = 0
    for year in years:
        yearly_data = above_thresh_df[above_thresh_df['year'] == year]
        if not yearly_data.empty:
            yearly_analysis[str(year)] = {
                'total_days_above_threshold': len(yearly_data),
                'years_after_previous': year - years[i-1] if i > 0 else 0,
                'average_flow': yearly_data['avg_flow'].mean(),
                'max_flow': yearly_data['avg_flow'].max(),
                'min_flow': yearly_data['avg_flow'].min()
            }
            i += 1
    return yearly_analysis

def annual_peak_summary(df):
    #generate a dictionary with the number of the month as the key and the month name as the value
    months_dict =return_waterYr_dict()

    if df is not None:
        annual_peaks = df.loc[df.groupby('year')['avg_flow'].idxmax()]
        annual_peaks['month_label'] = annual_peaks['month'].map(months_dict)
        annual_peaks['day'] = annual_peaks['date'].dt.strftime('%d')
        annual_peaks = annual_peaks.sort_values(by='date')
       
        return annual_peaks[['date', 'month', 'avg_flow','month_label','day']], months_dict
    else:
        return pd.DataFrame(columns=['year', 'date', 'avg_flow'])
    


def generate_summary_df(yearly_analysis, pf_threshold):

    summary_dict = {}
    for year, analysis in yearly_analysis.items():
        summary_dict[year] = {}
        summary_dict[year][f"Total Days Above {pf_threshold} cfs"] = analysis['total_days_above_threshold']
        summary_dict[year]["Years After Previous"] = analysis['years_after_previous']
        summary_dict[year][f"Average Flow Above {pf_threshold} cfs"] = analysis['average_flow']
        summary_dict[year]["Max Flow"] = analysis['max_flow']
        summary_dict[year][f"Min Flow Above {pf_threshold} cfs"] = analysis['min_flow']

    summary_df = pd.DataFrame.from_dict(summary_dict, orient='index')
    return summary_df
    
def peakFlow_main(usgs_station_id = None, begin_year="2015",end_year = "2025", pf_threshold = 200,upload_type= "downloaded",uploaded_file=None):
    """
    Main function to download and load peak flow data.
    
    Args:
        url (str): The URL to download the peak flow data from.
    """
    if upload_type == "downloaded":
        st.write("Downloading data from USGS...")
        file_path, info_path = download_usgs_data(usgs_station_id, begin_year)
        df = load_flow_data(file_path)
    elif upload_type == "uploaded":
        df,info_path, usgs_station_id = manual_upload_daily_flow_data(uploaded_file)
        
    if info_path:
        create_location_plot(info_path, usgs_station_id)
        if df is not None:
            above_thresh_df = subset_flow_above_threshold(df, pf_threshold)
            yearly_analysis = yearly_flow_analysis(above_thresh_df)
            annual_peaks,months_dict = annual_peak_summary(df)
            water_year_df = water_year_flows(df)
            
            clean_temp_files(file_path, info_path)
            return df, above_thresh_df, yearly_analysis,usgs_station_id,annual_peaks,months_dict,water_year_df
            
        else:
            st.write("No data available for the specified parameters. Please check the USGS Station ID including any leading zero's.")
            
    else:
        st.error("Failed to download peak flow data.")
        

