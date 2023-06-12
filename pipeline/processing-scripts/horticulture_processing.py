#imported required libraries

import pandas as pd
import os
import numpy as np
# import pymysql
from sqlalchemy import create_engine
from datetime import datetime



# Define a function to remove numbers from the beginning of the string
def remove_numbers(text):
        return ' '.join(text.split()[1:])

def clean_markets(directory_path):
      clean_markets = []
      for market in os.listdir(directory_path):
         for excel_file in os.listdir(directory_path+market+"/"):  
            # specify the directory where the CSV file is stored
            # directory_path = 'C:/Users/praise.taiwo/Documents/EXPLORE/INTERNSHIP/DARLLD/internship-project-2207-09/scripts/Web-scrapers/web_files/Bloemfontein_(Mangaung)_Fresh_Produce_Market_(BLO)/'
            df = pd.read_excel(directory_path+market+"/"+excel_file)
            df.head()
            # set the column names to the values in the first row
            df.columns = df.iloc[0]
            #drop first row
            df = df.drop(0)
            
            # Check if the dataframe has at least three rows
            if len(df.index) < 3:
               print(f"File {excel_file} has less than three rows of data and will be skipped")
               continue
            
            # extract the date information from the 'Unit' column
            dates = df['Unit'].str.split(', ', expand=True)[1]
            #dates = df['Unit'].str.split(', ', expand=True).apply(lambda x: x[1] if len(x) > 1 else '', axis=1)
            # add the date information as a new column in the dataframe
            df['Date'] = pd.to_datetime(dates, format='%d %B %Y')
            # Forward fill the NaT values in the Date column with the previous valid date
            df['Date'] = pd.to_datetime(df['Date'], errors='coerce').ffill()
            # Convert the dates to the desired format
            df['Date'] = df['Date'].dt.strftime('%Y-%m-%d')
            #rename 'Unit' column and remove 'kg' from rows
            df.rename({'Unit':'Unit(kg)'},axis=1,inplace=True)
            df['Unit(kg)'] = df['Unit(kg)'].str.replace('kg','')
            df['Average Price'].replace({'ý':'0'},inplace=True)
            df.rename({"Total Sales":'Total Sales(Rand)'},axis=1,inplace=True)
            df['Total Sales(Rand)'] = df['Total Sales(Rand)'].astype(str)
            #remove R
            df['Total Sales(Rand)'] = df['Total Sales(Rand)'].str.replace('R','')
            #create new column for market name
            df['Market'] = f'{market}_market'
            ##rearange column index
            #create a list of desired column order
            new_order = ['Market','Date','Product', 'Variety', 'Class', 'Size', 'Package', 'Unit(kg)',
               'Closing Price', 'High Price', 'Low Price', 'Average Price',
               'Total Sales(Rand)', 'Sales Quantity', 'Closing Stock']
            
            # reorder the columns
            df= df.reindex(columns=new_order)
            df['Product'] = df['Product'].astype(str)
            
            # Apply the function to the 'fruits' column
            df['Product'] = df['Product'].apply(remove_numbers)
            #drop null rows
            df.dropna(inplace=True)
            #change date to datetime
            df['Date'] = pd.to_datetime(df['Date'])
            df = df[(df["Variety"] != "Variety") & (df["Class"] != "Class") & 
               (df["Size"] != "Size") & (df["Package"] != "Package")
               & (df["Unit(kg)"] != "Unit") & (df["Closing Price"] != "Closing Price")
               & (df["High Price"] != "High Price") & (df["Low Price"] != "Low Price") & 
               (df["Total Sales(Rand)"] != "(Total Sales)") & (df["Sales Quantity"] != "Sales Quantity")
               & (df["Closing Stock"] != "Closing Stock")]
            
            #reset index
            df = df.reset_index(drop=True)
            #change datatype to numeric
            #df.iloc[:,6:] = df.iloc[:,6:].apply(pd.to_numeric, errors='coerce')
            df[df.columns[6:]] = df[df.columns[6:]].apply(pd.to_numeric, errors='coerce')
            df['Average Price'] = df[['High Price','Low Price']].mean(axis=1)

            # rename columns
            df.columns = ['Market','Date','Product', 'Variety', 'Class', 'Size', 'Package', 'Unit(kg)',
               'Closing_Price', 'High_Price', 'Low_Price', 'Average_Price',
               'Total_Sales(Rand)', 'Sales_Quantity', 'Closing_Stock']
            
            #extract the day, week and month from the date column
            df['Day'] = pd.to_datetime(df['Date']).dt.dayofweek
            df['Month'] = pd.to_datetime(df['Date']).dt.month
            df['Week'] = pd.to_datetime(df['Date']).dt.isocalendar().week
            
            #drop package column
            df.drop('Package',axis=1,inplace=True)
            clean_markets.append(df)
      clean_markets_data = pd.concat(clean_markets)
      return clean_markets_data

df = clean_markets(dir)


# Transmit data to RDS
# create sqlalchemy engine
engine = create_engine("mysql+pymysql://{user}:{pw}@intern-dalrrd-team9-database.ctgb19tevqci.eu-west-1.rds.amazonaws.com/{db}"
                       .format(user="explore_student",
                               pw="explore-student",
                               db="darrld_data"))


# Insert whole DataFrame into MySQL
# df.set_index("Market")
df.to_sql('horticulture_data', con = engine, if_exists = 'append', chunksize = 1000, index=False)

# Transmit data to S3 bucket
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
df.to_csv("/home/explore-student/internship-project-2207-09/pipeline/s3/horticulture/{}.csv".format(timestamp))

# create success file
with open('/home/explore-student/internship-project-2207-09/pipeline/logs/.success_horticulture_processing', 'w') as fp:
    pass