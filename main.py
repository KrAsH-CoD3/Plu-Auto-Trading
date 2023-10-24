from time import sleep
import contextlib, pytz
from datetime import datetime
from selenium import webdriver
from dotenv import load_dotenv
from os import environ as env_variable
from typing import Final, Optional, Dict
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from concurrent.futures import ThreadPoolExecutor, as_completed
from selenium.webdriver.support import expected_conditions as EC
from python_whatsapp_bot import Whatsapp, Inline_list, List_item

def main():
    
    load_dotenv()

    TOKEN: Final =  env_variable.get("TOKEN")  # Token
    NUM_ID: Final = env_variable.get("NUM_ID")  # Your Number ID
    USERNAME: Final =  env_variable.get("USER")  # Plu Username (Phone number)
    PASSWORD: Final =  env_variable.get("PASSWORD")  # Plu Password
    MY_NUMBER: Final = env_variable.get("MY_NUMBER")  # Your WhatsApp Number (234xxxxxxxxxx)
    
    plu_base_url: str = "https://pluapp.net/"
    plu_homepage: str =  plu_base_url + "index/index/index.html"
    plu_login_page: str = plu_base_url + "index/index/login.html"
    telegram_url: str = 'https://web.telegram.org/a/#-1001640574914'
    plu_contract_record: str = plu_base_url + "index/contract/record.html"

    timezone: str = "Africa/Lagos"  # Your timezone
    driverpath: str = "assets\drivers\chromedriver.exe"
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
    wa_bot = Whatsapp(number_id=NUM_ID, token=TOKEN)


    def getSignal():
        bot.get(telegram_url)
        print("Logged into Telegram."); sleep(5)
        count = 1
        while True:
            msgs = wait.until(EC.visibility_of_all_elements_located((By.XPATH, msgs_xpath)))
            with contextlib.suppress(Exception):  # Scoll to bottom (in case hidden) (ElementClickInterceptedException)
                bot.find_element(By.XPATH, '//i[@class="AafG9_xBi_2eJ_bFNnNg icon icon-arrow-down"]').click()  
            trade_msg = msgs[-1].text

            signal: dict = {}
            signal_key: list  = ['coin', 'action']

            counter = 0 
            for i in trade_msg.split("\n"): 
                if any(["Trading products:" in i, "Transaction instruction:" in i]):
                    signal[signal_key[counter]] = i.split("【")[-1].split("】")[0]
                    counter+=1

            if len(signal) == 2: break
            else:
                print(f"{count}. Waiting for signal..."); count+=1
                sleep(5) # Wait 5 secs and check again
        
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
        print("Logged in successfully into PLU. 😁\n", '-'*35, sep='')

        bot.get(coin_link)  # Goto Trading Page

        for idx in range(4):
            try:
                WebDriverWait(bot, 5).until(EC.element_to_be_clickable((By.XPATH, actionbtn_xpath)))
                break
            except TimeoutException: 
                if idx >= 2: bot.get(coin_link)

        bot.find_element(By.XPATH, actionbtn_xpath).click()  # Click Action Button
        
        sleep(3) # 3 secs sleep to load auto duration selection and amount

        ''' Amount and duration are auto inputted and selected by PluApp
         And cannot be editted (Amount and trade duration) '''
        
        initial_balance: float = float(bot.find_element(By.XPATH, '//span[@id="balance"]').text)  # Initial balance
        bot.find_element(By.XPATH, '//span[text()="Confirm order"]').click()  # Click Confirm Order
        print("Trading...")
        sleep(3) # 3 secs sleep to start the countdown
        
        # Check and Wait for the text "Check Results" TWICE to be visible on the screen after countdown
        for _ in range(2):
            with contextlib.suppress(TimeoutException, ValueError):
                trading_amount = float(bot.find_element(By.XPATH, '//div[@id="timer_buynum"]').text)
                exp_profit = float(bot.find_element(By.XPATH, '//div[@id="expected_profits"]').text)
                wait.until(EC.visibility_of_element_located((By.XPATH, '//div[@class="wait_box_info"]')))
                break
        
        while True:
            bot.get(plu_contract_record)
            numeric_vales = bot.find_elements(By.XPATH, '//span[@class=" f12 fce5"]')  # Numeric values
            evenStatus_OddDate: list = [i.text for i in bot.find_elements(By.XPATH, status_date_xpath)]

            with contextlib.suppress(AssertionError):
                status: str = evenStatus_OddDate[0]
                assert status == 'Settled'
                break
            sleep(5)

        for idx, numeric_value in enumerate(numeric_vales):
            if idx == 3: # The text 'Settled' is index 3
                profit: float = float(numeric_value.text)
                loss: float = 0.0
                break

        if '-' in str(profit): loss = str(profit).split('-')[1] 
        trade_output: str = f"Auto trade initiated at {evenStatus_OddDate[1]}\nInitial balance = {initial_balance} NGN\nTrade amount = {trading_amount} NGN\nExpected profit = {exp_profit} NGN\n{'-'*30}\nStatus = {evenStatus_OddDate[0]}, {'Loss' if '-' in str(profit) else 'Profit'} = {loss if '-' in str(profit) else profit} NGN\nNew Balance = {initial_balance + profit} NGN\nAuto trade completed at {''.join(gmtTime(timezone).split(' '))}"

        print(trade_output)
        
        # Send to Self
        wa_bot.send_message(MY_NUMBER, trade_output, 
            reply_markup=Inline_list("Show list",list_items=[List_item("Nice one 👌"), List_item("Thanks ✨"), List_item("Great Job")]))
          
    signal: dict = getSignal()

    coin: str = signal['coin'].lower()
    action: str = signal['action'].upper()
    actionbtn_xpath: str = f"//span[text()='{action}']"
    coin_link: str = f'{plu_base_url}index/trade/trans.html?sytx={coin}'

    trade()


if __name__ == "__main__":
    main()