# Necessary Imports
import requests
from bs4 import BeautifulSoup
import pandas as pd
import io
import os 
import PyPDF2
from PyPDF2 import PdfReader
from datetime import datetime

# website to scrap
url = "http://rpo.co.za/slaughtering-statistics/"
 
# get the url from requests get method
read = requests.get(url)
 
# full html content
html_content = read.content
 
# Parse the html content
soup = BeautifulSoup(html_content, "html.parser")

# Get PDF Links
pdf_links =[]
for link in soup.find_all("a"):
    href = link.get("href")
    if href and href.endswith(".pdf"):
        pdf_links.append(href)


# # Get last week number
# now = datetime.now()
# year = now.strftime("%Y")
# week_number = "Week-" + str(int(now.strftime("%V"))-1)

#PDF Downloads. NB: may take a while
for pdf_link in pdf_links:
    # if year in pdf_link and week_number in pdf_link:
    response = requests.get(pdf_link)
    with open(pdf_link.split("/")[-1], "wb") as f:
        f.write(response.content)

print("Stage 1 completed")
# VARIABLE INPUT:  Directory containing PDF files
pdf_directory = "./market_csvs"

# Get a list of PDF files in the directory
pdf_files = [os.path.join(pdf_directory, f) for f in os.listdir(pdf_directory) if f.endswith('.pdf')]


print("Stage 2 completed")
# Loop over each PDF file and extract its text
all_text =""
for pdf_file in pdf_files:
    with open(pdf_file, 'rb') as file:
        pdf_reader = PyPDF2.PdfReader(file)
        num_pages = len(pdf_reader.pages) 
        text = ""
        for i in range(num_pages):
            page = pdf_reader.pages[i]
            text += page.extract_text()
            all_text += text
        print(f"Text from {pdf_file}: {text}")


print("Stage 3 completed")
data = all_text.split('\n')

my_list = [string for string in data if len(string) <= 150]
my_list = [string for string in my_list if not string.startswith('FOR ENQUIRIES')]

for i in range(len(my_list)):
    if my_list[i].startswith('Class Units Avg Avg Purch Avg Selling Selling Selling'):
        parts = my_list[i].split(' From ')
        new_str = 'Class Units Avg_mass Avg_purch Avg_selling Selling_min Selling_max'
        my_list[i] = new_str + parts[1]

for i in range(len(my_list)):
    if 'Class Units Avg Avg Purch Avg Selling Selling Selling From' in my_list[i]:
        parts = my_list[i].split(' From ')
        new_str = 'Class Units Avg_mass Avg_purch Avg_selling Selling_min Selling_max From ' + parts[1]
        my_list[i] = new_str

for item in my_list[:]: # iterate over a copy of the list
    if item.startswith('is up-to-date, accurate and complete. NATIONAL SOUTH AFRICAN'):
        my_list.remove(item) # remove the item from the list

for item in my_list[:]: # iterate over a copy of the list
    if item.startswith('Mass Price Price min max  Beef A2 - Sales Price '):
        my_list.remove(item) # remove the item from the list

for i in range(len(my_list)):
    if my_list[i].startswith('Class Units Avg Mass Avg Purch Purch Min Purch Max'):
        new_str = 'Class Units Avg_mass Avg_purch Purch_min Purch_max'
        my_list[i] = new_str

for i in range(len(my_list)):
    if my_list[i].startswith('Class Units Avg Mass Avg Purch Avg Selling Selling Min Selling Max'):
        new_str = 'Class Units Avg_mass Avg_purch Avg_Selling Selling_Min Selling_Max'
        my_list[i] = new_str


for item in my_list[:]: # iterate over a copy of the list
    if item.startswith('THIS INFORMATION IS PROTECTED AGAINST COPYING OR DISTRIBUTION WITHOUT PRIOR PERMISSION'):
        my_list.remove(item) # remove the item from the list 

for item in my_list[:]: # iterate over a copy of the list
    if item.startswith('THIS INFORMATION IS PROTECTED AGAINST COPYING OR DISTRIBUTION WITHOUT PRIOR PERMISSION'):
        my_list.remove(item) # remove the item from the list 

# Substring to search for
substring = 'NATIONAL SOUTH AFRICAN PRICE INFORMATION FOR WEEK'

# Filter the list to remove strings containing the substring
my_list = [s for s in my_list if substring not in s]


# String to search for
search_string = "Class Units Avg Avg Purch Avg Selling Selling Selling"

# Check if the search string is in the list
if search_string in my_list:
    print("The search string is present in the list.")
else:
    print("The search string is not present in the list.")


for i in range(len(my_list)):
    if 'Class Units Avg Mass Avg Purch Avg Selling Selling Min Selling Max' in my_list[i]:
        parts = my_list[i].split(' From ')
        new_str = 'Class Units Avg_mass Avg_purch Avg_selling Selling_min Selling_max'
        my_list[i] = new_str + parts[1]


print("Stage 4 completed")
# Divide into multiple lists
result = []
current_list = []
for item in my_list:
    if 'Class Units Avg_mass Avg_purch Avg_selling Selling_min' in item:
        if current_list:
            result.append(current_list)
            current_list = []
    current_list.append(item)
result.append(current_list)


print("Stage 5 completed")




# Create an empty DataFrame to store the converted data
df = pd.DataFrame(columns=["Class", "Units", "Avg_mass", "Avg_purch", "Avg_selling", "Selling_min", "Selling_max"])

# Loop through each string in my_list and extract the relevant data
for s in my_list:
    # Check if the string contains data for a new row
    if len(s.split()) == 7:
        # Extract the data for the new row
        row_data = s.split()
        row_data[1:] = [x.replace(",", ".") for x in row_data[1:]] # replace comma with dot to convert the numeric columns
        # Add the new row to the DataFrame
        df.loc[len(df)] = row_data
    else:
        # If the string does not contain data for a new row, ignore it
        pass

# Print the resulting DataFrame
df = pd.DataFrame([line.split() for line in my_list])

print("Stage 6 completed")

# convert dataframe to csv file
df.to_csv('livestock.csv', index=False)