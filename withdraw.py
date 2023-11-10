import datetime
from time import sleep
from typing import Final
from selenium import webdriver
from dotenv import load_dotenv
from os import environ as env_variable
from python_whatsapp_bot import Whatsapp
from selenium.webdriver.common.by import By
from concurrent.futures import ThreadPoolExecutor
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException


def main():
    load_dotenv()

    TOKEN: Final = env_variable.get("TOKEN")  # Token
    NUM_ID: Final = env_variable.get("NUM_ID")  # Your Number ID
    MY_NUMBER: Final = env_variable.get(
        "MY_NUMBER"
    )  # Your WhatsApp Number (234xxxxxxxxxx)

    today = datetime.date.today()  # datetime.date(2023, 11, 4)
    todays_day = str(today).split('-')[2]  # 04

    plu_base_url: str = "https://pluapp.net/"
    driverpath: str = r"assets\drivers\chromedriver.exe"
    plu_homepage: str = plu_base_url + "index/index/index.html"
    plu_wallet_page: str = plu_base_url + "index/user/wallets.html"
    plu_withdraw_page: str = plu_base_url + "index/user/withdraw.html"
    wa_bot = Whatsapp(number_id=NUM_ID, token=TOKEN)

    def gotoPage(goto_link, plubot, NAME):
        while True:
            try:
                plubot.get(goto_link)  # Goto Page
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

    def withdraw(NAME, USERNAME, PASSWORD, xAxis, yAxis):

        print(f"{NAME.capitalize()}'s Plutomaia Withdrawal.")
        
        plubot_opts_args: list = [
            # '--headless',
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

        plubot.get(plu_wallet_page)

        if plubot.current_url not in plu_homepage:
            plubot.find_element(By.XPATH, '//input[@class="pml"]').send_keys(USERNAME)
            plubot.find_element(By.XPATH, '//input[@id="lpwd"]').send_keys(PASSWORD)
            plubot.find_element(By.XPATH, '//input[@name="submit"]').click()
            pluwait.until(EC.url_to_be(plu_homepage))

        assert plubot.current_url in plu_homepage
        print(f"Plutomania welcomes {NAME.capitalize()}. 😁")

        gotoPage(plu_wallet_page, plubot, NAME)

        balance = plubot.find_element(
            By.XPATH, '//span[@id="kymoney"]'
        ).text  # Balance
        total_deposit = plubot.find_element(
            By.XPATH, '//span[@id="zhmoney"]'
        ).text  # Total deposit        
        plubot.find_element(
            By.XPATH, '//div[@class="btnbox_b btnbg_a"]'
        ).click()  # Navigate to withdrawal page

        sleep(3)

        witdrawable_amt: float = (float(balance) - float(total_deposit)) / 1.2
        rounded_wth_amt: int = int(round(witdrawable_amt, -3))

        plubot.find_element(
            By.XPATH, '//input[@id="tbnum"]'
        ).send_keys(rounded_wth_amt)  # Input Amount
        # plubot.find_element(
        #     By.XPATH, '//div[@id="sumbtn"]'
        # ).click()  # Submit Button 
        
        gotoPage(plu_wallet_page, plubot, NAME)

        trx_name = plubot.find_elements(
            By.XPATH, '//span[@class="fe6im fzmm"]'
        )[2].text  # Transaction name
        new_balance = plubot.find_element(
            By.XPATH, '//span[@id="kymoney"]'
        ).text  # Balance
        trx_datetime = plubot.find_element(
            By.XPATH, '//span[@class="fe6im  f12  fzmm"]'
        ).text  # Transaction date and time
        trx_amt = plubot.find_element(
            By.XPATH, '//span[@class="fe6im f12 fzmmm"]'
        ).text  # Transaction amount

        # Convert string to datetime object
        datetime_object = datetime.datetime.strptime(trx_datetime, "%Y-%m-%d %H:%M:%S")

        # Format datetime in 12-hour clock format
        formatted_time = datetime_object.strftime("%Y-%m-%d %I:%M:%S %p")

        if 'Withdraw' in trx_name:
            latest_trx: str = f"{NAME.capitalize()} Successfully Made Withdrawal\nAt {formatted_time}\n\nWithdraw amount = {trx_amt[1:]}\nNew balance = {new_balance}"
            print(f"{'-'*35}\n{latest_trx}")
            wa_bot.send_message(MY_NUMBER, latest_trx)
            plubot.quit()
            return latest_trx
        else: print(f"{NAME.capitalize()} Withdrawal Failed.\n Calculated withdraw amount = {rounded_wth_amt}") 
        

    yAxis = 60
    max_workers: int = 1
    SAMM_USER: Final = env_variable.get("SAMM_USER")
    SAMM_PASSWORD: Final = env_variable.get("SAMM_PASSWORD")
    ENI_USER: Final = env_variable.get("ENI_USER")
    ENI_PASSWORD: Final = env_variable.get("ENI_PASSWORD")
    EMMY_USER: Final = env_variable.get("EMMY_USER")
    EMMY_PASSWORD: Final = env_variable.get("EMMY_PASSWORD")
    MAMA_USER: Final = env_variable.get("MAMA_USER")
    MAMA2_USER: Final = env_variable.get("MAMA2_USER")
    MAMA_PASSWORD: Final = env_variable.get("MAMA_PASSWORD")

    with ThreadPoolExecutor(max_workers=max_workers, thread_name_prefix="Withdraw Thread") as executor:
        # executor.submit(withdraw, "ENI", ENI_USER, ENI_PASSWORD, 0, yAxis)
        # executor.submit(withdraw, "SAMM", SAMM_USER, SAMM_PASSWORD, 500, yAxis)
        executor.submit(withdraw, "EMMY", EMMY_USER, EMMY_PASSWORD, 1000, yAxis)
        # executor.submit(withdraw, "MAMA", MAMA_USER, MAMA_PASSWORD, 0, 400)


if __name__ == "__main__":
    main()

