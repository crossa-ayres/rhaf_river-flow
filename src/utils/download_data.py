import pandas as pd
import os
import requests
import matplotlib.pyplot as plt





def download_usgs_data(site_id=6770):
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

        url = f"https://dwr.state.co.us/Tools/Stations/CLAFTCCO?params=DISCHRG"

        if not os.path.exists(r"C:\Users\crossa\GitHub\rhaf_river-flow\data/temp"):
            os.makedirs(r"C:\Users\crossa\GitHub\rhaf_river-flow\data/temp")
        file_path = requests.get(url)
        
        #save the file to the temp directory
        with open(os.path.join(r"C:\Users\crossa\GitHub\rhaf_river-flow\data/temp","precip.txt"), 'wb') as f:
            f.write(file_path.content)
        

        file_path = os.path.join(r"C:\Users\crossa\GitHub\rhaf_river-flow\data/temp","precip.txt")
        
        
        
        return file_path
    except Exception as e:
        print(f"Error downloading peak flow data: {e}")
       
        return None
def load_precip_data(file_path):
    """
    Loads the peak flow data from the given file path into a pandas DataFrame.
    
    Args:
        file_path (str): The path to the peak flow data file.
        
    Returns:
        pd.DataFrame: The loaded peak flow data.

        
    """
    try:
        df = pd.read_csv(file_path,sep='None' ,on_bad_lines='skip', header = None, engine='python')
        """                    
        df.columns = ['Date', 'Time', 'Inches',"Instant","None2"]
        
        df['Date'] = pd.to_datetime(df['Date'], format='mixed', errors='coerce')
        df['Instant'] = pd.to_numeric(df['Instant'], errors='coerce')
        #df = df[df['Instant'] <= 5]
        #add column contining just the year
        df['year'] = df['Date'].dt.year
        df['month'] = df['Date'].dt.month
        df['day'] = df['Date'].dt.day
        
        df.loc[(df["month"] > 3) & (df["month"] < 6), "season"] = "Spring"
        df.loc[(df["month"] > 5) & (df["month"] < 9), "season"] = "Summer"
        df.loc[(df["month"] > 8) & (df["month"] < 12), "season"] = "Fall"
        df.loc[(df["month"] < 4) | (df["month"] == 12), "season"] = "Winter"
        #add seasons to the dataframe
        
        """
        return df
    except Exception as e:
        print(f"Error loading peak flow data: {e}")
       
        return None

id = 6770
precip_data = download_usgs_data(id)
precip_df = load_precip_data(precip_data)
print(precip_df[0])
dates = []
discharge = []
for i in precip_df[0]:
    try:
        if "discharge" in i:
            gage_data = i.split(",")
            for k in gage_data:
                
                if "meas_date_time" in k:
                    date = k.split(":")[1][2:-1]
                    dates.append(date)
                if "discharge" in k and "xField" not in k:
                    try:
                        discharge.append(float(k.split(":")[1]))
                        print(k)
                        print("************************************************************")
                    except:
                        pass
    except:
        pass
          

  
print(dates)
print(discharge)