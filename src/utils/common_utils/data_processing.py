import os
import requests
import pandas as pd
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