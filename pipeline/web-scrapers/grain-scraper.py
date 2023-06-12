# Import necessary modules
from selenium import webdriver
# from selenium.webdriver.firefox.options import Options
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
import pandas as pd
from datetime import datetime, timedelta
import time
import os

# VARIABLE INPUT:
base_url = "http://webapps.daff.gov.za/amis/Link.amis?method=GrainMarket"


ChromeOptions = Options()
ChromeOptions.add_argument("--headless")
driver = webdriver.Chrome(options= ChromeOptions)
driver.get(base_url)


# VARIABLE INPUT:
download_path = "/home/explore-student/internship-project-2207-09/pipeline/bash-scripts" 
day_from_xpath = "/html/body/form/table/tbody/tr[3]/td[1]/img"
day_to_xpath = "/html/body/form/table/tbody/tr[3]/td[2]/img"

Sale_day_from = "2023,4,1" # (datetime.today() - timedelta(days=7)).strftime("%Y,%m,%d") # format: yyyy,mm,dd
Sale_day_to = "2023,5,22" # datetime.today().strftime("%Y,%m,%d") # format: yyyy,mm,dd


def CalendarSelect (date, Xpath):

    # wait for the element to become clickable
    wait = WebDriverWait(driver, 10)
    element = wait.until(expected_conditions.element_to_be_clickable((By.XPATH, Xpath)))

    # click on the element
    element.click()

    #driver.find_element(By.XPATH, Xpath).click()
    wait = WebDriverWait(driver, 10)
    wait.until(expected_conditions.visibility_of_element_located((By.XPATH, Xpath)))

    # Format date
    expected_date = date
    formatted_date = datetime.strptime(expected_date, "%Y,%m,%d")

    expected_month = formatted_date.month 
    expected_year = formatted_date.year
        
    # Get current year and month
    current_month_text = driver.find_element(By.XPATH, '//*[@id="CalendarControl"]/table/tbody/tr[1]/td[2]').text
    current_month_text = current_month_text[:len(current_month_text)-5]
    # print(current_month_text)
    month_number = {"January":1,"February":2, "March":3, "April": 4, "May":5,"June":6,"July":7,"August":8,"September":9,"October":10,"November":11,"December":12}
    current_month_number = month_number[current_month_text] 
    current_year_text = driver.find_element(By.XPATH, '//*[@id="CalendarControl"]/table/tbody/tr[1]/td[2]').text
    current_year_number = int(current_year_text[-4:])
    # print(current_year_number)


    # Adjust Year
    while current_year_number != expected_year:
        if current_year_number > expected_year:
            driver.find_element(By.XPATH,'//*[@id="CalendarControl"]/table/tbody/tr[1]/td[1]/a[2]').click()
            current_year_text = driver.find_element(By.XPATH, '//*[@id="CalendarControl"]/table/tbody/tr[1]/td[2]').text
            current_year_number = int(current_year_text[-4:])
        elif current_year_number < expected_year:
            driver.find_element(By.XPATH,'//*[@id="CalendarControl"]/table/tbody/tr[1]/td[3]/a[1]').click()
            current_year_text = driver.find_element(By.XPATH, '//*[@id="CalendarControl"]/table/tbody/tr[1]/td[2]').text
            current_year_number = int(current_year_text[-4:])
            # print(current_year_number)

    # Adjust month
    while current_month_number != expected_month:
        if current_month_number > expected_month:
            driver.find_element(By.XPATH,'//*[@id="CalendarControl"]/table/tbody/tr[1]/td[1]/a[1]').click()
            current_month_text = driver.find_element(By.XPATH, '//*[@id="CalendarControl"]/table/tbody/tr[1]/td[2]').text
            current_month_text = current_month_text[:len(current_month_text)-5]
            current_month_number = month_number[current_month_text]
        elif current_month_number < expected_month:
            driver.find_element(By.XPATH,'//*[@id="CalendarControl"]/table/tbody/tr[1]/td[3]/a[2]').click()
            current_month_text = driver.find_element(By.XPATH, '//*[@id="CalendarControl"]/table/tbody/tr[1]/td[2]').text
            current_month_text = current_month_text[:len(current_month_text)-5]
            current_month_number = month_number[current_month_text]

    # print("Year: ", current_year_number)
    # print("Month: ", current_month_number)


    # Select day
    driver.find_element(By.XPATH, '//a[@href="javascript:setCalendarControlDate({})"]'.format(expected_date)).click()


    return


# selecting dropdown
markets = driver.find_element(By.ID, "cbSearchMarket")
market_sel = Select(markets)

market_list = []
for item in market_sel.options:
    market_list.append(item.get_attribute('innerText'))

print("Total market count: ", len(market_list))
market_list_sources = []

# check for downloaded files
def count_files_in_directory_with_substring(parent_directory, substring):
    count = 0
    for root, dirs, files in os.walk(parent_directory):
        for directory in dirs:
            if substring in directory:
                directory_path = os.path.join(root, directory)
                file_count = len(os.listdir(directory_path))
                count += file_count
    return count

file_count = count_files_in_directory_with_substring(download_path, "Grain")

for market in market_list[file_count:]:
        
    try:
    
        # # Select Sale_day_from
        CalendarSelect(Sale_day_from,day_from_xpath)

        # # Select Sale_day_to
        CalendarSelect(Sale_day_to,day_to_xpath)

        markets = driver.find_element(By.ID, "cbSearchMarket")
        market_sel = Select(markets)
        market_sel.select_by_index(market_list.index(market)) 


        # Select View prices
        driver.find_element(By.ID, "btnDBSearch").click()
        wait = WebDriverWait(driver, 20)
        wait.until(expected_conditions.visibility_of_element_located((By.ID, "btnPrint")))



        # # Click Export to Excel
        driver.find_element(By.ID, "btnPrint").click()
        wait = WebDriverWait(driver, 20)
        market_list_sources.append(market)
        print(market_list.index(market), market, "Successfully Downloaded")


        # Renaming the file
        Folder = "GrainData" + Sale_day_from + "_" + Sale_day_to
        file_name = market + ".xls"

        # Create folder if it doesn't exist
        folder_path = os.path.join(download_path, Folder)
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)


        # wait till file is downloaded
        while not os.path.exists(os.path.join(download_path, "MarketPrices.xls")):
            time.sleep(1)

        # Move the renamed file to the folder
        new_file_path = os.path.join(folder_path, file_name)
        os.rename(os.path.join(download_path, "MarketPrices.xls"), new_file_path)

    except NoSuchElementException:
        print(market_list.index(market), market, "Download Skipped")

# Ensure Last data is downloaded by waiting till last file is downloaded
while not os.path.exists(os.path.join(download_path, market_list[-1]+".xls")):
    time.sleep(1)
driver.quit()

# create success file
with open('/home/explore-student/internship-project-2207-09/pipeline/logs/.success_grain-scraper', 'w') as fp:
    pass
