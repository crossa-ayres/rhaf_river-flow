import pandas as pd
import os
import requests
import matplotlib.pyplot as plt


import streamlit as st
import folium
from streamlit_folium import folium_static


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
        file_path = requests.get(url)
        
        #save the file to the temp directory
        with open(os.path.join("data/temp","flow_data.txt"), 'wb') as f:
            f.write(file_path.content)
        

        file_path = os.path.join("data/temp","flow_data.txt")
        
        info_path = download_site_coords(site_id)
        
        return file_path, info_path
    except Exception as e:
        st.error(f"Error downloading peak flow data: {e}")
       
        return None
def download_site_coords(site_id):
    """
    Downloads the site coordinates from the USGS website.
    
    Args:
        site_id (str): The USGS site ID.
        
    Returns:
        dict: A dictionary containing the site coordinates.
    """
    information_url = f"https://waterdata.usgs.gov/nwis/inventory/?site_no={site_id}&agency_cd=USGS"
    info_path = requests.get(information_url)
    with open(os.path.join("data/temp","info_data.txt"), 'wb') as f:
        f.write(info_path.content)
    info_path = os.path.join("data/temp","info_data.txt")
    return info_path
    
def manual_upload_daily_flow_data(uploaded_file):
    """
    Loads the peak flow data from an uploaded file into a pandas DataFrame.
    
    Args:
        uploaded_file (UploadedFile): The uploaded file containing peak flow data.
        
    Returns:
        pd.DataFrame: The loaded peak flow data.
    """
    try:
        
        data = pd.read_csv(uploaded_file, delimiter='\t', on_bad_lines='skip', header = None)
        
        data.columns = ['temp']
        #define the temp column as a string
        data2 = pd.read_csv(uploaded_file, delimiter=' ', on_bad_lines='skip',skiprows=29, header = None)
        st.write("this is data ",data2)
        row = data.iloc[13]
        #convert the row to a string and split it by tab
        row = str(row[0])
        
        
        usgs_station_id = row.split(' ')
        #remove empty strings from the list
        usgs_station_id = [x for x in usgs_station_id if x]
        usgs_station_id = usgs_station_id[2]
        
        
        df = load_flow_data(uploaded_file)
        st.write(df)
        info_path = download_site_coords(usgs_station_id)
        
        return df,info_path, usgs_station_id
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

def extract_site_info(info_path):
    """
    Extracts site information from the info file.
    
    Args:
        info_path (str): The path to the info file.
        
    Returns:
        dict: A dictionary containing site information.
    """
    #try:
    with open(info_path, 'r') as f:
        lines = f.readlines()
    site_info = {}
    for line in lines:
        #find lines that contain latitude and longitude
        if "latitude" in line.lower() or "longitude" in line.lower():
            parts = line.strip().split(' ')
            for part in parts:
                if part == "" or part == " ":
                    parts.remove(part)
            
            
            latitude = parts[1]
            latitude = latitude.replace(',', ' ').replace('&#176', ' ').replace(';', ' ').replace("'", ' ').replace('"', ' ')
            
            latitude = latitude.split(" ")
            
            decimal_lat = float(latitude[0]) + (float(latitude[2]) / 60) + (float(latitude[3])/ 3600)
            longitude = parts[4]
            longitude = longitude.replace(',', ' ').replace('&#176', ' ').replace(';', ' ').replace("'", ' ').replace('"', ' ')
            longitude = longitude.split(" ")
            
            decimal_long = float(longitude[0]) + (float(longitude[2]) / 60) + (float(longitude[3])/ 3600)
            location_df = pd.DataFrame({'latitude': [decimal_lat], 'longitude': [decimal_long*-1]})
            return location_df
            
                
def create_location_plot(info_path, site_id):
    location_df = extract_site_info(info_path)
    attr = (
    '&copy; <a href="https://www.stadiamaps.com/" target="_blank">Stadia Maps</a> &copy; <a href="https://openmaptiles.org/" target="_blank">OpenMapTiles</a> &copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> '
    'contributors, &copy; <a href="https://cartodb.com/attributions">CartoDB</a>'
)
    tiles = 'https://tiles.stadiamaps.com/tiles/alidade_satellite/{z}/{x}/{y}{r}.jpg'
    
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
    fig, ax = plt.subplots(figsize=(10,4), )
    season_df.set_index('year').T.plot(ax=ax, style=styles,linewidth=1,markersize=5, title=f'{season} Average Daily Flow: Gage {usgs_station_id}', legend=True)
    plt.xlabel('Day', fontsize=8)
    ax.set_facecolor("#999997")  # Set the background color of the plot area
    plt.minorticks_on()
    plt.title(f'{season} Average Daily Flow: Gage {usgs_station_id}', fontsize=10)
  
    plt.ylabel('Average Daily Flow (cfs)', fontsize=8)
    plt.legend(ncol=3, title = "Year")
    
    #add grid lines to the plot
    #ax.grid(which='major', linestyle='-', linewidth=0.35, color='black', alpha = 0.7)  # Major gridlines
    #ax.grid(which='minor', linestyle=':', linewidth=0.25, color='gray', alpha = 0.7)  # Minor gridlines
    return fig

