from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException, NoSuchElementException

import configparser
config = configparser.RawConfigParser()
config.read('.secret')

class BnfLoginException(Exception):
    """Base class for other exceptions"""
    pass

class EuropresseLoginException(Exception):
    """Base class for other exceptions"""
    pass

class NoArticleFound(Exception):
    pass

def login_bnf(driver):
    url = "https://authentification.bnf.fr/login"

    username = config.get('Login','username')
    password = config.get('Login','password')

    driver.get(url)
    driver.find_element_by_id("username").send_keys(username)
    driver.find_element_by_id("password").send_keys(password)
    driver.find_element_by_xpath("//input[@type='submit' and @value='Me connecter']").click()


def connexion_is_valid (driver):
    url = "https://authentification.bnf.fr/login"
    driver.get(url)
    try:
        driver.find_element_by_class_name("deconnexion")
    except NoSuchElementException:
        raise BnfLoginException


def login_europresse (driver):
    driver.get('https://bnf.idm.oclc.org/login?url=http://nouveau.europresse.com/access/ip/default.aspx?un=bnf')


def europress_is_valid (driver):
    driver.get('https://nouveau-europresse-com.bnf.idm.oclc.org/Search/Reading')

    if "authentification.bnf.fr" in driver.current_url:
        raise BnfLoginException

    try:
        driver.find_element_by_id("welcomeText")
    except NoSuchElementException:
        raise EuropresseLoginException


def start_europresse (driver, max_try=2):
    if max_try <= 0:
        raise "Maximum try exceeded"
    try:
        europress_is_valid(driver)
    except EuropresseLoginException:
        login_europresse(driver)
        europress_is_valid(driver)
    except BnfLoginException:
        login_bnf(driver)
        start_europresse(driver, (max_try-1))


def europresse_find_title(driver, title):
    start_europresse(driver)

    driver.find_element_by_id('Keywords').send_keys(title)
    driver.find_element_by_id('btnSearch').click()

    timeout = 5
    try:
        element_present = EC.presence_of_element_located((By.ID, 'chbdoc-0-0'))
        WebDriverWait(driver, timeout).until(element_present)
    except TimeoutException:
        print("Timed out waiting for page to load")

    try:
        action = ActionChains(driver)
        # Select firt article
        article = driver.find_element_by_xpath('//*[@id="doc0"]/div[2]/div[2]/div[1]/a')
        action.move_to_element(article)
        action.click()
        action.perform()
    except NoSuchElementException:
        raise NoArticleFound

    timeout = 5
    try:
        element_present = EC.presence_of_element_located((By.ID, 'docText'))
        WebDriverWait(driver, timeout).until(element_present)
    except TimeoutException:
        print("Timed out waiting for page to load")

    driver.execute_script("""
       var l = Array.from(document.getElementsByTagName("mark"));
       l.forEach((item, index) => {
        t = document.createTextNode(item.innerText);
        item.parentNode.replaceChild(t, item);
       })
    """)

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

driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)


if __name__ == "__main__":  # There is an error on this line
    europresse_find_title(driver, "Un an après le retour des talibans, le grand bond en arrière de l’Afghanistan")

    print('end')