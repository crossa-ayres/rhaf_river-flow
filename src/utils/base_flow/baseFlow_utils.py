import pandas as pd

from utils.common_utils.utils import load_flow_data,  clean_temp_files, create_location_plot
from utils.common_utils.data_processing import download_usgs_data



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
def generate_summary_df(yearly_analysis, pf_threshold):

    summary_dict = {}
    for year, analysis in yearly_analysis.items():
        summary_dict[year] = {}
        summary_dict[year][f"Total Days Below {pf_threshold} cfs"] = analysis['total_days_below_threshold']
        summary_dict[year]["Years After Previous"] = analysis['years_after_previous']
        summary_dict[year][f"Average Flow Below {pf_threshold} cfs"] = analysis['average_flow']
        summary_dict[year]["Max Flow Below Threshold"] = analysis['max_flow']
        summary_dict[year][f"Min Flow {pf_threshold} cfs"] = analysis['min_flow']

    summary_df = pd.DataFrame.from_dict(summary_dict, orient='index')
    return summary_df

def yearly_threshold_analysis(thresh_df):

    years  = thresh_df['year'].unique()
    thresh_analysis = {}
    i = 0
    for year in years:
        yearly_data = thresh_df[thresh_df['year'] == year]
        if not yearly_data.empty:
            thresh_analysis[str(year)] = {
                'total_days_below_threshold': len(yearly_data),
                'years_after_previous': year - years[i-1] if i > 0 else 0,
                'average_flow': yearly_data['avg_flow'].mean(),
                'max_flow': yearly_data['avg_flow'].max(),
                'min_flow': yearly_data['avg_flow'].min()
            }
            i += 1
    return thresh_analysis


def baseFlow_main(site_id, begin_year,trout_threshold, min_threshold):
    """
    Main function to download and load base flow data.
    
    Args:
        url (str): The URL to download the peak flow data from.
    """
    file_path, info_path = download_usgs_data(site_id, begin_year)
    if file_path:
        create_location_plot(info_path, site_id)
        df = load_flow_data(file_path)
        
        below_trout_threshold_df,below_min_threshold_df = subset_flow_below_threshold(df, trout_threshold, min_threshold)
        
        trout_analysis = yearly_threshold_analysis(below_trout_threshold_df)
        
        min_analysis = yearly_threshold_analysis(below_min_threshold_df)
        clean_temp_files(file_path, info_path)

        return df, trout_analysis, min_analysis
        
    else:
        return None