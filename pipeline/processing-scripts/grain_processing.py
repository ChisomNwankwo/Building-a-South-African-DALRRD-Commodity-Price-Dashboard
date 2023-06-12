#imported required libraries
import pandas as pd
import os
from sqlalchemy import create_engine
from datetime import datetime, timedelta

Sale_day_from = (datetime.today() - timedelta(days=7)).strftime("%Y,%m,%d") # format: yyyy,mm,dd
Sale_day_to = datetime.today().strftime("%Y,%m,%d") # format: yyyy,mm,dd
Folder = "/home/explore-student/internship-project-2207-09/pipeline/bash-scripts/" + "GrainData" + Sale_day_from + "_" + Sale_day_to


#specify the directory were the excel files are stored

def grain_processing(directory_path):
    '''Specify the directory path where the grain_dataset is located, This function performs cleaning and merging the whole data into a single csv.
    Variable:
    directory_path: Dir Path where grain-datasets are stored
    '''
    # Create an empty list to store the dataframes of each Excel file
    excels = []

    # Loop through all the Excel files in the specified directory
    for file_name in os.listdir(directory_path):
        if file_name.endswith(".xls"):
            path = directory_path + file_name
            excel_file = pd.read_excel(path)

            # Process datasets
            # set headers
            excel_file_header = excel_file.iloc[0] 
            excel_file = excel_file[1:]
            excel_file.columns = excel_file_header

            # Add market column
            excel_file["market"] = file_name[:-4]

            # Drop unamed column and rows with nan values
            excel_file = excel_file.dropna(subset=["Contract Type"])
            excel_file = excel_file.dropna(axis=1,how='all')

            # Add processed data to cleaned excel list
            excels.append(excel_file)

            # Extract market name from the first file and use it to name the CSV file
            if not os.path.exists('combined_csv.csv'):
                market_name = directory_path.split('/')[-2]
                csv_name = f'../Sample-Datasets/Grain/{market_name}_combined.csv'
    # Concatenate all the dataframes
    combined_df = pd.concat(excels)

    # Claening
    # Removing commas from the columns
    df_grain = combined_df.replace(',','', regex=True)

    #Leaving full stops after the decimals
    df_grain['High'] = df_grain['High'].str.extract('([0-9]+[,./]*[0-9]*)')
    df_grain['Low'] = df_grain['Low'].str.extract('([0-9]+[,./]*[0-9]*)')
    df_grain['Conts'] = df_grain['Conts'].str.extract('([0-9]+[,./]*[0-9]*)')
    df_grain['Value'] = df_grain['Value'].str.extract('([0-9]+[,./]*[0-9]*)')

    # Split "contract type" column into seperate contract date and type columns
    df_grain["Contract_Date"] = df_grain["Contract Type"].str[:9]
    df_grain["Contract_Type"] = df_grain["Contract Type"].str[10:]

    # convert the 'Contract_Date' column to datetime format
    df_grain['Contract_Date']= pd.to_datetime(df_grain['Contract_Date'])
    
    # Dropping unnecessary columns
    df_grain.drop(['Contract Type', 'Upload Date'], axis=1)

    # Rearrrange and rename columns
    df_grain = df_grain.reindex(columns=['Contract_Date', 'Contract_Type', 'market', 'Market to Market', 'Volatility','Bid',
                                    'Offer','First','Last','High','Low','Deals','Conts','Value'])
    df_grain.columns = ['contract_date', 'contract_type', 'market', 'market_to_market', 'volatility','bid',
                                    'offer','first','last','high','low','deals','conts','value']
    
    print(df_grain.describe())
    # Export to CSV
    # combined_df.to_csv(csv_name, index=False)
    print("Grain dataset cleaned successfully! \nSaved as: {}".format(csv_name))

    return df_grain

# Variable insert
df = grain_processing(Folder)


# Transmit data to RDS
# create sqlalchemy engine
engine = create_engine("mysql+pymysql://{user}:{pw}@intern-dalrrd-team9-database.ctgb19tevqci.eu-west-1.rds.amazonaws.com/{db}"
                       .format(user="explore_student",
                               pw="explore-student",
                               db="darrld_data"))


# Insert whole DataFrame into MySQL
# df.set_index("Market")
df.to_sql('grain_data', con = engine, if_exists = 'append', chunksize = 50000, index=False)

# Transmit data to S3 bucket
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
df.to_csv("/home/explore-student/internship-project-2207-09/pipeline/s3/grain/{}.csv".format(timestamp))

# # create success file
with open('/home/explore-student/internship-project-2207-09/pipeline/logs/.success_grain_processing', 'w') as fp:
    pass



# data = pd.read_csv("../Sample-Datasets/Grain/GrainData2023,1,1_2023,3,31_combined.csv")
# data['Upload Date'] = pd.to_datetime(data['Upload Date'], format='%d/%m/%Y')

# df = data["Upload Date"].value_counts().reset_index()
# df.columns = ["date","count"]
# df["date"] = pd.to_datetime(df['date'], format='%d/%m/%Y')
# df.sort_values(by=["date"])