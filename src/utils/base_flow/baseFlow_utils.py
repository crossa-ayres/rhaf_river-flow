import pandas as pd
from utils.common_utils.utils import download_usgs_data, load_flow_data


def subset_flow_below_threshold(df, trout_threshold=35, min_threshold=10):
    """
    Determines the dates when the flow is above a specified threshold.
    
    Args:
        df (pd.DataFrame): The DataFrame containing peak flow data.
        threshold (float): The flow threshold to check against.
        
    Returns:
        pd.DataFrame: A DataFrame with dates when flow is above the threshold.
    """
    if df is not None:
        below_trout_threshold_df = df[df['avg_flow'] < trout_threshold]
        below_min_threshold_df = df[df['avg_flow'] < min_threshold]
        return below_trout_threshold_df[['date','year','month','day', 'avg_flow']], below_min_threshold_df[['date','year','month','day', 'avg_flow']]
    else:
        return None
    

def yearly_threshold_analysis(thresh_df):

    years  = thresh_df['year'].unique()
    thresh_analysis = {}
    i = 0
    for year in years:
        yearly_data = thresh_df[thresh_df['year'] == year]
        if not yearly_data.empty:
            thresh_analysis[year] = {
                'total_days_below_threshold': len(yearly_data),
                'years_after_previous': year - years[i-1] if i > 0 else 0,
                'average_flow': yearly_data['avg_flow'].mean(),
                'max_flow': yearly_data['avg_flow'].max(),
                'min_flow': yearly_data['avg_flow'].min()
            }
            i += 1
    return thresh_analysis


def baseFlow_main(site_id = "06752280", begin_year="2015"):
    """
    Main function to download and load base flow data.
    
    Args:
        url (str): The URL to download the peak flow data from.
    """
    file_path = download_usgs_data(site_id, begin_year)
    if file_path:
        df = load_flow_data(file_path)
        below_trout_threshold_df,below_min_threshold_df = subset_flow_below_threshold(df, trout_threshold=35, min_threshold=10)
        trout_analysis = yearly_threshold_analysis(below_trout_threshold_df)
        min_analysis = yearly_threshold_analysis(below_min_threshold_df)

        return df, trout_analysis, min_analysis
    else:
        return None