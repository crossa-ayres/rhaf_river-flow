
#def download_usgs_data(site_id, begin_year):
    """
    Downloads the peak flow data from the given URL and returns the file path.
    
    Args:
        url (str): The URL to download the peak flow data from.
        
    Returns:
        str: The path to the downloaded file.
    """
#    try:
        
#        yesterday = pd.Timestamp.now() - pd.Timedelta(days=1)
#        yesterday_str = yesterday.strftime('%Y-%m-%d')
        

 #       #https://nwis.waterdata.usgs.gov/nwis/peak?site_no=09419000&agency_cd=USGS&format=rdb
 #       #url = f"https://waterdata.usgs.gov/nwis/dv?cb_00060=on&format=rdb&site_no={site_id}&legacy=&referred_module=sw&period=&begin_date={begin_year}-01-01&end_date={yesterday_str}"
 #       url = f"https://nwis.waterdata.usgs.gov/nwis/peak?site_no={site_id}&agency_cd=USGS&format=rdb"
 #       if not os.path.exists("data/temp"):
 #           os.makedirs("data/temp")
 #       file_path = requests.get(url)
        
        #save the file to the temp directory
 #       with open(os.path.join("data/temp","flow_data.txt"), 'wb') as f:
 #           f.write(file_path.content)
        

 #       file_path = os.path.join("data/temp","flow_data.txt")
        
 #       info_path = download_site_coords(site_id)
        
 #       return file_path, info_path
 #   except Exception as e:
 #       st.error(f"Error downloading peak flow data: {e}")
       
 #       return None