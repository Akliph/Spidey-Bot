import base64
import requests
import time
import json
import os
import urlextract
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

PATH = 'C:/Program Files (x86)/chromedriver.exe'
options = webdriver.ChromeOptions()
options.add_argument('--ignore-certificate-errors')
options.add_argument('--ignore-ssl-errors')
options.add_argument("--disable-notifications")
options.add_argument("--disable-gpu")
options.add_argument("--disable-crash-reporter")
options.add_argument("--disable-extensions")
options.add_argument("--disable-in-process-stack-traces")
options.add_argument("--disable-logging")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--log-level=3")
options.headless = True

linkvertise_bypass_url = 'https://thebypasser.com/'
ex = urlextract.URLExtract()
captcha_solver_api_key = '6ea633785283bda2fc25bd70ee678275'


def resolve_entire_link(bitly_url):
    pastelink_url = resolve_binbucks_to_linkvertise(bitly_url)

    if pastelink_url:
        final_link = resolve_pastelink_to_mega(pastelink_url)
    else:
        print("Binbucks resolve failed")
        return False

    if type(final_link) is not str:
        return False

    return final_link


def resolve_binbucks_to_linkvertise(bitly_url):
    driver = webdriver.Chrome(options=options, executable_path=PATH, service_log_path='NUL')
    driver.get(bitly_url)

    # If website uses alert, dismiss it
    try:
        alert = driver.switch_to.alert
        alert.dismiss()
    except:
        print("No Alert")
    time.sleep(5)

    # Image captcha check
    try:
        captcha_confirm = driver.find_element_by_id("globalCaptchaConfirm")
        captcha_confirm.click()
        time.sleep(2)

        global_captcha_div = driver.find_element_by_id("globalCaptchaQuestions")
        print(f"Global Div: {global_captcha_div}")

        captcha_images = global_captcha_div.find_elements_by_class_name("markAnswer")

        for i in range(3):
            current_word = driver.find_element_by_id("currentCapQue").text
            print(f"Current word: {current_word}")

            for captcha_image in captcha_images:
                if str(captcha_image.get_attribute('data-id')) == str(current_word):
                    captcha_image.click()
                    continue
            time.sleep(2)

        driver.find_element_by_name('open').click()
        time.sleep(1)

        pastelink_url = get_url_from_solved_page(driver)
        print(f"Result found: {pastelink_url}")

        driver.close()
        driver.quit()

        return pastelink_url
    except:
        print("This is not an image captcha...")

    # Word captcha
    try:
        # Word captcha
        frame_div = driver.find_element_by_id("adcopy-puzzle-image-image")
        iframe = frame_div.find_element_by_tag_name("iframe")
        print(f"iFrame id: {iframe.get_attribute('id')}")
        driver.switch_to.frame(iframe.get_attribute('id'))

        try:
            # Has play button
            play_button = driver.find_element_by_id("play_button")
            print("This is a word captcha with a play button...")
            play_button.click()
            time.sleep(18)
            captcha_image = driver.find_element_by_id('overlay')
            captcha_image.screenshot('word_captcha_screenshot.png')
        except Exception as e:
            time.sleep(15)
            captcha_image = driver.find_element_by_id('overlay')
            captcha_image.screenshot('word_captcha_screenshot.png')
            time.sleep(2)

        # Send a post request with the image encoded in Base64, and get the transaction ID as a result
        captcha_text = solve_captcha_with_image(captcha_solver_api_key,
                                                'word_captcha_screenshot.png',
                                                'please input the white text, thank you <3')

        if not captcha_text:
            return False

        driver.switch_to.default_content()
        return_to_page_btn = driver.find_element_by_id('adcopy-page-return')
        return_to_page_btn.click()
        captcha_form = driver.find_element_by_id('binbucksCaptcha')
        text_input_div = captcha_form.find_element_by_class_name('col-md-12')
        text_input_div = text_input_div.find_element_by_id('adcopy-response-cell')
        text_input = text_input_div.find_element_by_tag_name('input')
        text_input.send_keys(captcha_text)

        driver.find_element_by_name('open').click()
        time.sleep(1)

        pastelink_url = get_url_from_solved_page(driver)
        print(f"Result found: {pastelink_url}")

        driver.close()
        driver.quit()

        return pastelink_url
    except Exception as e:
        print("This is not a word captcha...")

    # Spelling captcha
    try:
        captcha_img = driver.find_element_by_id("my-captcha-image")
        print("This is a spelling captcha...")
        captcha_img.screenshot('spelling_captcha_screenshot.png')
        captcha_text = solve_captcha_with_image(captcha_solver_api_key,
                                                'spelling_captcha_screenshot.png',
                                                'please enter the text shown, thank you very much <3')

        if not captcha_text:
            return False

        time.sleep(1)
        input_box = driver.find_element_by_id('dynamicmodel-verificationcode')
        input_box.send_keys(captcha_text)
        driver.find_element_by_name('open').click()
        time.sleep(1)

        pastelink_url = get_url_from_solved_page(driver)
        print(f"Result found: {pastelink_url}")

        driver.close()
        driver.quit()

        return pastelink_url
    except:
        print("This is not a spelling captcha...")

    # reCaptcha captcha
    try:
        recaptcha_div = driver.find_element_by_class_name('g-recaptcha')
        print("This is a reCaptcha captcha...")

        sitekey_container = driver.find_element_by_xpath('/html/body/div[4]/div/div/div[1]/div[2]'
                                                         '/form/div[1]/center/div[2]/div')
        sitekey = sitekey_container.get_attribute('data-sitekey')
        print(f"Sitekey: {sitekey}")
        print(f"Url: {driver.current_url}")

        print("Posting recaptcha data to 2captcha...")
        captcha_answer = solve_recaptchav2_with_2captcha(captcha_solver_api_key, sitekey, driver.current_url)
        if not captcha_answer:
            return False
        print(captcha_answer)
        print("Captcha key received, attempting to inject captcha_answer into DOM")
        captcha_response_container = driver.find_element_by_id('g-recaptcha-response')
        print('Got captcha response container')
        driver.execute_script("arguments[0].setAttribute('style',"
                              " 'width: 250px; "
                              "height: 40px; border: 1px solid rgb(193, 193, 193); "
                              "margin: 10px 25px; "
                              "padding: 0px; "
                              "resize: none;') ", captcha_response_container)
        driver.execute_script(f'arguments[0].innerHTML = "{captcha_answer}"', captcha_response_container)
        print("Javascript injection complete...")

        captcha_form = driver.find_element_by_id('binbucksCaptcha')
        print("Got captcha form")
        # driver.execute_script('arguments[0].submit()', captcha_form)
        print("Submitted captcha form")

        time.sleep(5)
        driver.find_element_by_name('open').click()
        time.sleep(1)

        pastelink_url = get_url_from_solved_page(driver)
        print(f"Result found: {pastelink_url}")

        driver.close()
        driver.quit()

        return pastelink_url
    except:
        print("This is not a recaptcha")

    driver.close()
    driver.quit()

    return False


def resolve_pastelink_to_mega(linkvertise_url):
    driver = webdriver.Chrome(options=options, executable_path=PATH, service_log_path='NUL')

    print("Resolving redirect to mega link...")
    try:
        driver.get(linkvertise_url)
        linkvertise_url = driver.current_url
        print("Got redirect from link...")

        print("Accessing bypasser website...")
        driver.get(linkvertise_bypass_url)
        print("Bypass website accessed...")
        text_input = driver.find_element_by_class_name('input_box')
        text_input.send_keys(linkvertise_url)
        text_input.send_keys(Keys.RETURN)
        print("Request input and sent...")
        button = driver.find_element_by_id('submit_btn')
        print("Bitly link being accessed...")
        button.click()
        results = driver.find_element_by_id('results')
        time.sleep(2)
        pastelink_url = results.text
        print("Got link from pastelink...")

        print("Getting pastelink bitly redirect...")
        driver.get(pastelink_url)
        text_body = driver.find_element_by_class_name('body-display')
        urls = ex.find_urls(text_body.text)
        bitly_url = ''
        for url in urls:
            if 'bit.ly' in url:
                bitly_url = url
                break

        print("Finding bitly redirect...")
        driver.get(bitly_url)
        mega_url = driver.current_url
        print("Bitly redirect found!")
        driver.close()
        driver.quit()

        return mega_url
    except Exception as e:
        return False


def perform_2captcha_request(api_key, path_to_image, text_instructions):
    # Send a post request with the image encoded in Base64, and get the transaction ID as a result
    with open(path_to_image, 'rb') as f:
        post_data = {
            'key': api_key,
            'method': 'base64',
            'body': base64.b64encode(f.read()),
            'textinstructions': text_instructions,
            'json': 1
        }

    print("Sending captcha data to 2captcha...")
    res = requests.post('http://2captcha.com/in.php', post_data)
    print(f"Response: {res.text}")

    res_json = json.loads(res.text)

    if res_json['status'] == 1:
        captcha_id = res_json['request']
    else:
        return False

    print("Waiting 10 seconds for server to process data...")

    get_body = {
        'key': captcha_solver_api_key,
        'action': 'get',
        'id': captcha_id,
        'json': 1
    }

    while True:
        time.sleep(10)
        print("Requesting response data...")
        res = requests.get('http://2captcha.com/res.php', get_body)
        print(f"Response: {res.text}")

        res_json = json.loads(res.text)

        if res_json['status'] == 1:
            captcha_text = res_json['request']
            break
        elif res_json['request'] == "CAPCHA_NOT_READY":
            print("Captcha not ready, waiting another 10 seconds...")
        elif res_json['request'] == 'ERROR_CAPTCHA_UNSOLVABLE':
            captcha_text = 'ERROR_CAPTCHA_UNSOLVABLE'
            break
        else:
            return False

    return captcha_text


def solve_captcha_with_image(api_key, path_to_image, text_instructions):
    for i in range(5):
        res = perform_2captcha_request(api_key, path_to_image, text_instructions)
        if res != "ERROR_CAPTCHA_UNSOLVABLE":
            break
        print(f"Worker reported that the captcha was unsolvable, resending request... [Attempt {i + 1}/5]")

    if res == "ERROR_CAPTCHA_UNSOLVABLE":
        return False

    return res


def perform_recaptchav2_request(api_key, sitekey, page_url):
    post_body = {
        'key': api_key,
        'method': 'userrecaptcha',
        'googlekey': sitekey,
        'pageurl': page_url,
        'json': 1
    }

    res = requests.post('http://2captcha.com/in.php', post_body)
    print(f"POST Response: {res.text}")

    res_json = json.loads(res.text)

    if res_json['status'] == 1:
        captcha_id = res_json['request']
    else:
        return False

    get_body = {
        'key': api_key,
        'action': 'get',
        'id': captcha_id,
        'json': 1
    }

    print('Waiting 10 seconds for server to process data...')

    while True:
        time.sleep(10)
        res = requests.get('http://2captcha.com/res.php', get_body)
        print(f"GET Response: {res.text}")

        res_json = json.loads(res.text)

        if res_json['status'] == 1:
            return res_json['request']
        elif res_json['request'] == "CAPCHA_NOT_READY":
            print("Captcha not ready, waiting another 10 seconds...")
        elif res_json['request'] == 'ERROR_CAPTCHA_UNSOLVABLE':
            captcha_text = 'ERROR_CAPTCHA_UNSOLVABLE'
            break
        else:
            return False

    return captcha_text


def solve_recaptchav2_with_2captcha(api_key, sitekey, page_url):
    for i in range(5):
        res = perform_recaptchav2_request(api_key, sitekey, page_url)
        if res != "ERROR_CAPTCHA_UNSOLVABLE":
            break
        print(f"Worker reported that the captcha was unsolvable, resending request... [Attempt {i + 1}/5]")

    if res == "ERROR_CAPTCHA_UNSOLVABLE":
        return False

    return res


def get_url_from_solved_page(driver_reference):
    text_div = driver_reference.find_element_by_id("template-contactform-message")
    link_tag = text_div.find_element_by_tag_name("a")
    url = link_tag.get_attribute('href')
    return url


# WIP
def cache_captcha_word_image(image_url, text):
    if not os.path.isfile('word_captcha_cache.json'):
        with open('word_captcha_cache.json', 'w+') as f:
            data = []
            json.dump(data, f)
            f.close()

    with open('word_captcha_cache.json', 'r') as f:
        data = json.load(f)
        f.close()

    with open('word_captcha,json', 'w+') as f:
        data.append((image_url, text))
        json.dump(data, f)
        f.close()


def pull_word_from_word_cache(image_url):
    with open('word_captcha_cache.json') as f:
        data = json.load(f)
        for entry in data:
            if image_url == entry[0]:
                return entry[1]

    return False


if __name__ == "__main__":
    pastelink_url = resolve_binbucks_to_linkvertise('https://www.binbucks.com/site/confirm?code=jNP27a18K3')

    if pastelink_url:
        print(resolve_pastelink_to_mega(pastelink_url))
    else:
        print("Binbucks resolve failed")
