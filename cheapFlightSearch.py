import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from lxml import etree, html
import pandas as pd
import time
import datetime
import random

class Flight(object):
	def __init__(self, price, departure_time, arrival_time, day_shift, duration, airlines, stopover):
		self.price = price
		self.departure_time = departure_time
		self.arriaval_time = arrival_time
		self.day_shift = day_shift
		self.duration = duration
		self.airlines = airlines
		self.stopover = stopover
	
	def __str__(self):
		return '###################################################\n' \
				'price: ' + self.price + '\n' \
				'departure_time: '	+ self.departure_time  + '\n' \
				'arrival_time: ' + self.arriaval_time + '\n' \
				'day_shift: ' + self.day_shift + '\n' \
				'duration: ' + self.duration + '\n' \
				'airlines: ' + self.airlines + '\n' \
				'stopover: ' + self.stopover + '\n' \
				'###################################################\n' \
	

class FlightSearch(object):
	def __init__(self, browser, site_config, search_config):
		self.browser = browser
		self.site_config = site_config
		self.search_config = search_config
		self.search_results = []

	def run(self):
		browser.get(site_config['url'])
		self.wait(1)
		self.enter_tickettype_form(site_config['tickettype_xpath'][search_config['tickettype']])
		self.wait(2)
		self.enter_location_form(site_config['departure_xpath'], search_config['departure'])
		self.wait(1)
		self.enter_location_form(site_config['destination_xpath'], search_config['destination'])
		self.wait(1)
		self.enter_date_form(site_config['departure_date_xpath'], search_config['departure_date'])
		self.wait(2)
		self.enter_date_form(site_config['return_date_xpath'], search_config['return_date'])
		self.wait(1)
		self.enter_persons_form(site_config['persons_xpath'], search_config['persons'])
		self.wait(0.8)
		self.perform_search(site_config['search_button_xpath'])
		time.sleep(20)
		html_source = browser.page_source
		self.search_results = self.gather_flight_information(html_source, site_config['flight_result_xpath'])
		time.sleep(3)

	def wait(self, maxTime):
		time.sleep(maxTime*random.random())

	def enter_tickettype_form(self, form_xpath):
		try:
			tickettype_switch = browser.find_element_by_xpath(form_xpath)
			tickettype_switch.click()
		except Exception as e:
			raise RuntimeError(e)

	def enter_location_form(self, form_xpath, location):
		try:
			form = browser.find_element_by_xpath(form_xpath['form'])
			form.clear()
			time.sleep(1.2)
			form.send_keys(' ' + location)
			time.sleep(1.5)
			first_item = browser.find_element_by_xpath(form_xpath['option_select'])
			self.wait(0.5)
			first_item.click()
			self.wait(1.2)

		except Exception as e:
			raise RuntimeError(e)

	def enter_date_form(self, form_xpath, date):
		try:
			form = browser.find_element_by_xpath(form_xpath)
			#form.clear()
			for tmp in range(12):
				form.send_keys(Keys.BACKSPACE)
			self.wait(0.2)
			form.send_keys(date)
			self.wait(1.2)

		except Exception as e:
			raise RuntimeError(e)

	def enter_persons_form(self, form_xpath, persons):

		def set_number_of_persons(target_value, form_xpath_persontype, form_xpath_controls):
			person_count_elem = browser.find_element_by_xpath(form_xpath_persontype + form_xpath_controls['persons_count'])
			person_count = int(person_count_elem.text)

			while person_count != target_value:
				if person_count < target_value:
					incr_form = browser.find_element_by_xpath(form_xpath_persontype + form_xpath_controls['incr_persons'])
					self.wait(1)
					incr_form.click()
					person_count += 1
				else:
					incr_form = browser.find_element_by_xpath(form_xpath_persontype + form_xpath_controls['decr_persons'])
					self.wait(0.4)
					incr_form.click()
					person_count -= 1

		try:
			form = browser.find_element_by_xpath(form_xpath['form'])
			form.click()
			self.wait(0.2)
			set_number_of_persons(persons['adults'], form_xpath['adults'], form_xpath['controls'])
			self.wait(1.2)
			set_number_of_persons(persons['children'], form_xpath['children'], form_xpath['controls'])
			self.wait(0.8)
			set_number_of_persons(persons['infants'], form_xpath['infants'], form_xpath['controls'])
	
			self.wait(1.2)

		except Exception as e:
			print(e)
			raise RuntimeError(e)

	def perform_search(self, search_button_xpath):
		try:
			form = browser.find_element_by_xpath(search_button_xpath)
			form.click()
			self.wait(2.1)

		except Exception as e:
			print(e)
			raise RuntimeError(e)

	def gather_flight_information(self, html_source, flight_result_xpath)->list:
		try:
			result = []
			doc = 	html.fromstring(html_source)
			flights = doc.xpath(flight_result_xpath['flight_listing_xpath'])[0]
			flight_list = flights.xpath(flight_result_xpath['flight_listing_iter_xpath'])
			
			for flight in flight_list:

				departure_time_element = flight.xpath(flight_result_xpath['departure_time_xpath'])
				if len(departure_time_element) == 1:
					departure_time = departure_time_element[0].text.strip()
				else:
					departure_time = 'n.a.'

				arrival_time_element = flight.xpath(flight_result_xpath['arrival_time_xpath'])
				if len(arrival_time_element) == 1:
					arriaval_time = arrival_time_element[0].text.strip()
				else:
					arrival_time = 'n.a.'

				day_shift_element = flight.xpath(flight_result_xpath['day_shift_xpath'])
				if len(day_shift_element) == 1:
					day_shift = day_shift_element[0].text.strip()
				else:
					day_shift = '0'

				airline_element = flight.xpath(flight_result_xpath['airline_xpath'])
				if len(airline_element) == 1:
					airline = airline_element[0].text.strip()
				else:
					airline = 'n.a.'

				duration_element = flight.xpath(flight_result_xpath['duration_xpath'])
				if len(duration_element) == 1:
					duration = duration_element[0].text.strip()
				else:
					duration = 'n.a.'

				stopover_element = flight.xpath(flight_result_xpath['stopover_xpath'])
				if len(stopover_element) == 1:
					stopover = stopover_element[0].text.strip()
				else:
					stopover = 'n.a.'
					
				price_element = flight.xpath(flight_result_xpath['price_xpath'])
				if len(price_element) == 1:
					price = price_element[0].text.strip()
				else:
					price = 'n.a.'

				flight_obj = Flight(price, departure_time, arriaval_time, day_shift, duration, airline, stopover)
				result.append(flight_obj)
			
			self.wait(2.1)
			
			return result

		except Exception as e:
			print(e)

			raise RuntimeError(e)


if __name__ == '__main__':

	site_config = {
		'url': 'https://www.expedia.com/Flights',
		'tickettype_xpath': {
			'roundtrip' : "//label[@id='flight-type-roundtrip-label-flp']",
			'oneway' : "//label[@id='flight-type-one-way-label-flp']",
			'multistop' : "//label[@id='flight-type-multi-dest-label-flp']"
		},

		'departure_xpath' : {
			'form': "//input[@id='flight-origin-flp']",
			'option_select' : "//a[@id='aria-option-0']"
		},

		'destination_xpath' : {
			'form' : "//input[@id='flight-destination-flp']",
			'option_select' : "//a[@id='aria-option-0']"
		},

		'departure_date_xpath' : "//input[@id='flight-departing-flp']",
		'return_date_xpath' : "//input[@id='flight-returning-flp']",
		'persons_xpath' : {
			'form' : "//div[@id='traveler-selector-flp']//button", #//button[@id='traveler-selector-flp']",
			'adults' : "//div[@class='uitk-grid step-input-outside gcw-component gcw-component-step-input gcw-step-input gcw-component-initialized']",
			'children' : "//div[@class='children-wrapper']",
			'infants' : "//div[@class='infants-wrapper']",
			'controls' : {
				'incr_persons' : "//button[@class='uitk-step-input-button uitk-step-input-plus']",
				'decr_persons' : "//button[@class='uitk-step-input-button uitk-step-input-minus']",
				'persons_count' : "//div[@class='uitk-col all-col-shrink uitk-step-input-value-wrapper traveler-selector-traveler-field']//span[@class='uitk-step-input-value']"
			}
		},

		'search_button_xpath' : "//button[@class='btn-primary btn-action gcw-submit']",
		
		'flight_result_xpath' : {
			'flight_listing_xpath' : "//div[@id='flight-listing-container']",
			'flight_listing_iter_xpath' : ".//div[@data-test-id='listing-main']",	
			'departure_time_xpath' : ".//span[@data-test-id='departure-time']",
			'arrival_time_xpath' : ".//span[@data-test-id='arrival-time']",
			'day_shift_xpath' : ".//span[@data-test-id='arrives-next-day']",
			'airline_xpath' : ".//span[@data-test-id='airline-name']",
			'duration_xpath' : ".//span[@data-test-id='duration']",
			'stopover_xpath' : ".//span[@class='number-stops']",
			'price_xpath' : ".//span[@data-test-id='listing-price-dollars']"
		}
	}

	search_config = {
		'tickettype': 'roundtrip',
		'departure': "MUC",
		'destination': "GDA",
		'departure_date': "08/15/2019", # MM/DD/YYYY
		'return_date': "08/24/2019", # MM/DD/YYYY
		'persons' : { 
			'adults' : 2, 
			'children': 0,	# if other than 0, more logic needs to be implemented	
			'infants' : 0	# if other than 0, more logic needs to be implemented
		}
	}

	browser = webdriver.Chrome(executable_path='chromedriver')

	dep_dates = ["08/15/2019", "08/16/2019", "08/17/2019"]
	for date in dep_dates:
		search_config['departure_date'] = date
		fs = FlightSearch(browser, site_config, search_config)
		fs.run()
		search_results = fs.search_results
		for res in search_results:
			print(res)
	


