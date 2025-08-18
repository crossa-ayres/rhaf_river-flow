
import pandas as pd
import streamlit as st

from utils.common_utils.utils import download_usgs_data, load_flow_data, clean_temp_files, create_location_plot





def calculate_flow_dirivatives(df):
    """
    Calculates the daily flow derivatives (change in flow) for the given DataFrame.
    
    Args:
        df (pd.DataFrame): The DataFrame containing peak flow data with 'date' and 'avg_flow' columns.
        
    Returns:
        pd.DataFrame: A DataFrame with the original data and an additional column for flow derivatives.
    """
    if df is not None and 'avg_flow' in df.columns:
        df['flow_derivative'] = df['avg_flow'].diff().fillna(0)
        return df
    else:
        st.error("DataFrame is empty or does not contain 'avg_flow' column.")
        return pd.DataFrame(columns=['date', 'avg_flow', 'flow_derivative'])

def identify_derivative_outliers(df):
    """
    Identifies outliers in the flow derivatives based on statistical desiciptors of flow data.
    
    Args:
        df (pd.DataFrame): The DataFrame containing flow derivatives.
        
    Returns:
        pd.DataFrame: A DataFrame with an additional column indicating outliers.
    """
    if 'flow_derivative' in df.columns:
        #calculate median and standard deviation of flow derivatives
        median = df['flow_derivative'].median()
        std_dev = df['flow_derivative'].std()
        # Identify outliers as those that are more than 3 standard deviations from the median
        df['is_outlier'] = (df['flow_derivative'] > median + 3 * std_dev) | (df['flow_derivative'] < median - 3 * std_dev)
        # Fill NaN values in 'is_outlier' with False
        df['is_outlier'].fillna(False, inplace=True)
       
        # Return the DataFrame with the outlier information
        return df
    else:
        st.error("DataFrame does not contain 'flow_derivative' column.")
        return pd.DataFrame(columns=['date', 'avg_flow', 'flow_derivative', 'is_outlier'])

def rate_change_main(usgs_station_id, begin_year):
    """
    Main function to download and load rate change data.
    
    Args:
        usgs_station_id (str): The USGS station ID.
        begin_year (str): The year to start downloading data from.
        
    Returns:
        pd.DataFrame: A DataFrame containing the rate change data with derivatives calculated.
    """
    file_path, info_path = download_usgs_data(usgs_station_id, begin_year)

    if file_path:
        create_location_plot(info_path, usgs_station_id)
        
        df = load_flow_data(file_path)
        df = calculate_flow_dirivatives(df)
        df = identify_derivative_outliers(df)
        clean_temp_files(file_path, info_path)
        return df
    else:
        return pd.DataFrame(columns=['date', 'avg_flow', 'flow_derivative'])  # Return empty DataFrame if download fails