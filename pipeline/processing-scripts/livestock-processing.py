import pandas as pd
import numpy as np
import datetime
from datetime import datetime
from sqlalchemy import create_engine


livestock = pd.read_csv('../livestock.csv')

#create a copy of the df
df_copy =livestock.copy()


#select rows containing 'To'
to_rows = df_copy.eq('To').any(axis=1)

#create a new row containing dates
for i, row in df_copy[to_rows].iterrows():
    all_dates = ''
    for j, val in enumerate(row):
        if val == 'From':
            all_dates += val + ' ' + str(row[j+1])
        elif val == 'To':
            all_dates += ' ' + str(row[j+1])
            break
    df_copy.loc[i, 'all_dates'] = all_dates




# Remove the last column and save it in a variable
last_col = df_copy.pop(df_copy.columns[-1])

# Insert the last column into the 13th position
df_copy.insert(10, last_col.name, last_col)

# select first 11 columns
df_copy= df_copy.iloc[:,:11]


# fill empty values in the 'all_date' column with the previous value
df_copy['all_dates'] = df_copy['all_dates'].fillna(method='ffill')

#rename first rows whoose second row is class to class
for i in range(len(df_copy)):
    if df_copy.iloc[i, 1] == 'Class':
        df_copy.at[df_copy.index[i], df_copy.columns[0]] = ' Class'

#rename first rows whoose first row is purch to pigs
for i in range(len(df_copy)):
    if df_copy.iloc[i, 0] == 'Purch':
        df_copy.at[df_copy.index[i], df_copy.columns[0]] = ' PIGS'


# rename first column with 'Cattle' to 'CattleClass'
for i in range(len(df_copy)):
    if df_copy.iloc[i, 0] == 'CATTLE':
        df_copy.at[df_copy.index[i], df_copy.columns[0]] = ' CATTLEClass'

#rename the value in the first row to 'Class' if any of the values in that row contains 'Class'

# Iterate over all rows and columns
for i, row in df_copy.iterrows():
    for j, value in row.items():
        # Check if the value contains 'Class'
        if 'Class' in str(value):
            # Change the value in the first column to 'Class'
            df_copy.at[i, df_copy.columns[0]] = 'Class'
            break  # Exit the inner loop if the value is found


#Define a function to identify the rows containing the keywords 'PIGS' and 'CLASS' 
#and return the indices where these keywords occur.

def find_indices(df):
    pigs_index = df[df['0'].str.contains('PIGS', case=False)].index
    class_index = df[df['0'].str.contains('CLASS', case=False)].index
    return pigs_index, class_index

#Use the find_indices function to get the indices for pigs and cattles/lamps/sheep.\
pigs_index, class_index = find_indices(df_copy)


cattle_index = class_index[1:]
pigs_index
start_index = pigs_index[0]
end_index = cattle_index[0]
first_pig = df_copy.iloc[start_index: end_index]

pigs_dfs = []
dfs = []
for i in range(len(pigs_index)):
    try:
        start_index = min(pigs_index, key=lambda x: abs(x - end_index))
        end_index = min(set(cattle_index) - set(range(start_index)), key=lambda x: abs(x - start_index))
        dfs.append(df_copy.iloc[start_index:end_index])
        pigs_index = [i for i in pigs_index if i not in (range(start_index, end_index))]
    except ValueError:
        break

pigs_dfs.append(first_pig)

for i, df_ in enumerate(dfs):
    exec(f"pigs_df{i+1} = df_")
    pigs_dfs.append(df_)


#turn the list of dfs to one df
pigs_df = pd.concat(pigs_dfs, ignore_index=False)

#Check and drop for duplicate row indexes
pigs_df = pigs_df[~pigs_df.index.duplicated(keep='first')]

# create a new dataframe that excludes the rows in the pigs_df
cattles_df = df_copy.drop(pigs_df.index)

#Check if the duplicate rows have been dropped
cattles_df[cattles_df.index.duplicated(keep=False)]

pigs = pigs_df.copy().reset_index(drop=True)
cattles = cattles_df.copy().reset_index(drop=True)

#Create a copy of the pigs dataframe

pigs_copy = pigs.copy()



# set the column names to the values in the first row
pigs_copy.columns = pigs_copy.iloc[0]

#drop first row
pigs_copy = pigs_copy.drop(0)

# Remove the last column and save it in a variable
last_col = pigs_copy.pop(pigs_copy.columns[-1])

# Insert the last column into the 6th position
pigs_copy.insert(6, last_col.name, last_col)

# create a list of new column names
new_cols = ['Class', 'Units', 'Avg_Mass(kg)', 'Avg_Purchase', 'Purchase_Min', 'Purchase_Max', 'Date']

# rename the first 7 columns using the new list of column names
pigs_copy.columns = new_cols + list(pigs_copy.columns[7:])

#if the first column has values that contain more than 3 characters, remove that row
pigs_copy = pigs_copy[pigs_copy.iloc[:,0].str.len()<=3]

#keep the first 7 columns
pigs_copy = pigs_copy.iloc[:, :7]

#drop rows with null values
pigs_copy.dropna(inplace=True)

#drop rows where the value in the first column starts with 'PIGS'
pigs_copy = pigs_copy[~pigs_copy['Class'].str.startswith('FOR')]


# Define a regular expression pattern to match strings with symbols or only numbers
pattern = r'^\W+|\d+$'

# Filter the rows where the first column matches the pattern
pigs_copy = pigs_copy[~pigs_copy.iloc[:,0].str.match(pattern)]

#drop rows where the value in the first column starts with 'is'
pigs_copy = pigs_copy[~pigs_copy['Class'].str.startswith('is')]

# split the 'Date' column into two new columns 'Start_Date' and 'End_Date'
pigs_copy[['From','Start_Date', 'End_Date']] = pigs_copy['Date'].str.split(' ', expand=True)

# drop the original 'Date' column
pigs_copy.drop(['Date','From'], axis=1, inplace=True)

pigs_copy.replace('#DIV/0!', np.nan, inplace=True)
pigs_copy.dropna(inplace=True)

cols = ['Units','Avg_Mass(kg)', 'Avg_Purchase', 'Purchase_Min', 'Purchase_Max']
pigs_copy[cols] = pigs_copy[cols].replace(',', '', regex=True).replace('-', np.nan, regex=True).astype(float)

#change to datetime
date_cols = ['Start_Date', 'End_Date']
pigs_copy[date_cols] = pigs_copy[date_cols].apply(pd.to_datetime, format='%Y/%m/%d')

pigs_copy.dropna(inplace=True)


cattles_copy = cattles.copy()


for index, row in cattles_copy.iterrows():
    if row['0'].startswith('Class'):
        cattles_copy.at[index, 'Type'] = 'Cattle'
    elif 'LAMB/SHEEP' in row['0']:
        cattles_copy.at[index, 'Type'] = 'Lamb/Sheep'
    else:
        cattles_copy.at[index, 'Type'] = ''


cattles_copy.replace('', np.nan, inplace=True)

# fill empty values in the 'type' column with the previous value
cattles_copy['Type'] = cattles_copy['Type'].fillna(method='ffill')


# Remove the last column and save it in a variable
last_col = cattles_copy.pop(cattles_copy.columns[-1])

# Insert the last column into the 1st position
cattles_copy.insert(0, last_col.name, last_col)


#THERE AIS ANOTHER COLUMN TO CHANGE POSITION

last_col = cattles_copy.pop(cattles_copy.columns[-1])

# Insert the last column into the ninth position
cattles_copy.insert(8, last_col.name, last_col)

# set the column names to the values in the first row
cattles_copy.columns = cattles_copy.iloc[0]

#drop first row
cattles_copy = cattles_copy.drop(0)

cols_rename = ['Type','Class','Units','Avg_Mass(kg)','Avg_Purchase','Avg_Selling','Selling_Min','Selling_Max','Date']

# rename the first 8 columns using the new list of column names
cattles_copy.columns = cols_rename + list(cattles_copy.columns[9:])

#drop last two columns 
cattles_copy = cattles_copy.iloc[:,:-3]

# split the 'Date' column into two new columns 'Start_Date' and 'End_Date'
cattles_copy[['From','Start_Date', 'End_Date']] = cattles_copy['Date'].str.split(' ', expand=True)

# drop the original 'Date' column
cattles_copy.drop(['Date','From'], axis=1, inplace=True)


#if the Class column has values that contain more than 3 characters, remove that row
cattles_copy = cattles_copy[cattles_copy.iloc[:,1].str.len()<=3]

cattles_copy = cattles_copy[~cattles_copy['Class'].str.startswith('FOR')]

cattles_copy = cattles_copy[~cattles_copy['Class'].str.startswith('is')]

# Define a regular expression pattern to match strings with symbols or only numbers
pattern = r'^\W+|\d+$'

# Filter the rows where the class column matches the pattern
cattles_copy = cattles_copy[~cattles_copy.iloc[:,1].str.match(pattern)]

cattles_copy.replace('#DIV/0!', np.nan, inplace=True)
cattles_copy.dropna(inplace=True)

cols = ['Units','Avg_Mass(kg)','Avg_Purchase','Avg_Selling','Selling_Min','Selling_Max']
cattles_copy[cols].replace(',', '', regex=True).astype(float)

problematic_row = cattles_copy[cattles_copy['Units'].apply(lambda x: not isinstance(x, str) or not x.isnumeric())]
# problematic_row

#use the errors='coerce' option in the pd.to_numeric function to convert the values to 
#numeric and any non-numeric values will be replaced with NaN.

cols = ['Units','Avg_Mass(kg)','Avg_Purchase','Avg_Selling','Selling_Min','Selling_Max']
cattles_copy[cols] = cattles_copy[cols].apply(pd.to_numeric, errors='coerce')
cattles_copy.dropna(inplace=True)

#change to datetime

date_cols = ['Start_Date', 'End_Date']
cattles_copy[date_cols] = cattles_copy[date_cols].apply(pd.to_datetime, format='%Y/%m/%d')

pigs_copy['Total_Purchases'] = pigs_copy['Units'] * pigs_copy['Avg_Purchase']

cattles_copy['Total_Purchases'] = cattles_copy['Units'] * cattles_copy['Avg_Purchase']
cattles_copy['Total_Selling'] = cattles_copy['Units'] * cattles_copy['Avg_Selling']


# create sqlalchemy engine
engine = create_engine("mysql+pymysql://{user}:{pw}@intern-dalrrd-team9-database.ctgb19tevqci.eu-west-1.rds.amazonaws.com/{db}"
                       .format(user="explore_student",
                               pw="explore-student",
                               db="darrld_data"))

# Transmit Cattles_data to RDS & s3
# Insert whole DataFrame into MySQL
# df.set_index("Market")
cattles_copy.to_sql('cattles_data', con = engine, if_exists = 'append', chunksize = 500, index=False)

# Transmit data to S3 bucket
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
cattles_copy.to_csv("/home/explore-student/internship-project-2207-09/pipeline/s3/livestock/cattles_data/{}.csv".format(timestamp))


# Transmit pigs_data to RDS & s3
# Insert whole DataFrame into MySQL
# df.set_index("Market")
pigs_copy.to_sql('pigs_data', con = engine, if_exists = 'append', chunksize = 500, index=False)

# Transmit data to S3 bucket
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
pigs_copy.to_csv("/home/explore-student/internship-project-2207-09/pipeline/s3/livestock/pigs_data/{}.csv".format(timestamp))


# # create success file
with open('/home/explore-student/internship-project-2207-09/pipeline/logs/.success_livestock_processing', 'w') as fp:
    pass