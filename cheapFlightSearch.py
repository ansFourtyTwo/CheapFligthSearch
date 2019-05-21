import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import pandas as pd
import time
import datetime


def main():
	browser = webdriver.Chrome(executable_path='chromedriver')
	browser.get('https://www.expedia.com/Flights')
	browser.
	time.sleep(4)

	
	#Setting ticket types paths
	return_ticket = "//label[@id='flight-type-roundtrip-label-hp-flight']"
	one_way_ticket = "//label[@id='flight-type-one-way-label-hp-flight']"
	multi_ticket = "//label[@id='flight-type-multi-dest-label-hp-flight']"

def ticket_chooser(ticket):
    try:
        ticket_type = browser.find_element_by_xpath(ticket)
        ticket_type.click()
    except Exception as e:

        pass

if __name__ == "__main__":
	main()


