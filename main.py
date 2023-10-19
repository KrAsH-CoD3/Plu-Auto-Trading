from datetime import datetime
from selenium import webdriver
from typing import Optional, Dict
import contextlib, pyautogui, pytz
from time import sleep, perf_counter
from os import environ as env_variable
from selenium.webdriver.common.by import By
from art import tprint, set_default, text2art
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
    ...

if __name__ == "__main__":
    main()