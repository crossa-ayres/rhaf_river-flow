
import os
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
import folium
from streamlit_folium import folium_static
import re
from utils.common_utils.data_processing import download_usgs_data, extract_site_info, download_site_coords





def water_year_flows(df):
    if df is not None:
        
        df['water_year'] = df['date'].apply(lambda x: x.year + 1 if x.month >= 10 else x.year)
        df['day_of_waterYear'] = df['date'].apply(lambda x: (x - pd.Timestamp(year=x.year if x.month >= 10 else x.year - 1, month=10, day=1)).days + 1)
        return df
    else:
        return pd.DataFrame(columns=['date', 'avg_flow'])
    
def return_waterYr_dict():
    return {1: 'January', 2: 'February', 3: 'March', 4: 'April', 5: 'May', 6: 'June', 7: 'July', 8: 'August', 9: 'September', 10: 'October', 11: 'November', 12: 'December'}

def clean_manual_date_column(df, date_col):
    """
    Cleans and converts a date column to datetime format.
    
    Args:
        date_series (pd.Series): The date column to clean.
        
    Returns:
        pd.Series: The cleaned date column in datetime format.
    """
    
    #remove any '=' characters from the date column
    
    df[f"{date_col}"] = df[f"{date_col}"].astype(str).str.replace('"', '', regex=True)
    df[f"{date_col}"] = df[f"{date_col}"].astype(str).str.replace('=', '', regex=True)
    df[f"{date_col}"] = pd.to_datetime(df[f"{date_col}"], errors='coerce')

    # Remove time part, keeping only the date
    df[f"{date_col}"] = df[f"{date_col}"].dt.date
    
    return df

def remove_nan_rows(df, col_name):
    """
    Removes rows with NaN values in the specified column.
    
    Args:
        df (pd.DataFrame): The DataFrame to clean.
        col_name (str): The column name to check for NaN values.
        
    Returns:
        pd.DataFrame: The cleaned DataFrame without NaN rows.
    """
    df_cleaned = df.dropna(subset=[col_name])
    return df_cleaned
    
    
def manual_upload_daily_flow_data(data, date_col, flow_col):
    """
    Loads the peak flow data from an uploaded file into a pandas DataFrame.
    
    Args:
        uploaded_file (UploadedFile): The uploaded file containing peak flow data.
        
    Returns:
        pd.DataFrame: The loaded peak flow data.
    """
    try:
        
        
        
        df = data[[date_col, flow_col]]
        df = clean_manual_date_column(df, date_col)
        df = remove_nan_rows(df, flow_col)
        

        
        
        df.columns = ['date', 'avg_flow']
        df['date'] = pd.to_datetime(df['date'])
        df['avg_flow'] = pd.to_numeric(df['avg_flow'], errors='coerce')
        #add column contining just the year
        df['year'] = df['date'].dt.year
        df['month'] = df['date'].dt.month
        df['day'] = df['date'].dt.day
        df.loc[(df["month"] > 3) & (df["month"] < 6), "season"] = "Spring"
        df.loc[(df["month"] > 5) & (df["month"] < 9), "season"] = "Summer"
        df.loc[(df["month"] > 8) & (df["month"] < 12), "season"] = "Fall"
        df.loc[(df["month"] < 4) | (df["month"] == 12), "season"] = "Winter"
        
        return df
    except Exception as e:
        st.error(f"Error loading peak flow data: {e}")
       
        return None


def load_flow_data(file_path):
    """
    Loads the peak flow data from the given file path into a pandas DataFrame.
    
    Args:
        file_path (str): The path to the peak flow data file.
        
    Returns:
        pd.DataFrame: The loaded peak flow data.
    """
    try:
        df = pd.read_csv(file_path, delimiter='\t', on_bad_lines='skip', skiprows=29, header = None)
        
        df.columns = ['agency_cd', 'site_no', 'date', 'avg_flow', 'qc']
        df['date'] = pd.to_datetime(df['date'], format='%Y-%m-%d')
        df['avg_flow'] = pd.to_numeric(df['avg_flow'], errors='coerce')
        #add column contining just the year
        df['year'] = df['date'].dt.year
        df['month'] = df['date'].dt.month
        df['day'] = df['date'].dt.day
        df.loc[(df["month"] > 3) & (df["month"] < 6), "season"] = "Spring"
        df.loc[(df["month"] > 5) & (df["month"] < 9), "season"] = "Summer"
        df.loc[(df["month"] > 8) & (df["month"] < 12), "season"] = "Fall"
        df.loc[(df["month"] < 4) | (df["month"] == 12), "season"] = "Winter"
        #add seasons to the dataframe
        
        
        return df
    except Exception as e:
        st.error(f"Error loading peak flow data: {e}")
       
        return None
    





def clean_temp_files(file_path, info_path):
    """
    Cleans up temporary files created during the download process.
    
    Args:
        file_path (str): The path to the downloaded file.
        info_path (str): The path to the info file.
    """
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
        if os.path.exists(info_path):
            os.remove(info_path)
    except Exception as e:
        st.error(f"Error cleaning up temporary files: {e}")


            
                
def create_location_plot(info_path, site_id):
    location_df = extract_site_info(info_path)
    attr = ('Tiles courtesy of the <a href="https://usgs.gov/">U.S. Geological Survey</a>')
    tiles = 'https://basemap.nationalmap.gov/arcgis/rest/services/USGSImageryTopo/MapServer/tile/{z}/{y}/{x}'
    
    m = folium.Map(location=[location_df["latitude"],location_df["longitude"]], tiles=tiles,attr = "Aerial Imagery", zoom_start=16)
    
    folium.Marker(
        [location_df["latitude"], location_df["longitude"]], popup=f"Gage {site_id} location", tooltip=f"Gage {site_id} location"
    ).add_to(m)
    
    #folium.LayerControl().add_to(m)
    st.header(f"Gage {site_id} Location")
    folium_static(m, width=3000, height=500)
            

def subset_by_season(df):
    spring_dict = {}
    summer_dict = {}
    fall_dict = {}
    winter_dict = {}
    for year in df['year'].unique():
        spring_dict[str(year)] = {}
        summer_dict[str(year)] = {}
        fall_dict[str(year)] = {}
        winter_dict[str(year)] = {}
        #subset the data for the current year
        yearly_data = df[df['year'] == year]
        #subset unique seasons in the yearly_data df
        seasons_year = yearly_data['season'].unique()
        for season in seasons_year:
            if season == 'Spring':
                spring_dict[str(year)] = yearly_data[yearly_data['season'] == season]['avg_flow'].values
            elif season == 'Summer':
                summer_dict[str(year)]= yearly_data[yearly_data['season'] == season]['avg_flow'].values
            elif season == 'Fall':
                fall_dict[str(year)] = yearly_data[yearly_data['season'] == season]['avg_flow'].values
            elif season == 'Winter':
                winter_dict[str(year)] = yearly_data[yearly_data['season'] == season]['avg_flow'].values
            
    #create a dataframe of the seasonal data.
    spring_df = pd.DataFrame.from_dict(spring_dict, orient='index').reset_index()
    spring_df.columns = ['year'] + [f'{i+1}' for i in range(spring_df.shape[1]-1)]
    
    summer_df = pd.DataFrame.from_dict(summer_dict, orient='index').reset_index()
    summer_df.columns = ['year'] + [f'{i+1}' for i in range(summer_df.shape[1]-1)]

    fall_df = pd.DataFrame.from_dict(fall_dict, orient='index').reset_index()
    fall_df.columns = ['year'] + [f'{i+1}' for i in range(fall_df.shape[1]-1)]

    winter_df = pd.DataFrame.from_dict(winter_dict, orient='index').reset_index()
    winter_df.columns = ['year'] + [f'{i+1}' for i in range(winter_df.shape[1]-1)]
    return [spring_df, summer_df, fall_df, winter_df]

def plot_seasonal_data(season_df, usgs_station_id, season):
    plt.style.use(['ggplot'])
    styles = ['-4', ':', '-+', '-o', '-', '--', '-p', '-P', '-x', '-*','-.', '-v', '-^', '-<', '->', '-1', '-8', '-s', '-H', '-X']
    fig, ax = plt.subplots(figsize=(10,4) )
    season_df.set_index('year').T.plot(ax=ax, style=styles,linewidth=1,markersize=5, title=f'{season} Average Daily Flow: Gage {usgs_station_id}', legend=True)
    plt.xlabel('Day', fontsize=8)
    ax.set_facecolor("#999997")  # Set the background color of the plot area
    plt.minorticks_on()
    plt.title(f'{season} Average Daily Flow: Gage {usgs_station_id}', fontsize=10)
  
    plt.ylabel('Average Daily Flow (cfs)', fontsize=8)
    plt.legend(ncol=3, title = "Year")
    
    return fig

def plot_waterYear_data(water_year_df, usgs_station_id):
    plt.style.use(['ggplot'])
    styles = ['-4', ':', '-+', '-o', '-', '--', '-p', '-P', '-x', '-*','-.', '-v', '-^', '-<', '->', '-1', '-8', '-s', '-H', '-X']
    fig, ax = plt.subplots(figsize=(10,4) )
   
    yearly_data = water_year_df[['water_year', 'avg_flow']]
    yearly_data.set_index('water_year').T.plot(ax=ax, style=styles,linewidth=1,markersize=5)
    plt.xlabel('Day', fontsize=8)
    ax.set_facecolor("#999997")  # Set the background color of the plot area
    plt.minorticks_on()
    plt.title(f'Average Daily Flow Across Water Years: Gage {usgs_station_id}', fontsize=10)

    plt.ylabel('Average Daily Flow (cfs)', fontsize=8)
    
    return fig

