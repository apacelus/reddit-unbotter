# Selenium for firefox
import logging
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, ElementClickInterceptedException
from selenium.webdriver.firefox.service import Service as FirefoxService
from webdriver_manager.firefox import GeckoDriverManager
from time import sleep
from json import load as json_load
from random import uniform, randint

if __name__ == "selenium_wrapper.firefox":
    base_xpath = "/html/body/div[1]/div/div[2]/div[2]/div/div/div/div[2]/div[2]/div[1]/div[5]/div["
    with open('./config/settings.json', 'r') as file:
        settings_json = json_load(file)
    driver_options = webdriver.FirefoxOptions()
    driver_options.binary_location = settings_json["browser_path"]
    driver_options.add_argument("--incognito")
    driver = webdriver.Firefox(log_path="./logs/driver.log", service=FirefoxService(GeckoDriverManager().install()),
                               options=driver_options)
    driver.minimize_window()
    wait = WebDriverWait(driver, 10)


def get_session_cookie(username, password):
    driver.get("https://www.reddit.com/login/")
    driver.find_element(By.ID, 'loginUsername').send_keys(username)
    driver.find_element(By.ID, 'loginPassword').send_keys(password)
    sleep(1)
    driver.find_element(By.XPATH, '/html/body/div/main/div[1]/div/div[2]/form/fieldset[5]/button').click()
    sleep(5)
    session_cookie = driver.get_cookie("reddit_session")["value"]
    logging.debug(driver.get_cookie("reddit_session"))
    driver.delete_all_cookies()
    driver.refresh()
    return session_cookie


def delete_top_bar():
    try:
        driver.execute_script("""
        var element = arguments[0];
        element.parentNode.removeChild(element);
        """, driver.find_element(By.XPATH, "/html/body/div[1]/div/div[2]/div[1]/header"))
        logging.debug("Deleted top bar!!!")
    except NoSuchElementException:
        logging.warning("Couldnt find top bar")


def login_account(session_cookie, username):
    logging.info("Logging in account: " + username)
    logging.debug("Session cookie: " + session_cookie)
    driver.get("https://www.reddit.com/")
    driver.add_cookie(
        {'name': 'reddit_session', 'value': session_cookie, 'path': '/', 'domain': 'reddit.com', 'secure': True,
         'httpOnly': True, 'sameSite': 'None'})
    # cookie denial cookie, to get rid of cookie prompt
    driver.add_cookie(
        {'name': 'eu_cookie', 'value': "{%22opted%22:true%2C%22nonessential%22:false}", 'path': '/',
         'domain': 'reddit.com', 'secure': False,
         'httpOnly': False, 'sameSite': 'None'})
    driver.get("https://www.reddit.com/u/me")
    try:
        wait.until(ec.url_to_be('https://www.reddit.com/user/' + username + "/"))
        driver.get("https://www.reddit.com/")
        delete_top_bar()
    except TimeoutError:
        logging.warning("Couldnt login as user: " + username)
        driver.delete_all_cookies()
        return False
    # removing reddit popup
    try:
        driver.find_element(By.XPATH,
                            "/html/body/div[1]/div/div[2]/div[2]/div/div/div/div[2]/div[2]/div[1]/div[1]/button").click()
        logging.info("Removed reddit suggestion")
    except NoSuchElementException:
        pass


def scroll_to_next_post(post_id):
    driver.execute_script("return arguments[0].scrollIntoView();",
                          driver.find_element(By.XPATH, base_xpath + str(post_id) + ']'))
    try:
        if "promotedlink" in driver.find_element(By.XPATH, base_xpath + str(post_id) + "]/div/div").get_attribute(
                "class"):
            logging.info("Found ad post, skipping")
            post_id += 1
            return scroll_to_next_post(post_id)
        else:
            return post_id
    except NoSuchElementException:
        logging.warning("Found broken post")
        post_id += 1
        return scroll_to_next_post(post_id)


def upvote_post(post_id):
    try:
        driver.find_element(By.XPATH, base_xpath + str(post_id) + "]/div/div/div[2]/div/button[1]").click()
    except ElementClickInterceptedException:
        delete_top_bar()
        driver.find_element(By.XPATH, base_xpath + str(post_id) + "]/div/div/div[2]/div/button[1]").click()
    except NoSuchElementException:
        logging.warning("Couldnt find downvote button, trying alternate path")
        driver.find_element(By.XPATH, base_xpath + str(post_id) + "]/div/div/div/div/div[2]/div/button[1]").click()


def downvote_post(post_id):
    try:
        driver.find_element(By.XPATH, base_xpath + str(post_id) + "]/div/div/div[2]/div/button[2]").click()
    except ElementClickInterceptedException:
        delete_top_bar()
        driver.find_element(By.XPATH, base_xpath + str(post_id) + "]/div/div/div[2]/div/button[2]").click()
    except NoSuchElementException:
        logging.warning("Couldnt find downvote button, trying alternate path")
        driver.find_element(By.XPATH, base_xpath + str(post_id) + "]/div/div/div/div/div[2]/div/button[2]").click()


def enter_comments(post_num):
    try:
        driver.find_element(By.XPATH, base_xpath + str(post_num) + "]/div/div/div[3]/div[5]/div[2]/a").click()
    except NoSuchElementException:
        logging.warning("Couldnt find comment button, trying alternate path")
        driver.find_element(By.XPATH, base_xpath + str(post_num) + "]/div/div/div/div/div[3]/div[5]/div[2]/a").click()


def scroll_comments(amount):
    counter = 1
    try:
        while counter <= amount:
            print(
                '/html/body/div[1]/div/div[2]/div[3]/div/div/div/div[2]/div[1]/div[3]/div[5]/div/div/div/div[' + str(
                    counter) + ']')
            driver.execute_script("return arguments[0].scrollIntoView();", driver.find_element(By.XPATH,
                                                                                               '/html/body/div[1]/div/div[2]/div[3]/div/div/div/div[2]/div[1]/div[3]/div[5]/div/div/div/div[' + str(
                                                                                                   counter) + ']'))
            counter += randint(1, 3)
            sleep(uniform(2, 4))
    except NoSuchElementException:
        logging.info("Couldnt find next comment, using alt path")
        try:
            while counter <= amount:
                print(
                    '/html/body/div[1]/div/div[2]/div[3]/div/div/div/div[2]/div[1]/div[3]/div[6]/div/div/div/div[' + str(
                        counter) + ']')
                driver.execute_script("return arguments[0].scrollIntoView();", driver.find_element(By.XPATH,
                                                                                                   '/html/body/div[1]/div/div[2]/div[3]/div/div/div/div[2]/div[1]/div[3]/div[6]/div/div/div/div[' + str(
                                                                                                       counter) + ']'))
                sleep(uniform(2, 4))
                counter += randint(1, 3)
        except NoSuchElementException:
            logging.info("Couldnt find next comment, probably no more comments")
            driver.execute_script("window.history.go(-1)")
            sleep(2)
            return counter


def write_comment(comment):
    WebDriverWait(driver, 10).until(ec.element_to_be_clickable(
        (By.XPATH,
         "/html/body/div[1]/div/div[2]/div[3]/div/div/div/div[2]/div[1]/div[3]/div[3]/div[2]/div/div/div[2]/div/div[1]/div/div/div"))).send_keys(
        comment)
    driver.find_element(By.XPATH,
                        "/html/body/div[1]/div/div[2]/div[3]/div/div/div/div[2]/div[1]/div[3]/div[3]/div[2]/div/div/div[3]/div[1]/button").click()
