from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys

import time

# ChromeDriver yolunu Service nesnesi ile belirtin
s = Service()
driver = webdriver.Chrome(service=s)

targetWeb ='https://ieeexplore.ieee.org/search/searchresult.jsp?newsearch=true&queryText=TCP'
driver.get(targetWeb)

inst_sign_in_button = WebDriverWait(driver, 120).until(
        EC.presence_of_element_located((By.CLASS_NAME, "inst-sign-in"))
    )
inst_sign_in_button.click()
time.sleep(2)
div_xpath = "//div[contains(text(), 'Access Through Your Institution')]"
inst2 = WebDriverWait(driver, 120).until(
        EC.presence_of_element_located((By.XPATH, div_xpath))
    )
inst2.click()
time.sleep(2)
'''inst3 = WebDriverWait(driver, 120).until(
        EC.presence_of_element_located((By.XPATH, "//a[contains(text(), 'Sign In with Username and Password')]"))
    )
inst3.click()'''
search_input = WebDriverWait(driver, 120).until(
        EC.presence_of_element_located((By.XPATH, "//input[@aria-label='Search for your Institution']"))
    )
search_input.send_keys('TOBB')
search_input.send_keys(Keys.RETURN)  # Opsiyonel: Arama yapmak için Enter tuşuna bas
# Kullanıcı 'Enter' tuşuna basana kadar bekleyin
time.sleep(2)
tobb_university_span = WebDriverWait(driver, 120).until(
        EC.presence_of_element_located((By.XPATH, "//span[contains(text(), 'TOBB University of Economics and Technology')]"))
    )
tobb_university_span.click()
time.sleep(2)
email_input = WebDriverWait(driver, 120).until(
        EC.presence_of_element_located((By.ID, "username"))
    )
email_input.send_keys('kulasan@etu.edu.tr')
time.sleep(2)
password_input = WebDriverWait(driver, 120).until(
        EC.presence_of_element_located((By.ID, "password"))
    )
password_input.send_keys('Keremking123*')
time.sleep(2)
login_button = WebDriverWait(driver, 120).until(
        EC.presence_of_element_located((By.XPATH, "//input[@type='submit'][@value='Log in']"))
    )
login_button.click()
login_button.click()
time.sleep(5)
search_input = WebDriverWait(driver, 120).until(
        EC.presence_of_element_located((By.XPATH, "//input[@type='search'][@aria-label='main']"))
    )
search_input.send_keys('AI')
time.sleep(2)
search_button = WebDriverWait(driver, 120).until(
        EC.presence_of_element_located((By.XPATH, "//button[@type='submit'][@aria-label='Search']"))
    )
search_button.click()

time.sleep(5)
input("gir")

# Kullanıcı girişi aldıktan sonra tarayıcıyı kapat
driver.quit()
