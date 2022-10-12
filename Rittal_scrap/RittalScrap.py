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
    driverSoup =setUpSoup('https://www.rittal.com/us-en_US/Suche')
    driver = driverSoup[0]
    soup = driverSoup[1]    
    time.sleep(20)
    driver.implicitly_wait(20)
    popUp = driver.find_element(By.XPATH,"/html/body/div[5]/div/div/div/div/div[2]/div[2]/div/div/button[3]")
    print(popUp)
    time.sleep(10)
    popUp.click()
    searchBox = driver.find_element(By.XPATH, '//*[@id="content"]/div[1]/div/div[2]/div/div/div/div/div/div[1]/div[1]/form/div/input')
    searchBox.send_keys(catalogNum)
    searchBox.send_keys(Keys.RETURN)
    time.sleep(10)
    page_source = driver.page_source
    soup = BeautifulSoup(page_source, 'html.parser')
    driver.implicitly_wait(10)
    time.sleep(10)
    itemLinkCon = soup.find_all('div', {'class':'teaser-list'})[0].find('a', {'class':'teaser-image'})
    itemLink = itemLinkCon['href']
    driver.close()
    return itemLink

def scrapProductInformation(productUrl, catalogNum):
    description = {}
    driverSoup = setUpSoup(productUrl)
    driver = driverSoup[0]
    driver.maximize_window()
    soup = driverSoup[1]

    navLinks = soup.find('div', {'id':'breadcrumb'})
    listOfBread = navLinks.find_all('a')
    filterCount = 1
    for link in listOfBread:
        linkstrip = link.get_text().strip('.').strip()
        if linkstrip != "Homepage":
            if linkstrip != "Products":
                if linkstrip != str(catalogNum):
                    description['Filter'+str(filterCount)] = linkstrip
                    filterCount +=1
        
                    
    time.sleep(10)
    popUp = driver.find_element(By.XPATH, '/html/body/div[5]/div/div/div/div/div[2]/div[2]/div/div/button[3]')
    popUp.click()
    cookiePopUP = driver.find_element(By.XPATH, '//*[@id="hs-eu-confirmation-button"]').click()
    time.sleep(5)

    # Main Product details
    productInfoCon = soup.find('div', {'class':'product-header-container'})
    imageUrl = productInfoCon.find('img')['src']
    SKU = 'Rittal_'+str(catalogNum)
    description['SKU'] = SKU
    description["ImageURL"] = imageUrl
    description['CatalogNumber'] = catalogNum

    # allColumns = articleCon.find_all('div', {'class':'collapsable'})
    allColumns = driver.find_elements(By.CLASS_NAME, 'collapsable')
    
    accessories =[]
    getDes = False
    getAcc = False
    index = 0
    for column in allColumns:
         time.sleep(10)
         driver.implicitly_wait(20)
         link =column.find_element(By.CLASS_NAME,'collapsable-label')
         driver.execute_script("arguments[0].scrollIntoView();",link)
         time.sleep(5)
         link.click()        #  if link != None:
            
         soup = BeautifulSoup(driver.page_source, 'html.parser')
         dataContainer = soup.find_all('div', {'class':'smooth-reflow-wrapper collapsable-container'})[index]
         time.sleep(5)
        #  Getting the description
         descriptionCon = dataContainer.find('div', {'class':'description-list'})
         if descriptionCon !=None and getDes == False:
            dls = descriptionCon.find('dl')
            getDes = True
            for dl in dls:
                if dl != ' ':
                    description[dl.find('dt').get_text()] = dl.find('dd').get_text()
            break
        
        # Getting Accesories
        #  accesoriesCon = dataContainer.find('div', {'class': 'accessories'})
        #  if accesoriesCon !=None and getAcc == False:
        #     containerList = driver.find_element(By.TAG_NAME,'ul')
        #     getAcc = True
        #     if containerList !=None:
        #         listOfLinks = containerList.find_elements(By.TAG_NAME, 'li')
        #         # for list in listOfLinks:
         
         index +=1
    driver.close() 
    print(description)
    # dataFrame = dataFrame.append(description, ignore=True)
    return description

def createDirectory(manufacturer):
     # create directory for outputs
    outputDir = os.path.dirname(os.path.abspath(__file__)) + '\\'+manufacturer
    if not os.path.exists(outputDir):
        os.makedirs(outputDir)
    return outputDir

if __name__ == "__main__":
    df = pd.DataFrame()
    outputDir = createDirectory('Rittal')
    listOfCatalogNumber = getListOfCatalogNum('Rittal Price List 2022 August Modified.xlsx', 'Catalog Part No.',)
    
    # Looping through the catalog Number
    for catalogNum in listOfCatalogNumber:
        # Get the Product Link
        productLink = getProductPage(catalogNum)
        # Opeinging the Product Link
        description = scrapProductInformation(productLink, catalogNum)
        df= df.append(description, ignore_index = True)
        df.to_excel(outputDir+'\\data.xlsx', encoding='utf-8', index=False)
   
    
    df.to_excel(outputDir+'\\data.xlsx', encoding='utf-8', index=False)
    #'https://www.rittal.com/us-en_US/products/PG0002SCHRANK1/PG0003SCHRANK1/PGRP30363SCHRANK1/PRO70335?variantId=1500000'