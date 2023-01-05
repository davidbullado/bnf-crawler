from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementNotInteractableException
import os
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler()
    ]
)

username = os.getenv('BNF_USERNAME')
password = os.getenv('BNF_PASSWORD')


class BnfLoginException(Exception):
    """Base class for other exceptions"""
    pass


class EuropresseLoginException(Exception):
    """Base class for other exceptions"""
    pass


class NoArticleFound(Exception):
    pass


class RetryLaterException(Exception):
    pass


def login_bnf(driver):
    url = "https://authentification.bnf.fr/login"
    logging.debug("Log to BNF")
    driver.get(url)
    driver.find_element_by_id("username").send_keys(username)
    driver.find_element_by_id("password").send_keys(password)
    driver.find_element_by_xpath("//input[@type='submit' and @value='Me connecter']").click()


def connexion_is_valid(driver):
    url = "https://authentification.bnf.fr/login"
    logging.debug("Check validity of bnf...")
    driver.get(url)
    try:
        driver.find_element_by_class_name("deconnexion")
        logging.debug("bnf connection valid.")
    except NoSuchElementException:
        logging.debug("bnf connection not valid.")
        raise BnfLoginException


def login_europresse(driver):
    logging.debug("Login to europress")
    #driver.get('https://bnf.idm.oclc.org/login?url=http://nouveau.europresse.com/access/ip/default.aspx?un=bnf')
    driver.get('https://www.bnf.fr/fr/ressources-electroniques-de-presse')
    click_on_link('EUROPRESSE')


def europress_is_valid(driver):
    # driver.get('https://nouveau-europresse-com.bnf.idm.oclc.org/Search/Reading')
    logging.debug("Checking europress validity...")
    login_europresse(driver)
    if "authentification.bnf.fr" in driver.current_url:
        logging.debug("Bnf connection is invalid")
        raise BnfLoginException
    try:
        #driver.find_element_by_id("welcomeText")
        driver.find_element_by_id("Keywords")
        logging.debug("Europress connection is valid")
    except NoSuchElementException:
        logging.debug("Europress connection is invalid")
        raise EuropresseLoginException


def start_europresse(driver, max_try=2):
    if max_try <= 0:
        logging.debug("Maximum try exceeded")
        raise "Maximum try exceeded"
    try:
        europress_is_valid(driver)
    except EuropresseLoginException:
        login_europresse(driver)
        europress_is_valid(driver)
    except BnfLoginException:
        login_bnf(driver)
        start_europresse(driver, (max_try - 1))


def click_on_link(link_text):
    timeout = 5
    pause = 1
    element_present = EC.element_to_be_clickable((By.LINK_TEXT, link_text))
    WebDriverWait(driver, timeout).until(element_present)

    link = driver.find_element_by_link_text(link_text)

    for i in range(3):
        driver.execute_script('arguments[0].scrollIntoView();', link)
        pause += 1
        try:
            action = ActionChains(driver)
            action.move_to_element(link)
            action.click()
            action.pause(pause)
            action.perform()
        except ElementNotInteractableException:
            return
        try:
            link = driver.find_element_by_link_text(link_text)
        except NoSuchElementException:
            return
        if link is None:
            return
    raise Exception

def click_until_disappear_xpath(xpath):
    timeout = 5
    pause = 1
    element_present = EC.element_to_be_clickable((By.XPATH, xpath))
    WebDriverWait(driver, timeout).until(element_present)

    link = driver.find_element_by_xpath(xpath)
    driver.execute_script('arguments[0].scrollIntoView();', link)

    while link is not None:
        pause += 1
        try:
            action = ActionChains(driver)
            action.move_to_element(link)
            action.pause(0.5)
            action.click()
            action.pause(pause)
            action.perform()
        except ElementNotInteractableException:
            return
        try:
            link = driver.find_element_by_xpath(xpath)
        except NoSuchElementException:
            return

def error_screenshot(driver):
    screenshot = driver.get_screenshot_as_base64()
    img_tag = '<img src="data:image/png;base64,{}">'.format(screenshot)
    return img_tag

import re
def europresse_find_title(driver, title):
    start_europresse(driver)
    pattern = re.compile(r'[«»]')
    title = pattern.sub('', title)
    logging.debug(f"Find title {title}")
    driver.find_element_by_id('Keywords').send_keys(f'"{title}"')
    driver.find_element_by_id('btnSearch').click()

    timeout = 10
    try:
        element_present = EC.presence_of_element_located((By.CSS_SELECTOR, '#container > div.noResultFound'))
        WebDriverWait(driver, timeout).until(element_present)
    except TimeoutException:
        logging.error("Timed out waiting for page to load")
        raise RetryLaterException

    if driver.find_element_by_class_name('noResultFound').get_attribute('style') == 'display: inline-block;':
        raise NoArticleFound

    click_until_disappear_xpath('//*[@id="doc0"]/div[2]/div[2]/div[1]/a')

    timeout = 10
    try:
        element_present = EC.presence_of_element_located((By.ID, 'docText'))
        WebDriverWait(driver, timeout).until(element_present)
    except TimeoutException:
        logging.error("Timed out waiting for page to load")
        raise RetryLaterException

    driver.execute_script("""
       var l = Array.from(document.getElementsByTagName("mark"));
       l.forEach((item, index) => {
        t = document.createTextNode(item.innerText);
        item.parentNode.replaceChild(t, item);
       })
    """)

    elements = driver.find_elements_by_tag_name("img")
    # Itérez sur les balises img
    for element in elements:
        # Exécutez le script JavaScript qui remplace la balise img par une balise img avec les données en base64
        driver.execute_script('''
        var img = arguments[0];
        var canvas = document.createElement("canvas");
        canvas.width = img.width;
        canvas.height = img.height;
        var ctx = canvas.getContext("2d");
        ctx.drawImage(img, 0, 0);
        var dataURL = canvas.toDataURL("image/png");
        img.src = dataURL;
        ''', element)

    article_html = driver.find_element_by_xpath('//*[@id="docText"]/article').get_attribute("outerHTML")
    return article_html


options = Options()
options.add_argument("--headless")
options.add_argument("start-maximized")
options.add_argument("disable-infobars")
options.add_argument("--disable-extensions")
options.add_argument("--disable-gpu")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--no-sandbox")
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36")
options.add_argument("--window-size=1920,800")

driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)

if __name__ == "__main__":  # There is an error on this line
    europresse_find_title(driver, "Un an après le retour des talibans, le grand bond en arrière de l’Afghanistan")
    driver.quit()
    print('end')
