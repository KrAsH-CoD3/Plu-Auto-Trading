from datetime import datetime
from selenium import webdriver
from dotenv import load_dotenv
from typing import Optional, Dict
from time import sleep, perf_counter
from os import environ as env_variable
import contextlib, pyautogui, pytz, json
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

    MY_NUMBER: str = env_variable.get("MY_NUMBER")  # Your WhatsApp Number (234xxxxxxxxxx)
    NUM_ID: str = env_variable.get("NUM_ID")  # Your Number ID
    TOKEN: str =  env_variable.get("TOKEN")  # Token
    USERNAME: str =  env_variable.get("USER")  # Plu Username (Phone number)
    PASSWORD: str =  env_variable.get("PASSWORD")  # Plu Password
    
    plu_base_url: str = "https://pluapp.net/"
    plu_login_page: str = plu_base_url + "index/index/login.html"
    plu_homepage: str =  plu_base_url + "index/index/index.html"
    plu_contract_record: str = plu_base_url + "index/contract/record.html"
    telegram_url: str = 'https://web.telegram.org/a/#-1001640574914'

    timezone: str = "Africa/Lagos"  # Your timezone
    sticky_date_xpath: str = '//div[@class="sticky-date interactive"]'
    driverpath: str = "assets\drivers\chromedriver.exe"
    durationbtn_xpath: str = '//div[@id="time_1"]//span[text()="60 S"]'
    selected_duration_xpath: str = '//div[@class="dong_order_option_list fontchangecolor fontchangecolor_1 bgf5465cim"]'
    msgs_xpath: str = '//div[@class="text-content clearfix with-meta"]'
    status_date_xpath: str = '//div[@id="list_box"]//div[@class="listbox_title_r"]//span[@class="fcc"]'

    
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
    wa_bot = Whatsapp(number_id=NUM_ID, token=TOKEN)


    def getSignal():
        bot.get(telegram_url); sleep(5)
        msgs = wait.until(EC.visibility_of_all_elements_located((By.XPATH, msgs_xpath)))
        bot.find_element(By.XPATH, '//i[@class="AafG9_xBi_2eJ_bFNnNg icon icon-arrow-down"]').click()
        msg = msgs[-3].text  # Should be -1 at 8PM
        signal: dict = {}

        signal_atrr: list  = ['coin', 'action']
        counter: int = 0
        for i in msg.split("\n"): 
            if any(["Trading products:" in i, "Transaction instruction:" in i]):
                signal[signal_atrr[counter]] = i.split("【")[-1].split("】")[0]
                counter += 1
        
        print("Signal Gotten! 👍", signal)
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

        bot.get(coin_link)  # Goto Trading Page

        for idx in range(4):
            try:
                wait5secs.until(EC.element_to_be_clickable((By.XPATH, actionbtn_xpath)))
                break
            except TimeoutException: 
                if idx >= 2: bot.get(coin_link)

        bot.find_element(By.XPATH, actionbtn_xpath).click()  # Click Action Button

        # Amount and duration is auto inputted and selected 
        try: 
            # REMOVE FROM HERE  # TESTING PURPOSE
            bot.find_element(By.XPATH, '//input[@id="tzmoney"]').send_keys("10")  # Type amount/Your amount here
            bot.find_element(By.XPATH, '//span[@id="balance"]').click()  # To update expected balance
            # TO HERE
            wait5secs.until(EC.element_to_be_clickable((By.XPATH, durationbtn_xpath)))
            bot.find_element(By.XPATH, durationbtn_xpath).click()  # Click Duration Button
            wait5secs.until(EC.visibility_of_element_located((By.XPATH, selected_duration_xpath)))
            # bot.find_element(By.XPATH, '//input[@id="tzmoney"]').send_keys("10")  # Type amount/Your amount here
        except: ... # 
        finally: 
            initial_balance: float = float(bot.find_element(By.XPATH, '//span[@id="balance"]').text)  # Initial balance
            bot.find_element(By.XPATH, '//span[@id="balance"]').click()  # To update expected balance
            bot.find_element(By.XPATH, '//span[text()="Confirm order"]').click()  # Click Confirm Order
            print("Trading...")
            for i in range(0, 90, 30): # 90 S Countdown with 30 S steps and WebDriverWait 
                if i >= 30: 
                    trading_amount = float(bot.find_element(By.XPATH, '//div[@id="timer_buynum"]').text)
                    exp_profit = float(bot.find_element(By.XPATH, '//div[@id="expected_profits"]').text)
                    print(f'{initial_balance= } NGN\n{trading_amount= } NGN\n{exp_profit= } NGN')
                with contextlib.suppress(TimeoutException):
                    # Wait for "Check Results" to be visible on the screen after countdown
                    wait.until(EC.visibility_of_element_located((By.XPATH, '//div[@class="wait_box_info"]')))
                    break
        
        input(F"DONE FOR NOW!")
        
        bot.get(plu_contract_record)
        numeric_vales = bot.find_elements(By.XPATH, '//span[@class=" f12 fce5"]')  # Numeric values
        evenStatus_OddDate = bot.find_elements(By.XPATH, status_date_xpath)  # evenStatus_OddDate # First=Status, Second=Date
        for idx, numeric_value in enumerate(numeric_vales):
            if idx == 3: print(f'{initial_balance = }, Profit = {float(numeric_value.text)}\nNew Balance = {initial_balance + float(numeric_value.text)}')
        evenStatus_OddDate_list: list = []
        for i in evenStatus_OddDate:
            evenStatus_OddDate_list.append(i.text)
        
        # Send to Self //  # Add balance and profit 
        wa_bot.send_message(MY_NUMBER, f"Auto trade complete at {gmtTime(timezone)}.\n{initial_balance = }, Profit = {float(numeric_value.text)}\nNew Balance = {initial_balance + float(numeric_value.text)}", 
            reply_markup=Inline_list("Show list",list_items=[List_item("Nice one 👌"), List_item("Thanks ✨"), List_item("Great Job")]))
        

    
        input("Press the enter key: ")

    # signal: dict = getSignal()
    signal: dict = {'coin': 'FIL', 'action': 'PUT'}

    coin: str = signal['coin'].lower()
    action: str = signal['action'].upper()
    actionbtn_xpath: str = f"//span[text()='{action}']"
    coin_link: str = f'https://pluapp.net/index/trade/trans.html?sytx={coin}'

    trade()


if __name__ == "__main__":
    main()