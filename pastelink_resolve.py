import json
import random
import requests
import time
from urlextract import URLExtract
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

PATH = 'C:/Program Files (x86)/chromedriver.exe'
options = webdriver.ChromeOptions()
options.add_argument('--ignore-certificate-errors')
options.add_argument('--ignore-ssl-errors')
options.add_argument("--disable-gpu")
options.add_argument("--disable-crash-reporter")
options.add_argument("--disable-extensions")
options.add_argument("--disable-in-process-stack-traces")
options.add_argument("--disable-logging")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--log-level=3")
options.headless = True

linkvertise_bypass_url = 'https://thebypasser.com/'
ex = URLExtract()

def resolve_bitly_to_mega(bitly_url):
    driver = webdriver.Chrome(executable_path=PATH, options=options, service_log_path='NUL')

    # Bitly -> Blogspot
    try:
        blogspot_url = requests.get(bitly_url).url

        # Blogspot -> Linkvertise
        driver.get(blogspot_url)
        if 'blogspot' in driver.current_url:
            time.sleep(13)
            button = driver.find_element_by_id('link')
            button.click()
        linkvertise_url = driver.current_url

        # Linkvertise -> Pastelink
        driver.get(linkvertise_bypass_url)
        text_input = driver.find_element_by_class_name('input_box')
        text_input.send_keys(linkvertise_url)
        text_input.send_keys(Keys.RETURN)
        button = driver.find_element_by_id('submit_btn')
        button.click()
        results = driver.find_element_by_id('results')
        time.sleep(2)
        pastelink_url = results.text
        print(f"Pastelink: {pastelink_url}")

        # Pastelink -> Bitly
        driver.get(pastelink_url)
        text_body = driver.find_element_by_class_name('body-display')
        urls = ex.find_urls(text_body.text)
        bitly_url = ''
        for url in urls:
            if 'bit.ly' in url:
                bitly_url = url
                break
        print(f"Bitly: {bitly_url}")

        # Bitly -> Mega
        driver.get(bitly_url)
        driver.close()
        driver.quit()
        return driver.current_url

        driver.close()
        driver.quit()
    except Exception as e:
        print("Something unexpected happened while processing a blogspot redirect :(")


def return_random_entry():
    with open('./cache.json', 'r') as f:
        data = json.load(f)
        link = data[random.randint(0, len(data) - 1)]['resolved']
        f.close()
    return link