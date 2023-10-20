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
    
    plu_base_url: str = "https://pluapp.net/"
    plu_login_page: str = plu_base_url + "index/index/login.html"
    plu_homepage: str =  plu_base_url + "index/index/index.html"
    telegram_url: str = 'https://web.telegram.org/a/#-1001640574914'

    sticky_date_xpath: str = '//div[@class="sticky-date interactive"]'
    driverpath: str = "assets\drivers\chromedriver.exe"
    durationbtn_xpath: str = '//div[@id="time_1"]//span[text()="60 S"]'
    selectd_duration_xpath: str = '//div[@class="dong_order_option_list fontchangecolor fontchangecolor_1 bgf5465cim"]'
    msgs_xpath: str = '//div[@class="text-content clearfix with-meta"]'

    
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
    wait = WebDriverWait(bot, 30)
    wait5secs = WebDriverWait(bot, 5)


    def getSignal():
        bot.get(telegram_url); sleep(5)
        # sticky_dates = wait.until(EC.visibility_of_all_elements_located((By.XPATH, sticky_date_xpath)))  # NOT USED
        msgs = wait.until(EC.visibility_of_all_elements_located((By.XPATH, msgs_xpath)))
        # sticky_dates = bot.find_elements(By.XPATH, sticky_date_xpath)
        msg = msgs[-2].text
        signal: dict = {}

        signal_atrr: list  = ['coin', 'action']
        counter: int = 0
        for i in msg.split("\n"): 
            if any(["Trading products:" in i, "Transaction instruction:" in i]):
                signal[signal_atrr[counter]] = i.split("【")[-1].split("】")[0]
                counter += 1
        
        print("Signal gotten 👍")
        return signal

    def trade():
        
        bot.get(plu_login_page)

        if bot.current_url not in plu_homepage: 
            bot.find_element(By.XPATH, '//input[@class="pml"]').send_keys(USERNAME)
            bot.find_element(By.XPATH, '//input[@id="lpwd"]').send_keys(PASSWORD)
            bot.find_element(By.XPATH, '//input[@name="submit"]').click()
            wait.until(EC.url_to_be(plu_homepage))

        assert bot.current_url in plu_homepage
        print("Logged in successfully into PLU. 😁")

        bot.get(coin_link)

        for idx in range(4):
            try:
                wait5secs.until(EC.element_to_be_clickable((By.XPATH, actionbtn_xpath)))
                break
            except TimeoutException: 
                if idx >= 2: bot.get(coin_link)
        
        bot.find_element(By.XPATH, actionbtn_xpath).click()  # Click Action Button
        wait5secs.until(EC.element_to_be_clickable((By.XPATH, durationbtn_xpath)))
        bot.find_element(By.XPATH, durationbtn_xpath).click()  # Click Duration Button
        wait5secs.until(EC.visibility_of_element_located((By.XPATH, selectd_duration_xpath)))
        try:
            bot.find_element(By.XPATH, '//input[@id="tzmoney"]').send_keys("12000")  # Type amount
        except: ...
        # bot.find_element(By.XPATH, '//span[text()="Confirm order"]').click()  # Click Confirm Order

    
        input("Press the enter key: ")

    signal: dict = getSignal()

    coin: str = signal['coin'].lower()
    action: str = signal['action'].upper()
    actionbtn_xpath: str = f"//span[text()='{action}']"
    coin_link: str = f'https://pluapp.net/index/trade/trans.html?sytx={coin}'

    trade()


if __name__ == "__main__":
    main()