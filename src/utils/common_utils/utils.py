
import os
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
import folium
import altair as alt
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
        # `download_usgs_data` writes a plain CSV with these column names. The
        # previous read parsed the legacy NWIS RDB text -- tab-delimited with a
        # 29-line header -- which the modernised API no longer returns.
        df = pd.read_csv(file_path)
        missing = {'agency_cd', 'site_no', 'date', 'avg_flow', 'qc'} - set(df.columns)
        if missing:
            raise ValueError(
                f"{file_path} is missing columns {sorted(missing)}. If this is "
                "an old flow_data.txt from the legacy RDB service, delete it "
                "and re-download."
            )
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
        #add seasons to the dataframe
        
        
        return df
    except Exception as e:
        st.error(f"Error loading peak flow data: {e}")
       
        return None
    
def manual_boxplot(df, category_col, value_col, whisker_coef=1.5):
    """
    Create a manual box-and-whisker plot in Altair with custom column names.
    
    Parameters:
        df (pd.DataFrame): Your dataset
        category_col (str): Column name for categories (nominal)
        value_col (str): Column name for numeric values
        whisker_coef (float): Whisker length multiplier (default 1.5)
    """

    # Compute stats per category
    def boxplot_stats(group):
        q1 = group.quantile(0.25)
        q3 = group.quantile(0.75)
        iqr = q3 - q1
        lower_whisker = max(group.min(), q1 - whisker_coef * iqr)
        upper_whisker = min(group.max(), q3 + whisker_coef * iqr)
        median = group.median()
        return pd.Series({
            'q1': q1,
            'q3': q3,
            'median': median,
            'lower_whisker': lower_whisker,
            'upper_whisker': upper_whisker
        })

    stats = df.groupby(category_col)[value_col].apply(boxplot_stats).reset_index()

    # Box (Q1 to Q3)
    box = alt.Chart(stats).mark_bar(size=30).encode(
        x=f'{category_col}:Q',
        y='q1:Q',
        y2='q3:Q'
    )

    # Median line
    median_line = alt.Chart(stats).mark_rule(color='black').encode(
        x=f'{category_col}:Q',
        y='median:Q'
    )

    # Whiskers
    whisker_lower = alt.Chart(stats).mark_rule().encode(
        x=f'{category_col}:Q',
        y='lower_whisker:Q',
        y2='q1:Q'
    )

    whisker_upper = alt.Chart(stats).mark_rule().encode(
        x=f'{category_col}:Q',
        y='q3:Q',
        y2='upper_whisker:Q'
    )

    # Whisker caps
    cap_lower = alt.Chart(stats).mark_tick(size=30).encode(
        x=f'{category_col}:Q',
        y='lower_whisker:Q'
    )

    cap_upper = alt.Chart(stats).mark_tick(size=30).encode(
        x=f'{category_col}:Q',
        y='upper_whisker:Q'
    )

    # Outliers
    #outliers = df.merge(stats[[category_col, 'lower_whisker', 'upper_whisker']], on=category_col)
    #outliers = outliers[(outliers[value_col] < outliers['lower_whisker']) |
    #                    (outliers[value_col] > outliers['upper_whisker'])]

    #outlier_points = alt.Chart(outliers).mark_point(color='red').encode(
    #    x=f'{category_col}:N',
    #    y=f'{value_col}:Q'
    #)

    return box + median_line + whisker_lower + whisker_upper + cap_lower + cap_upper 




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

