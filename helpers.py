from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
import time
import pandas as pd
import os
import json
# from run import test_extract_jobs

def write_json(data, file_path):
    """
    Write a large array or any data structure to a JSON file.

    Parameters:
    data (any): The data to be written to the file.
    file_path (str): The path of the file where the data will be saved.
    """
    try:
        with open(file_path, 'w', encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False, indent=4)
        print(f"Data successfully written to {file_path}")
    except Exception as e:
        print(f"An error occurred: {e}")

def append_json(new_data, file_path):
    """
    Append data to a JSON file. If the file doesn't exist or is empty,
    it starts a new array. 

    Parameters:
    new_data (any): The data to be appended to the file.
    file_path (str): The path of the file where the data will be saved.
    """
    try:
        # Try to read the existing data
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
                if not isinstance(data, list):
                    print(f"Error: Data in {file_path} is not a list.")
                    return
        except (FileNotFoundError, json.JSONDecodeError):
            # If there's no file or file is empty, start a new list
            data = []

        # Append new data
        data.append(new_data)

        # Write back to file
        with open(file_path, 'w', encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False, indent=4)

        print(f"Data successfully appended to {file_path}")
    except Exception as e:
        print(f"An error occurred: {e}")


def read_json(file_path):
    """
    Read a JSON file that contains an array of dictionaries. For each top-level dictionary,
    retain the sub-keys that have non-empty values.

    Parameters:
    file_path (str): The path of the JSON file to be read.

    Returns:
    list: A list of dictionaries with filtered sub-keys.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
  
            return data
    except Exception as e:
        print(f"An error occurred: {e}")
        return []



def init_webdriver():
    # Setup Selenium to use Chrome
    s = Service(ChromeDriverManager().install())
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument('--log-level=3')  # Set log level to avoid most logs except fatal errors
    chrome_options.add_argument("--window-size=1920,1080")
    driver = webdriver.Chrome(service=s, options=chrome_options)
    return driver


def take_screenshot(driver, url, path):
    try:
        # Go to the website
        driver.get(url)

        # Wait for the page to load
        time.sleep(5)

        # Retrieve the dimensions of the entire page
        total_width = driver.execute_script("return document.body.offsetWidth")
        total_height = driver.execute_script("return document.body.parentNode.scrollHeight")

        # Resize window to capture the whole page
        driver.set_window_size(total_width, total_height)

        # Additional wait for the resize action
        time.sleep(3)

        # Take a screenshot
        driver.save_screenshot(path)
        print("Screenshot Saved")

    except Exception as e:
        print(f"An error occurred: {e}")


def close_webdriver(driver):
    # Close the browser and end the session
    driver.quit()


def check_stars(distinction):

    if distinction == "1 star":
        return 1
    elif distinction == '2 star':
        return 2
    elif distinction == '3 star':
        return 3
    else:
        return 0