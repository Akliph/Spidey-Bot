import random

import requests
import os
import json
import time
import json
from pprint import pprint
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


def retrieve_messages(channel_id):
    headers = {
        'authorization': 'ODU4MDM5MzA1MDI5Mjg3OTY2.YNYW_Q.D5Hh5Q8cVWLis5F9r8L52yVQQRs'
    }

    r = requests.get(f'https://discord.com/api/v9/channels/{channel_id}/messages', headers=headers)

    response = json.loads(r.text)

    return response


def resolve_bitly_to_mega(bitly_url):
    driver = webdriver.Chrome(executable_path=PATH, options=options, service_log_path='NUL')

    # Bitly -> Blogspot
    try:
        blogspot_url = requests.get(bitly_url).url
    except:
        print("Could not get link from entry, returning previous entry: ")
        return return_random_entry()

    try:
        # Blogspot -> Linkvertise
        driver.get(blogspot_url)
        if 'blogspot' in driver.current_url:
            time.sleep(13)
            button = driver.find_element_by_id('link')
            button.click()
        linkvertise_url = driver.current_url
        if 'linkvertise' not in linkvertise_url:
            print("Not correct link tree, resolving to previous entry: ")
            print(f"Returned on unexpected link: {linkvertise_url}")
            return return_random_entry()
        print(f"Linkvertise: {linkvertise_url}")
    except:
        return return_random_entry()

    try:
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
        if 'pastelink' not in pastelink_url:
            print("Not correct link tree, resolving to previous entry: ")
            print(f"Returned on unexpected link: {linkvertise_url}")
            return return_random_entry()
        print(f"Pastelink: {pastelink_url}")
    except:
        return return_random_entry()

    try:
        # Pastelink -> Bitly
        driver.get(pastelink_url)
        text_body = driver.find_element_by_class_name('body-display')
        urls = ex.find_urls(text_body.text)
        bitly_url = ''
        for url in urls:
            if 'bit.ly' in url:
                bitly_url = url
                break
        if bitly_url == '':
            return return_random_entry()
        print(f"Bitly: {bitly_url}")
    except:
        return return_random_entry()

    try:
        # Bitly -> Mega
        driver.get(bitly_url)
        driver.close()
        driver.quit()
        return driver.current_url
    except:
        l = return_random_entry()
        driver.close()
        driver.quit()
        return l


def add_link_to_cache(unresolved, resolved):
    with open('./cache.json', 'r+') as f:
        data = json.load(f)

        data.append(
            {
                'unresolved': unresolved,
                'resolved': resolved
            }
        )

        f.seek(0)
        json.dump(data, f, indent=4)
        f.truncate()
        f.close()


def pull_link_from_cache(unresolved):
    with open('./cache.json', 'r') as f:
        if os.stat('./cache.json').st_size == 0:
            return False

        data = json.load(f)

        for link in data:
            if link['unresolved'] == unresolved:
                return link['resolved']

        return False


def return_random_entry():
    with open('./cache.json', 'r') as f:
        data = json.load(f)
        link = data[random.randint(0, len(data) - 1)]['resolved']
        f.close()
    return link


if __name__ == '__main__':
    print(len(retrieve_messages(796166200555470878)))
    # start_time = time.time()
    # print(resolve_bitly_to_mega('https://bit.ly/2TRuQ3D'))
    # print(f'It took: {time.time() - start_time}')
    pass
