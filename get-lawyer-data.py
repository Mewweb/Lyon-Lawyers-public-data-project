#coding:utf-8
from selenium import webdriver
import json
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time

options = Options()

options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

driver = webdriver.Chrome(options=options)

base_url = "https://www.barreaulyon.com/annuaire"

driver.get(base_url)
time.sleep(6)
pages = 1
fiche = 1
nextButton = driver.find_element(By.CSS_SELECTOR,".custom-pagination .next").get_attribute("href")
data = []
while True:
    
    a_elements = driver.find_elements(By.CSS_SELECTOR, ".container article .entry-link")
    href_elements = list({element.get_attribute("href") for element in a_elements})

    for href in href_elements:
        data_item = {}
        driver.get(href)
        time.sleep(2)
        title = driver.find_element(By.CSS_SELECTOR, ".entry-header h1")
        data_item["title"] = title.text
        contactItems = driver.find_elements(By.CSS_SELECTOR, ".entry-infos .entry-infos__item")
        contact = {}

        for item in contactItems:
            if item.get_attribute("class").find("tel") != -1:
                contact["phone"] = item.text
            elif item.get_attribute("class").find("mail") != -1:
                contact["email"] = item.text
            elif item.find_element(By.CSS_SELECTOR, "i").get_attribute("class").find("print") != -1:
                contact["fax"] = item.text
            elif item.find_element(By.CSS_SELECTOR, "i").get_attribute("class").find("pin") != -1:
                contact["site"] = item.text
            else:
                print("Autre")
                item.text
        
        fiche += 1
        print(fiche)
        street = ""
        postcode = ""
        data_item["contact"] = contact

        entrycontents = driver.find_elements(By.CSS_SELECTOR, ".entry-content .entry-content__item")
        for entrycontent in entrycontents:
            if entrycontent.find_element(By.CSS_SELECTOR, "b").text.lower() == "prestation de serment" :
                data_item["service"] = entrycontent.find_element(By.CSS_SELECTOR,"p").text
            
            if entrycontent.find_element(By.CSS_SELECTOR, "b").text.lower() == "rue":
                street = entrycontent.find_element(By.CSS_SELECTOR, "p").text

            if entrycontent.find_element(By.CSS_SELECTOR, "b").text.lower() == "code postal":
                postcode = entrycontent.find_element(By.CSS_SELECTOR, "p").text
        
        data_item["address"] = street + " " + postcode

        data.append(data_item)

    print(pages)
    pages += 1
    fiche = 1
    print(nextButton)
    if nextButton != None:
        driver.get(nextButton)
    else:
        break
    print("---Changement de page---")
    time.sleep(2)
    nextButton = driver.find_element(By.CSS_SELECTOR, ".custom-pagination .next").get_attribute("href")



with open("data.json", "w") as f:
    f.write(json.dumps(data))