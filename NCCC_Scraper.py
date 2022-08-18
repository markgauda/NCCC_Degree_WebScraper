"""
This program was created by Mark Gauda in June of 2022
The purpose of this program is to go thorough all of my NCCC
degree paths and see which one I am closest to
"""
import os
import sys
import selenium
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import Scraper
import time
import re
import logging


def login_loop(driver):
    #go to degree works
    driver.get("https://www.niagaracc.suny.edu/academics/evaluation/")
    try:
        driver.find_element(By.CSS_SELECTOR, ".regular-button").click()
    except:
        java_script = "document.querySelectorAll('.large.regular-button')[0].click()"
        driver.execute_script(java_script)
    WebDriverWait(driver, 60).until(
        EC.presence_of_element_located((By.ID, "username"))
    )
    driver.find_element(By.ID, "username").send_keys(sys.argv[1])
    driver.find_element(By.ID, "password").send_keys(sys.argv[2])
    driver.find_element(By.CSS_SELECTOR, ".wr-btn").submit()
    




def main_loop(driver):
    WebDriverWait(driver, 60).until(
        EC.presence_of_element_located((By.ID, "what-if"))
    )
    time.sleep(2)
    driver.find_element(By.ID, "what-if").click()
    WebDriverWait(driver, 60).until(
        EC.presence_of_element_located((By.ID, "major_label_value"))
    )
    time.sleep(2)
    try:
        driver.find_element(By.ID, "catalogYear_label_value").click()
    except:
        driver.find_element(By.ID, "WhatIfWorksheetMode").click()
        driver.find_element(By.ID,"catalogYear_label_value").click()
    java_script = "document.querySelectorAll('li')[3].click()" #Hard coding the location of the current semester
    driver.execute_script(java_script)
    try:
        driver.find_element(By.ID, "major_label_value").click()
    except:
        driver.find_element(By.ID, "WhatIfWorksheetMode").click()
        driver.find_element(By.ID,"major_label_value").click()
    list_elements = driver.find_elements(By.TAG_NAME, "li")
    list_element_names = list()
    for name in list_elements:
        list_element_names.append(name.text)
    for count in range(len(list_elements)):
        if count <= 1:
            continue

        #print the name of the class
        try:
            print_class_name(list_element_names[count])
            #print(list_element_names[count], end=': ')
            element_printed = True
        except Exception as exception:
            #print("Could not print text?", exception)
            pass
        time.sleep(.25)


        # we need to click on the element
        click_on_element(driver, count)
        

        #we need to click on the button
        time.sleep(1)
        press_button(driver)

        #We need to get the credit hours
        get_credit_hours(driver)
        

def get_credit_hours(driver):
    """The simple aproach to getting the credits
    This looks for the location of the page
    that tells you how many credits you still
    need to get this degree.
    This has the side effect of printing or saving
    the value found

    Args:
        driver (WebDriver): Selenium WebDriver

    Returns:
        None: None
    """
    try:
        #Wait for the 'credits needed' message to load
        WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.XPATH, "//div[@id='WhatIf']/div[3]/div/div[5]/div[1]/div[1]/div[2]/div[1]/div[1]/div[1]/div[1]/div[1]/div[1]/div[2]/div[1]/p"))
            )
    except:
        #Could not find the 'credits needed' message at the given xpath, try the second method
        get_credits_second_try(driver)
        return None
    needed_credits = driver.find_element(By.XPATH, "//div[@id='WhatIf']/div[3]/div/div[5]/div[1]/div[1]/div[2]/div[1]/div[1]/div[1]/div[1]/div[1]/div[1]/div[2]/div[1]/p")
    credits_text = needed_credits.text
    try:
        #test if the string gathered was correct
        assert "Credits needed" in credits_text
        print_credits(re.findall('[0-9]+', credits_text)[0])
    except:
        #if the string was wrong, then try the second method
        get_credits_second_try(driver)

def get_credits_second_try(driver):
    """This is a different aproach to getting
    the credit hours needed. This will look in
    the webpage for where you are told how many
    credits are needed, and how many credits you
    have, then this will spit out the difference.
    This has the side effect of printing or saving
    the value found

    Args:
        driver (WebDriver): Selenium WebDriver

    Returns:
        None: None
    """
    try:
        #locate the 'credits have' text at the xpath
        WebDriverWait(driver, 30).until(
            EC.presence_of_all_elements_located((By.XPATH,"(//div[@id='WhatIf']/div[3]/div/div[4]/div/div/div/div/div/div/span)[2]"))
        )
    except:
        logging.error("Could not find 'credits_have'")

    try:
        #We found the given xpath, now lets get its info
        #note that this is the third entry of xpath matches
        java_script = "return document.evaluate(\"(//div[@id='WhatIf']/div[3]/div/div[4]/div/div/div/div/div/div/span)[2]\", document.querySelector('html')).iterateNext().textContent"
        credits_have = str(driver.execute_script(java_script))
        credits_have = re.findall('[0-9]+', credits_have)[0]
        credits_have = int(credits_have)
        #note this is the second endry of xpath matches
        java_script = "return document.evaluate(\"(//div[@id='WhatIf']/div[3]/div/div[4]/div/div/div/div/div/div/span)[1]\", document.querySelector('html')).iterateNext().textContent"
        credits_need = str(driver.execute_script(java_script))
        credits_need = re.findall('[0-9]+', credits_need)[0]
        credits_need = int(credits_need)
        credit_difference = credits_need - credits_have
        print_credits(credit_difference)
    except Exception as exception:
        #catch all, perhaps the xpath was not good enough, you you already have the degree
        logging.info(exception)
        if test_if_have_degree(driver) == True:
            print_credits(0)
        else:
            logging.error("could not find credits")
            print_credits(0)

def test_if_have_degree(driver):
    """This will test the web page to see if you 
    have already completed the degree. If you have
    This will return True, else Flase

    Args:
        driver (WebDriver): Selenium WebDiver

    Returns:
        Bool: True if you have the degree
    """
    #Look for the 'degree complete' message
    java_script = "return document.evaluate(\"//div[@id='WhatIf']/div[3]/div/div[4]/div/div/div/div/div/h2/span[2]\", document.querySelector('html')).iterateNext().textContent"
    status = credits_have = str(driver.execute_script(java_script))
    if status == "COMPLETE":
        return True
    else:
        return False

def print_credits(number: int):
    print(number)

def print_class_name(class_name: str):
    print(class_name, end=":\t")




def click_on_element(driver, count = 0):
    """This will click on the given list element on the NCCC degree works page

    Args:
        driver (_type_): _description_
        count (int, optional): _description_. Defaults to 0.
    """
    #We are using JS to do the clicking to bypass selenium sensativity
    element_clicked = False
    try:
        #The simplest click attempt
        java_script = "document.querySelectorAll('li')[{index}].click()".format(index = count)
        driver.execute_script(java_script)
        element_clicked = True
    except:
        pass
    if element_clicked == False:
        try:
            #Perhaps the 'major label' list isn't open, lets try to open it
            driver.find_element(By.ID, "major_label").click()
            java_script = "document.querySelectorAll('li')[{index}].click()".format(index = count)
            driver.execute_script(java_script)
            element_clicked = True
        except:
            pass
    if element_clicked == False:
        try:
            #Maybe the "what if worksheet" isn't open, lets try to open it
            driver.find_element(By.ID, "WhatIfWorksheetMode").click()
            driver.find_element(By.ID, "major_label").click()
            java_script = "document.querySelectorAll('li')[{index}].click()".format(index = count)
            driver.execute_script(java_script)
            element_clicked = True
        except:
            logging.error("Failed to click element!")


def press_button(driver):
    """This will click on the process button when
    it is clickable. If 5 seconds pass then it will skip

    Args:
        driver (WebDriver): Selenium WebDriver
    """
    press_fail = False
    try:
        WebDriverWait(driver, 5).until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR,"#WhatIfProcess button"))
        )
    except:
        press_fail = True
    if press_fail == True:
        open_what_if_worksheet(driver)
        try:
            WebDriverWait(driver, 5).until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR,"#WhatIfProcess button"))
        )
        except:
            logging.error("Could not click button :<")
            return None
    java_script = 'document.querySelectorAll("#WhatIfProcess button")[1].click()'
    driver.execute_script(java_script)

def open_what_if_worksheet(driver):
    """This will look for the what if worksheet
    and it will test to see if it is open. If it
    is not open, then it will be clicked on to be
    opened.

    Args:
        driver (WebDriver): Selenium WebDriver

    Returns:
        None: None
    """
    try:
        java_script = "return document.evaluate(\"//div[@id='WhatIfWorksheetMode']/div[1]/div[1]\", document.querySelector('html')).iterateNext().attributes[4].value"
        test_case = driver.execute_script(java_script)
    except:
        logging.info("Could not find what if worksheet")
        #perhaps we are logged out (it happens)
        try_to_log_in(driver)
        #Try the open function again
        open_what_if_worksheet(driver)
        return None
    if test_case == 'false':
        driver.find_element(By.XPATH,"//div[@id='WhatIfWorksheetMode'").click()
    else:
        logging.info("did not click the WhatIf button")

def try_to_log_in(driver):
    """This should be called if you have reason to expect
    that you are at the 'Signed out' screen. It will
    try to log you back in

    Args:
        driver (WebDriver): Selenium WebDriver

    Returns:
        None: None
    """
    try:
        #Look for log in link
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.XPATH, "//a[@href='.']"))
        )
    except Exception as exception:
        logging.warning("Could not find log in")
        logging.debug(exception)
        return None
    #click on log in link
    driver.find_element(By.XPATH,"//a[@href='.']").click()
    restart_loop(driver)
    

def restart_loop(driver):
    """This is for when you are taken back to the
    start of the webpage. This happens when you
    are logged out by accident. It will restart the
    main loop, then quit the driver then exit the
    process

    Args:
        driver (WebDriver): WebDriver
    """
    main_loop(driver)
    driver.quit()
    os._exit(0)


def main():
    #check command line arguments
    if len(sys.argv) != 3:
        print("There is an invalid number of command line arguments.\nPlease enter your email and then your password as command line arguments.")
        return

    else:
        web_scraper = Scraper.make_scraper(login_code= login_loop, main_loop=main_loop)
        web_scraper()

if __name__ == "__main__": 
    main()