from datetime import datetime
from selenium import webdriver
from dotenv import load_dotenv
from typing import Optional, Dict
import contextlib, pyautogui, pytz, json
from time import sleep, perf_counter
from os import environ as env_variable
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from concurrent.futures import ThreadPoolExecutor, as_completed
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from python_whatsapp_bot import Whatsapp, Inline_list, List_item
from selenium.common.exceptions import TimeoutException, NoSuchElementException

def main():
    
    load_dotenv()

    NUMBER: str = env_variable.get("MY_NUMBER")  # Your WhatsApp Number (234xxxxxxxxxx)
    NUM_ID: str = env_variable.get("NUM_ID")  # Your Number ID
    TOKEN: str =  env_variable.get("TOKEN")  # Token
    USERNAME: str =  env_variable.get("USER")  # Plu Username (Phone number)
    PASSWORD: str =  env_variable.get("PASSWORD")  # Plu Password

    driverpath: str = "assets\drivers\chromedriver.exe"

    base_url: str = "https://pluapp.net/"

    login_page: str = base_url + "index/index/login.html"
    homepage: str =  base_url + "index/index/index"
    
    gmtTime: str = lambda tz: datetime.now(
        pytz.timezone(tz)).strftime("%H : %M : %S")
    
    service = Service(executable_path=driverpath)
    options = Options()
    options.add_argument("--disable-gpu")
    options.add_argument("--no-first-run")
    options.add_argument("--single-process")
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument(r'--profile-directory=Plu Profile')
    options.add_argument(r'user-data-dir=C:\PluBot Chrome Profile')
    options.add_experimental_option('useAutomationExtension', False)
    options.add_experimental_option(
        "excludeSwitches", ["enable-automation", 'enable-logging'])
    options.add_argument('--disable-blink-features=AutomationControlled')
    bot = webdriver.Chrome(service=service, options=options)

    bot.get(login_page)
    if bot.current_url == homepage:
        print("Logged in.")
    else:  # Loggin in
        bot.find_element(By.XPATH, '//input[@class="pml"]').send_keys(USERNAME)
        bot.find_element(By.XPATH, '//input[@id="lpwd"]').send_keys(PASSWORD)
        bot.find_element(By.XPATH, '//input[@name="submit"]').click()


    input()


if __name__ == "__main__":
    main()