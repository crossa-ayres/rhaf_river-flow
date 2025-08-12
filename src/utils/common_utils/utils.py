import pandas as pd
import os
import wget
import matplotlib.pyplot as plt
import streamlit as st

def download_usgs_data(site_id, begin_year):
    """
    Downloads the peak flow data from the given URL and returns the file path.
    
    Args:
        url (str): The URL to download the peak flow data from.
        
    Returns:
        str: The path to the downloaded file.
    """
    try:
        yesterday = pd.Timestamp.now() - pd.Timedelta(days=1)
        yesterday_str = yesterday.strftime('%Y-%m-%d')
        
        url = f"https://waterdata.usgs.gov/nwis/dv?cb_00060=on&format=rdb&site_no={site_id}&legacy=&referred_module=sw&period=&begin_date={begin_year}-01-01&end_date={yesterday_str}"
        if not os.path.exists("data/temp"):
            os.makedirs("data/temp")
        file_path = wget.download(url,os.path.join("data/temp","flow_data.txt"))
        
        
        return file_path
    except Exception as e:
        st.error(f"Error downloading peak flow data: {e}")
       
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
        
        os.remove(file_path)  # Remove the downloaded file after loading
        return df
    except Exception as e:
        st.error(f"Error loading peak flow data: {e}")
       
        return None
    

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
    
    fig, ax = plt.subplots(figsize=(10, 6))
    season_df.set_index('year').T.plot(ax=ax, marker='o', title=f'{season} Average Daily Flow: Gage {usgs_station_id}', legend=False)
    plt.xlabel('Day')
    plt.ylabel('Flow (cfs)')
    #set log axis for y-axis
    ax.set_yscale('log')  # Set y-axis to logarithmic scale
    #add grid lines to the plot
    plt.grid(True)
    return fig

