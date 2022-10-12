from gettext import Catalog
from time import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import NoSuchElementException
import bs4
import time
from bs4 import BeautifulSoup
# from openpyxl import load_workbook
import pandas as pd
import os
import re
import requests

def downloadPDF(url, dirPath, attempt=0, session=None):
    ''' download a PDF
        args:
            url (str): url to download
            dirPath (str): directory path to save in
            session (requests.session()) optional: session connection
        return:
            name of file downloaded
    '''
    fileName = url.split('/')[-1] # get file name
    fileName = fileName.split('?')[0] # remove any params in the url
    if 'tracepartsonline.net' in url:
        return 'Did not download'
    if os.path.exists(dirPath + fileName):
        return fileName
    # requests
    requestStatus = False
    while not requestStatus and attempt < 5:
        try:
            r = requests.get(url, stream=True, timeout=3)
            requestStatus = r.ok
        except:
            print('retry {}'.format(url))
            attempt += 1
            downloadPDF(url, dirPath, attempt=attempt)
            requestStatus = False
        if not requestStatus:
            attempt += 1

    if attempt > 4:
        print('too many attempts')
        return 'Fail'
    ## add .pdf if not .pdf and not a .zip
    #if fileName[-4:] != '.pdf' and fileName[-4:] != '.zip':
    #    fileName = fileName + '.pdf'        
    try:
        with open(dirPath + fileName, 'wb') as f:
            # iterate through binary data and write out to file
            for chunk in r.iter_content(chunk_size=1024):
                if chunk: # filter out keep-alive new chunks
                    f.write(chunk)
    except:
        print('retry {}'.format(url))
        attempt += 1
        downloadPDF(url, dirPath, attempt=attempt)

    if attempt > 4:
        return 'Fail'
    return fileName

def downloadImg(url, dirPath):
    ''' download img
        args:
            url (str): url to download
            dirPath (str): directory path to save in
        return:
            name of file downloaded
    '''
    url = url.split('?')[0]
    fileName = url.split('/')[-1] # get file name
    if os.path.exists(dirPath + fileName):
        return fileName

    # add file extension if absent
    if len(fileName.split('.')) == 1:
        fileName = fileName + '.jpg'

    # get image and write to binary file
    r = requests.get(url, stream=True) 
    if r.ok:
        with open(dirPath + fileName, 'wb') as f:
            # iterate through binary data and write out to file
            for chunk in r.iter_content(chunk_size=1024):
                if chunk: # filter out keep-alive new chunks
                    f.write(chunk)
    else:
        return 'download failed image from {}, pheonix contact probably does not have an image for this'.format(url)
    return fileName

def setUpDriver(url):
    options = Options()
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    options.add_argument("--disable-popup-blocking")
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--incognito')
    # options.add_argument("--headless")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.maximize_window()
    driver.get(url)
    return driver

def setUpSoup(url):
    driver = setUpDriver(url)
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    # time.sleep(300)
    return [driver, soup]

def getListOfCatalogNum( excel_path,row_nam):
    data = pd.read_excel(excel_path) 
    df = pd.DataFrame(data)
    listOfCatalogNumber =[]
    for number in df[row_nam]:
        listOfCatalogNumber.append(number)
    return listOfCatalogNumber
   
def getProductPage(catalogNum):
    driverSoup =setUpSoup('https://hoffman.nvent.com/en-us/')
    driver = driverSoup[0]
    soup = driverSoup[1]

    # Get the search bar
    searchBar = driver.find_element(By.XPATH,'//*[@id="coveo_block_standalone_search_box"]/div[3]/div[1]/input')
    searchBar.send_keys(catalogNum)
    searchBar.send_keys(Keys.RETURN)

    # Find the Right Product
    time.sleep(10)
    driver.implicitly_wait(10)
    
    searchResultsContainers = driver.find_elements(By.CLASS_NAME,'coveo-result-list-container.coveo-list-layout-container')
    if searchResultsContainers !=None:
        for container in searchResultsContainers:
            containerText = container.text
            if catalogNum in containerText:
                searchResultsDivs = container.find_elements(By.CLASS_NAME,'coveo-list-layout')
                for div in searchResultsDivs:
                    try:
                        div.find_element(By.CLASS_NAME, 'nventCatalogId')
                        link = div.find_element(By.TAG_NAME, 'h3').find_element(By.TAG_NAME, 'a')
                        link.click()
                        time.sleep(10)
                        current_url = driver.current_url
                        driver.close()  
                        return current_url
                    except NoSuchElementException:
                        print("No such element")
        return 0

def scrapProductInformation(productUrl, catalogNum):
    description = {}
    driverSoup = setUpSoup(productUrl)
    driver = driverSoup[0]
    soup = driverSoup[1]

    # Getting the image
    productUrl = soup.find('li', {'class':'carousel__main-item carousel__item'}).find('img')['src']
    productTitle = soup.find('h1', {'class':'product-hero__title'}).get_text()

    # getting the BreadCrums to make filters
    breadCrumsCon = soup.find('ol', {'class':'breadcrumb'}).get_text()
    breadCrumsCon = breadCrumsCon.split('\n\n')
    filterCount = 1
    for bread in breadCrumsCon:
        if bread != '':
            if bread != 'Home':
                filter = bread.strip('\n')
                description['Filter'+str(filterCount)]= filter
                filterCount +=1

    # Getting Product Description
    productDescription = soup.find('div', {'class':'product-hero__description'}).get_text()
    description['ProductDescription'] = productDescription

    # Getting the product Attribute
    productAttribute = soup.find('div', {'class':'products-attribute__wrapper'}).find_all('li')
    for attrribute in productAttribute:
        text = attrribute.get_text()
        if ':' in text:
            texts = text.split(':')
            description[texts[0].strip().strip('\n')] = texts[1].strip().strip('\n')

    return description

def createDirectory(manufacturer):
     # create directory for outputs
    outputDir = os.path.dirname(os.path.abspath(__file__)) + '\\'+manufacturer
    if not os.path.exists(outputDir):
        os.makedirs(outputDir)
    return outputDir

if __name__ == "__main__":
    df = pd.DataFrame()
    outputDir = createDirectory('Hoffman')
    # listOfCatalogNumber = getListOfCatalogNum('Rittal Price List 2022 August Modified.xlsx', 'Catalog Part No.',)
    # productUrl= getProductPage('SSTB153012')
    scrapProductInformation('https://hoffman.nvent.com/en-us/products/encsstb153012','SSTB153012')
    