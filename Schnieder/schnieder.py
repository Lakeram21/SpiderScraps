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
import bs4
import time
from bs4 import BeautifulSoup
# from openpyxl import load_workbook
import pandas as pd
import os
import re

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
    return [driver, soup]

def getListOfCatalogNum( excel_path,row_nam):
    data = pd.read_excel(excel_path) 
    df = pd.DataFrame(data)
    listOfCatalogNumber =[]
    for number in df[row_nam]:
        listOfCatalogNumber.append(number)
    return listOfCatalogNumber
   
def getProductPage(catalogNum):
    driverSoup =setUpSoup('https://www.rittal.com/us-en_US/Suche')
    driver = driverSoup[0]
    soup = driverSoup[1]    
    time.sleep(20)
    
    return itemLink

def scrapProductInformation(productUrl, catalogNum):
    description = {}
    driverSoup = setUpSoup(productUrl)
    driver = driverSoup[0]
    driver.maximize_window()
    soup = driverSoup[1]
    return description

def createDirectory(manufacturer):
     # create directory for outputs
    outputDir = os.path.dirname(os.path.abspath(__file__)) + '\\'+manufacturer
    if not os.path.exists(outputDir):
        os.makedirs(outputDir)
    return outputDir
def findAllProductLink(productUrl):
    driverSoup = setUpSoup(productUrl)
    driver = driverSoup[0]
    driver.maximize_window()
    soup = driverSoup[1]

    container = soup.find('ul', {'class':'product-finder-result'})
    links = container.find_all('a')
    links_array=[]
    count = 0
    for link in links:
            if link.has_attr('href'):
                count +=1
                # links_array.append(link['href'])
    print(count)         
    print("Hello")

if __name__ == "__main__":
    df = pd.DataFrame()
    findAllProductLink('https://www.se.com/us/en/product-range-az')
    # outputDir = createDirectory('Rittal')
    # listOfCatalogNumber = getListOfCatalogNum('SpiderScraps\Schnieder\Schneider-Modicon Price List 2022 July.xlsx', 'Cat. Number',)
    # print('hello')
    # Looping through the catalog Number
    # for catalogNum in listOfCatalogNumber:
    #     # Get the Product Link
    #     productLink = getProductPage(catalogNum)
    #     # Opeinging the Product Link
    #     description = scrapProductInformation(productLink, catalogNum)
    #     df= df.append(description, ignore_index = True)
    #     df.to_excel(outputDir+'\\data.xlsx', encoding='utf-8', index=False)
   
    
    # df.to_excel(outputDir+'\\data.xlsx', encoding='utf-8', index=False)
    #'https://www.rittal.com/us-en_US/products/PG0002SCHRANK1/PG0003SCHRANK1/PGRP30363SCHRANK1/PRO70335?variantId=1500000'