import random
import string
import datetime
import requests
import re
from bs4 import BeautifulSoup
import time
import csv
import unicodedata
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options 

print('import success')
start = time.time()

# Customizeable
output_filename = 'HMO License Scraping Results.csv'

## Replace any error encoded character to csv become space
def clean_string(x):
    try:
        x=x.replace('\"','\'\'').replace('\r',' ').replace('\n',' ')
        x=unicodedata.normalize('NFKD', x).encode('ascii', 'ignore')
        x=x.decode('ascii')
    except:
        x='?'

    return x

## Scraping HMO License Holder
def license_scraping(writer):
    chrome_options = webdriver.ChromeOptions()
    # chrome_options.add_argument("--headless")
    chrome_options.add_experimental_option("detach", True)
    driver = webdriver.Chrome(options=chrome_options)

    main_search_url = 'https://publicaccessapplications.newcastle.gov.uk/online-applications/search.do?action=advanced&searchType=Licencing'

    ward_arr = [
        '18NJES', ## North Jesmond
        '18SJES', ## South Jesmond
        '18HEAT' ## Heaton
    ]

    for ward in ward_arr:
        driver.get(main_search_url)

        ## Choose Application Type
        application_type_dropdown = driver.find_element_by_xpath("//select[@name='searchCriteria.applicationType']")
        application_type_dropdown.click()
        application_type_new = driver.find_element_by_xpath("//select[@name='searchCriteria.applicationType']").find_element_by_xpath("//option[@value='NEW']")
        application_type_new.click()

        ## Choose Category
        category_type_dropdown = driver.find_element_by_xpath("//select[@name='searchCriteria.categoryType']")
        category_type_dropdown.click()
        category_type_hmo = driver.find_element_by_xpath("//select[@name='searchCriteria.categoryType']").find_element_by_xpath("//option[@value='HMO']")
        category_type_hmo.click()

        ## Choose Ward
        ward_dropdown = driver.find_element_by_xpath("//select[@name='searchCriteria.ward']")
        ward_dropdown.click()
        ward_picked = driver.find_element_by_xpath("//select[@name='searchCriteria.ward']").find_element_by_xpath("//option[@value='{}']".format(ward))
        ward_picked.click()

        ## Choose Status
        status_dropdown = driver.find_element_by_xpath("//select[@name='searchCriteria.caseStatus']")
        status_dropdown.click()
        status_current_license = driver.find_element_by_xpath("//select[@name='searchCriteria.caseStatus']").find_element_by_xpath("//option[@value='Current Licence']")
        status_current_license.click()

        ## Press Search Button
        search_btn = driver.find_element_by_xpath("//input[@class='button primary']")
        search_btn.click()

        time.sleep(4) ## Wait until the search result page is loaded

        ## Choose Results per Page
        results_per_page_dropdown = driver.find_element_by_xpath("//select[@name='searchCriteria.resultsPerPage']")
        results_per_page_dropdown.click()
        results_per_page_100 = driver.find_element_by_xpath("//select[@name='searchCriteria.resultsPerPage']").find_element_by_xpath("//option[@value='100']")
        results_per_page_100.click()

        ## Press Go Button
        go_btn = driver.find_element_by_xpath("//input[@value='Go']")
        go_btn.click()

        time.sleep(3)

        print('=========================================')

        ## Search for pagination
        soup2 = BeautifulSoup(driver.page_source, 'html.parser')
        pager_top = soup2.find('p', class_='pager top')
        list_page_numbers = pager_top.find_all('a', class_='page')
        print('Number of pages: ' + str(len(list_page_numbers)))

        ## Loop through all the pages
        for x in range(1, len(list_page_numbers)+2): 
            print('Current page number: ' + str(x))

            if x != 1:
                ## Click different page
                driver.find_element_by_xpath("//a[@href='/online-applications/pagedSearchResults.do?action=page&searchCriteria.page={}']".format(x)).click()

            soup = BeautifulSoup(driver.page_source, 'html.parser')
    
            search_results = soup.find('ul', {"id": "searchresults"})
            list_search_results = search_results.find_all('li', class_='searchresult')

            for result in list_search_results:
                ## Get Applicant Address
                applicant_address = result.find('p', class_='address').text.strip()
                print('Applicant address: ' + str(applicant_address))
                
                ## Get Applicant Name
                applicant_name = result.find('p', class_='metaInfo').text.strip()
                # y = re.match(".+\n.+\n.+\n\n\n\n\n\n\n\n\n\n\n\n\n\n.+\n.+\n\n\n\n\n\n\n\n.+\n.+\n(.+)", str(applicant_name))
                applicant_final_name = clean_string(applicant_name)
                y = re.match(".+Applicant Name:(.+)", str(applicant_final_name))
                applicant_final_name = y.group(1)
                applicant_final_name = applicant_final_name.replace('\r', '')
                applicant_final_name = applicant_final_name.strip()
                print('Applicant name: ' + str(applicant_final_name))

                data = {
                    'Applicant Name': applicant_final_name,
                    'Applicant Address': applicant_address
                }

                writer.writerow(data)

            print('-------------------------------------')

###############################################

## Main function
def main():
    # Initialize fieldnames
    fieldnames=[
        'Applicant Name',
        'Applicant Address'
    ]

    filename_csv = output_filename
    with open(filename_csv , 'a', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        try:
            license_scraping(writer)
        except Exception as err:
            print('Error -> ' + str(err))

############################################### Run script

if __name__ == '__main__':
    main()

    end = time.time()
    run_time = end - start
    run_time_hour = run_time/3600
    print('\nScript runs for', round(run_time), 'seconds')
    print('Script runs for', round(run_time_hour), 'hour(s)')
