"""
This program was created by Mark Gauda in June of 2022
The purpose of this program is to provide a boiler-plate for the selenium module
This module will offer a modular log-in, and form filler boiler plate
"""



from selenium import webdriver

def make_scraper(main_loop = None, login_code = None, browser = "firefox", test = False, headless = False):
    
    #Make main loop
    if main_loop != None:
        def run_main_loop(code):
            code()

    else:
        def run_main_loop():
            return None
    
    #Make login
    if login_code != None:
        def run_login_code(code):
            code()
            return None

    else:
        def run_login_code():
            return None

    #Open browser

    if str(browser).lower() == "chrome":
        if headless == False:
            def open_browser():
                driver = webdriver.Chrome()
                return driver
        if headless == True:
            def open_browser():
                from selenium.webdriver.chrome.options import Options
                chrome_options = Options()
                chrome_options.add_argument("--headless")
                driver = webdriver.Chrome(chrome_options=chrome_options)
                return driver

    else:
        def open_browser():
            driver = webdriver.Firefox()
            return driver
    
    #Make test
    if test == True:
        def test_code(driver):
            driver.get("http://www.google.com")
            assert "Google" in driver.title
    else:
        def test_code(diver):
            return None

    
    def final_code():
        #open browser
        driver = open_browser()

        #test code
        test_code(driver)

        #login
        if login_code != None:
            login_code(driver)

        
        #run main loop
        if main_loop != None:
            main_loop(driver)

        #close driver
        driver.quit()

    return final_code
    

        