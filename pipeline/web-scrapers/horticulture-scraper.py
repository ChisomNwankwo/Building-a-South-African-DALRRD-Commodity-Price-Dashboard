from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from bs4 import BeautifulSoup
import time
import os
import pandas as pd
import shutil
from datetime import datetime



# VARIABLE INPUT:
# Set the website URL
website = 'http://webapps.daff.gov.za/amis/amis_price_search.jsp'

# Path to Chrome WebDriver executable file
# driver_path = r'C:\Users\PC\Documents\INTERNSHIP\chromedriver.exe'

# Create a Service object with the path to the executable
# service = Service(executable_path=driver_path)


# ChromeOptions
ChromeOptions = Options()
#prefs = {"download.default_directory" : "/home/explore-student/internship-project-2207-09/Sample-Datasets/horticulture"}
#ChromeOptions.add_experimental_option("prefs",prefs)

ChromeOptions.add_argument("--headless")
driver = webdriver.Chrome(options= ChromeOptions)

# Load the website
driver.get(website)
 
# Wait for the table to load
driver.implicitly_wait(20)




# Create lists of markets and products
# Find the select element with id 'cbSearchMarket'
market_select = Select(driver.find_element(By.ID, 'cbSearchMarket'))
# Extract the visible text for each product
markets = [market.get_attribute('innerHTML') for market in market_select.options]

# find the select element by id
select_element = Select(driver.find_element(By.ID,"cbSearchProduct"))

# get all the options from the select element
options = select_element.options

# create an empty list to store the option values
products = []

# iterate over the options and get their values
for option in options:
    products.append(option.get_attribute("value"))
    
products=products[1:]


# Find the select element with id 'cbSearchMarket'
#product_select = Select(driver.find_element(By.ID, 'cbSearchProduct'))
# Extract the visible text for each product
#products = [product.get_attribute('innerHTML') for product in product_select.options][1:]



def download_excel_file(market, product):
    # Select the desired options
    period_select = Select(driver.find_element(By.ID, 'cbPeriod'))
    period_select.select_by_visible_text('Last 30 Days') # VARIABLE INPUT:
    
    # select the market and product
    market_select = Select(driver.find_element(By.ID, 'cbSearchMarket'))
    market_select.select_by_visible_text(market)
    select_element = Select(driver.find_element(By.ID, 'cbSearchProduct'))
    select_element.select_by_value(product)


    # Select the default options for other filters
    variety_select = Select(driver.find_element(By.ID, 'cbSearchVariety'))
    variety_select.select_by_visible_text('All Varieties')
    class_select = Select(driver.find_element(By.ID, 'cbSearchClass'))
    class_select.select_by_visible_text('All Classes')
    size_select = Select(driver.find_element(By.ID, 'cbSearchSize'))
    size_select.select_by_visible_text('All Sizes')
    package_select = Select(driver.find_element(By.ID, 'cbSearchContainer'))
    package_select.select_by_visible_text('All Packages')

    # Find and click the "View Prices" button
    view_prices_button = driver.find_element(By.ID, "btnDBSearch")
    view_prices_button.click()

    # Wait for the results to load
    time.sleep(30)

    # Check if "No price available!" text exists in the page source
    if "NO PRICES AVAILABLE!" in driver.page_source:
        return None

    # Find and click the "Export" button
    export_button = driver.find_element(By.ID, "btnExport")
    export_button.click()

    # Wait for the download to complete
    time.sleep(20)


    # VARIABLE INPUT:
    # Find the most recent file in the default download folder
    download_folder = r'/home/explore-student/internship-project-2207-09/pipeline/bash-scripts'
    files = os.listdir(download_folder)
    files = [os.path.join(download_folder, f) for f in files]
    files = [f for f in files if f.endswith(".xls") or f.endswith(".xlsx")]

    # Create the web_files folder if it doesn't exist
    if not os.path.exists(os.path.join(download_folder, "web_files")):
        os.makedirs(os.path.join(download_folder, "web_files"))

    # Move the downloaded files to a folder with the market name and a timestamp
    for file in files:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        market_folder = os.path.join(download_folder, "web_files", market.replace(" ", "_"))
        if not os.path.exists(market_folder):
            os.makedirs(market_folder)
        new_file_name = os.path.splitext(os.path.basename(file))[0] + "_" + timestamp + os.path.splitext(file)[1]
        shutil.move(file, os.path.join(market_folder, new_file_name))

    return files


# call the function for each market and product
#THIS CODE WILL DOWNLOAD THE FILES AND MAY TAKE A WHILE

for market in markets:
    for product in products:
        download_excel_file(market, product)

# create success file
with open('/home/explore-student/internship-project-2207-09/pipeline/logs/.success_horticulture-scraper', 'w') as fp:
    pass
