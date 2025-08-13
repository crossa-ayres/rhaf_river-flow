
import pandas as pd
import streamlit as st

from utils.common_utils.utils import download_usgs_data, load_flow_data






    


    
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
    
def peakFlow_main(site_id = "06752280", begin_year="2015", pf_threshold = 200):
    """
    Main function to download and load peak flow data.
    
    Args:
        url (str): The URL to download the peak flow data from.
    """
    file_path = download_usgs_data(site_id, begin_year)
    if file_path:


        df= load_flow_data(file_path)
        if df is not None:
            above_thresh_df = subset_flow_above_threshold(df, pf_threshold)
            yearly_analysis = yearly_flow_analysis(above_thresh_df)
            return df, above_thresh_df, yearly_analysis
            
        else:
            st.write("No data available for the specified parameters. Please check the USGS Station ID including any leading zero's.")
            
    else:
        st.error("Failed to download peak flow data.")
        

