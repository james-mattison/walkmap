from selenium import webdriver
import os
import time


def template_iter():
    for file in os.listdir("/root/static"):
        if ".html" in file and not "index.html" in file:
            yield file

class ScreenShotter:

    def __init__(self):
        options = webdriver.ChromeOptions()
        options.add_argument("--no-sandbox")
        options.add_argument('--headless')
        options.add_argument("--disable-dev-shm-usage")
        self.driver = webdriver.Chrome(chrome_options = options)

    def take_screenshots(self):
        for obj in template_iter():
            self.driver.get("http://0.0.0.0/map/" + obj)
            print("Sleeping 3 seconds to let page load.")
            time.sleep(3)
            fn = "/root/static/" + obj.split(".")[0] + ".png"
            print("Browser pointed at: " + obj + " Writing screenshot to filename " + fn )
            self.driver.get_screenshot_as_file(fn)
            print("Took screenshot and wrote to " + fn)


shotter = ScreenShotter()
shotter.take_screenshots()
