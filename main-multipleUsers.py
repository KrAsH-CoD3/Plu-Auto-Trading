from time import sleep, perf_counter
import contextlib, pytz
from datetime import datetime
from selenium import webdriver
from dotenv import load_dotenv
from os import environ as env_variable
from typing import Final, Optional, Dict
from selenium.webdriver.common.by import By
from concurrent.futures import ThreadPoolExecutor
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from python_whatsapp_bot import Whatsapp, Inline_list, List_item
from selenium.common.exceptions import TimeoutException, NoSuchElementException


def main():
    load_dotenv()

    TOKEN: Final = env_variable.get("TOKEN")  # Token
    NUM_ID: Final = env_variable.get("NUM_ID")  # Your Number ID
    MY_NUMBER: Final = env_variable.get(
        "MY_NUMBER"
    )  # Your WhatsApp Number (234xxxxxxxxxx)

    plu_base_url: str = "https://pluapp.net/"
    plu_homepage: str = plu_base_url + "index/index/index.html"
    plu_login_page: str = plu_base_url + "index/index/login.html"
    telegram_url: str = "https://web.telegram.org/a/#-1001640574914"
    plu_contract_record: str = plu_base_url + "index/contract/record.html"

    timezone: str = "Africa/Lagos"  # Your timezone
    driverpath: str = r"assets\drivers\chromedriver.exe"
    msgs_xpath: str = '//div[@class="text-content clearfix with-meta"]'
    status_date_xpath: str = (
        '//div[@id="list_box"]//div[@class="listbox_title_r"]//span[@class="fcc"]'
    )

    gmtTime: str = lambda tz: datetime.now(pytz.timezone(tz)).strftime("%H : %M : %S")

    wa_bot = Whatsapp(number_id=NUM_ID, token=TOKEN)

    def gotoPage(goto_link, plubot, NAME):
        while True:
            try:
                plubot.get(goto_link)  # Goto Trading Page
                accs_exce_elem = plubot.find_element(
                    By.XPATH, '//pre[text()="Access exception, please try again."]'
                )
                if accs_exce_elem is not None:
                    print(f"{NAME.capitalize()} Access Exception, Waiting...")
                WebDriverWait(plubot, 10).until(
                    EC.invisibility_of_element(
                        (
                            By.XPATH,
                            '//pre[text()="Access exception, please try again."]',
                        )
                    )
                )
            except TimeoutException:
                continue
            except NoSuchElementException:
                break

    def getSignal():

        service = Service(executable_path=driverpath)
        telebot_opts = Options()
        telebot_opts.add_argument(r"--profile-directory=Plu Profile")
        telebot_opts.add_argument(r"user-data-dir=C:\PluBot Chrome Profile")
        telebot_opts.add_experimental_option(
            "excludeSwitches", ["enable-automation", "enable-logging"]
        )
        telebot = webdriver.Chrome(service=service, options=telebot_opts)
        telebot.set_window_size(250, 600)
        telebot.set_window_rect(0, 60)
        telebot_wait = WebDriverWait(telebot, 30)

        while True:  # Continous login if failed
            telebot.get(telegram_url)
            with contextlib.suppress(TimeoutException):  # Channel Name
                telebot_wait.until(
                    EC.visibility_of_element_located(
                        (By.XPATH, '//div[@class="title ysHMmXALnn0fgFRc7Bn7"]//h3[text()="PLU - Official Signal Channel⑦"]')
                    )
                )
                print("Logged into Telegram.")
                break
        
        print("Loading Messages...")
        
        refresh_time: float = perf_counter()
        while True:
            try:  ## Sticky Date
                telebot.find_element(By.XPATH, '//div[@class="sticky-date interactive"]//span[text()="Today"]')
                break
            except NoSuchElementException:
                if (perf_counter() - refresh_time) >= 15: 
                    telebot.get('https://google.com/')
                    telebot.get(telegram_url)
                    refresh_time = perf_counter()
                    continue

        count = 1
        while True:
            msgs = telebot_wait.until(
                EC.visibility_of_all_elements_located((By.XPATH, msgs_xpath))
            )
            with contextlib.suppress(
                Exception
            ):  # Scoll to bottom (in case hidden) (ElementClickInterceptedException)
                telebot.find_element(
                    By.XPATH, '//i[@class="AafG9_xBi_2eJ_bFNnNg icon icon-arrow-down"]'
                ).click()
            trade_msg = msgs[-1].text

            signal: dict = {}
            signal_key: list = ["coin", "action"]

            counter = 0
            for i in trade_msg.split("\n"):
                if any(["Trading products:" in i, "Transaction instruction:" in i]):
                    signal[signal_key[counter]] = i.split("【")[-1].split("】")[0]
                    counter += 1

            if len(signal) == 2:
                break
            else:
                print(f"{count}. Waiting for signal...")
                count += 1
                sleep(5)  # Wait 5 secs and check again

        print(f"Signal Gotten! 👍 signal= {signal['action']} : {signal['coin']}")
        telebot.quit()

        return signal

    def trade(NAME, USERNAME, PASSWORD, xAxis, yAxis):
        plubot_opts_args: list = [
            '--headless',
            "--incognito",
            rf"--profile-directory={NAME.capitalize()} Plu Profile",
            rf"user-data-dir=C:\{NAME.capitalize()} PluBot Chrome Profile",
        ]

        service = Service(executable_path=driverpath)
        plubot_opts = Options()
        [
            plubot_opts.add_argument(plubot_opts_arg)
            for plubot_opts_arg in plubot_opts_args
        ]
        plubot_opts.add_experimental_option(
            "excludeSwitches", ["enable-logging", "enable-automation"]
        )
        plubot = webdriver.Chrome(service=service, options=plubot_opts)
        plubot.set_window_size(250, 600)
        plubot.set_window_rect(xAxis, yAxis)
        pluwait = WebDriverWait(plubot, 30)

        plubot.get(plu_login_page)

        if plubot.current_url not in plu_homepage:
            plubot.find_element(By.XPATH, '//input[@class="pml"]').send_keys(USERNAME)
            plubot.find_element(By.XPATH, '//input[@id="lpwd"]').send_keys(PASSWORD)
            plubot.find_element(By.XPATH, '//input[@name="submit"]').click()
            pluwait.until(EC.url_to_be(plu_homepage))

        assert plubot.current_url in plu_homepage
        print(f"Plutomania welcomes {NAME.capitalize()}. 😁\n", "-" * 35, sep="")

        while True:
            gotoPage(coin_link, plubot, NAME)
            while True:
                try:
                    WebDriverWait(plubot, 5).until(
                        EC.element_to_be_clickable((By.XPATH, actionbtn_xpath))
                    )
                    break
                except TimeoutException:
                    continue

            plubot.find_element(
                By.XPATH, actionbtn_xpath
            ).click()  # Click Action Button
            sleep(3)  # 3 secs sleep to load auto duration selection and amount

            """
            Amount and trade duration are auto inputted and 
            selected by site for the given signal and cannot be editted
            """

            initial_balance: float = float(
                plubot.find_element(By.XPATH, '//span[@id="balance"]').text
            )  # Initial balance
            if initial_balance == 0.0:
                continue
            break

        plubot.find_element(
            By.XPATH, '//span[text()="Confirm order"]'
        ).click()  # Click Confirm Order
        print(f"{NAME.capitalize()} is trading...")
        sleep(3)  # 3 secs sleep to start the countdown

        # Check and Wait for the text "Check Results" TWICE to be visible on the screen after countdown
        for _ in range(2):
            with contextlib.suppress(TimeoutException, ValueError):
                trading_amount = float(
                    plubot.find_element(By.XPATH, '//div[@id="timer_buynum"]').text
                )
                exp_profit = float(
                    plubot.find_element(By.XPATH, '//div[@id="expected_profits"]').text
                )
                pluwait.until(
                    EC.visibility_of_element_located(
                        (By.XPATH, '//div[@class="wait_box_info"]')
                    )
                )
                break

        while True:
            plubot.get(plu_contract_record)
            gotoPage(plu_contract_record, plubot, NAME)
            numeric_vales = plubot.find_elements(
                By.XPATH, '//span[@class=" f12 fce5"]'
            )  # Numeric values
            evenStatus_OddDate: list = [
                i.text for i in plubot.find_elements(By.XPATH, status_date_xpath)
            ]

            with contextlib.suppress(AssertionError):
                status: str = evenStatus_OddDate[0]
                assert status == "Settled"
                break
            sleep(5)

        for idx, numeric_value in enumerate(numeric_vales):
            if idx == 3:  # The text 'Settled' is index 3
                profit: float = float(numeric_value.text)
                loss: float = 0.0
                break

        plubot.quit()

        if "-" in str(profit):
            loss = str(profit).split("-")[1]

        trade_output: str = f"{NAME}'S TRADE OUTCOME\n\nAuto trade initiated at {evenStatus_OddDate[1]}\nInitial balance = {initial_balance} NGN\nTrade amount = {trading_amount} NGN\nExpected profit = {exp_profit} NGN\n{'-'*30}\nStatus = {evenStatus_OddDate[0]}, {'Loss' if '-' in str(profit) else 'Profit'} = {loss if '-' in str(profit) else profit} NGN\nNew Balance = {initial_balance + profit} NGN\nAuto trade completed at {''.join(gmtTime(timezone).split(' '))}"

        print(trade_output)

        # Send to Self
        wa_bot.send_message(
            MY_NUMBER,
            trade_output,
            reply_markup=Inline_list(
                "Show list",
                list_items=[
                    List_item("Nice one 👌"),
                    List_item("Thanks ✨"),
                    List_item("Great Job"),
                ],
            ),
        )
        return "DONE."

    signal: dict = getSignal()
    print(f"WELCOME TO THE PLUTOMANIA WAYS 🎉\n{signal}\n")

    yAxis = 60
    coin: str = signal["coin"].lower()
    action: str = signal["action"].upper()
    actionbtn_xpath: str = f"//span[text()='{action}']"
    coin_link: str = f"{plu_base_url}index/trade/trans.html?sytx={coin}"

    SAMM_USER: Final = env_variable.get("SAMM_USER")
    SAMM_PASSWORD: Final = env_variable.get("SAMM_PASSWORD")
    ENI_USER: Final = env_variable.get("ENI_USER")
    ENI_PASSWORD: Final = env_variable.get("ENI_PASSWORD")
    EMMY_USER: Final = env_variable.get("EMMY_USER")
    EMMY_PASSWORD: Final = env_variable.get("EMMY_PASSWORD")
    MAMA_USER: Final = env_variable.get("MAMA_USER")
    MAMA_PASSWORD: Final = env_variable.get("MAMA_PASSWORD")

    with ThreadPoolExecutor(4, "Trading Thread") as executor:
        executor.submit(trade, "ENI", ENI_USER, ENI_PASSWORD, 0, yAxis)
        executor.submit(trade, "SAMM", SAMM_USER, SAMM_PASSWORD, 500, yAxis)
        executor.submit(trade, "EMMY", EMMY_USER, EMMY_PASSWORD, 1000, yAxis)
        executor.submit(trade, "MAMA", MAMA_USER, MAMA_PASSWORD, 0, 400)


if __name__ == "__main__":
    main()
