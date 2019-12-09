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
    def __init__(self, price, departure_time, arrival_time, departure_date, return_date, day_shift, duration, airlines, stopover):
        self.price = price
        self.departure_time = departure_time
        self.arriaval_time = arrival_time
        self.departure_date = departure_date
        self.return_date = return_date
        self.day_shift = day_shift
        self.duration = duration
        self.airlines = airlines
        self.stopover = stopover

    def __str__(self):
        return '###################################################\n' \
             'price: ' + self.price + '\n' \
             'departure_time: ' + self.departure_time + '\n' \
             'arrival_time: ' + self.arriaval_time + '\n' \
             'departure_date: ' + self.departure_date + '\n' \
             'return_date: ' + self.return_date + '\n' \
             'day_shift: ' + self.day_shift + '\n' \
             'duration: ' + self.duration + '\n' \
             'airlines: ' + self.airlines + '\n' \
             'stopover: ' + self.stopover + '\n' \
             '###################################################\n'


class FlightSearch(object):
    def __init__(self, browser, site_config, search_config):
        self.browser = browser
        self.site_config = site_config
        self.search_config = search_config
        self.search_results = []

    def run(self):
        browser.get(site_config['url'])
        self.wait(1)
        self.enter_tickettype_form(site_config['xpath']['tickettype'][search_config['tickettype']])
        self.wait(2)
        self.enter_location_form(site_config['xpath']['departure'], search_config['departure'])
        self.wait(1)
        self.enter_location_form(site_config['xpath']['destination'], search_config['destination'])
        self.wait(1)
        self.enter_date_form(site_config['xpath']['departure_date'], search_config['departure_date'])
        self.wait(2)
        self.enter_date_form(site_config['xpath']['return_date'], search_config['return_date'])
        self.wait(1)
        self.enter_persons_form(site_config['xpath']['persons'], search_config['persons'])
        self.wait(0.8)
        self.perform_search(site_config['xpath']['search_button'])
        time.sleep(20)
        html_source = browser.page_source
        self.search_results = self.gather_flight_information(html_source, site_config['xpath']['flight_results'])
        time.sleep(3)

    def wait(self, maxTime):
        time.sleep(maxTime * random.random())

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
            # form.clear()
            for tmp in range(12):
                form.send_keys(Keys.BACKSPACE)
            self.wait(0.2)
            form.send_keys(date)
            self.wait(1.2)

        except Exception as e:
            raise RuntimeError(e)

    def enter_persons_form(self, form_xpath, persons):

        def set_number_of_persons(target_value, form_xpath_persontype, form_xpath_controls):
            person_count_elem = browser.find_element_by_xpath(
                form_xpath_persontype + form_xpath_controls['persons_count'])
            person_count = int(person_count_elem.text)

            while person_count != target_value:
                if person_count < target_value:
                    incr_form = browser.find_element_by_xpath(
                        form_xpath_persontype + form_xpath_controls['incr_persons'])
                    self.wait(1)
                    incr_form.click()
                    person_count += 1
                else:
                    incr_form = browser.find_element_by_xpath(
                        form_xpath_persontype + form_xpath_controls['decr_persons'])
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

    def gather_flight_information(self, html_source, flight_result_xpath) -> list:
        try:
            result = []
            doc = html.fromstring(html_source)
            flights = doc.xpath(flight_result_xpath['flight_listing'])[0]
            flight_list = flights.xpath(flight_result_xpath['flight_listing_item'])

            for flight in flight_list:

                departure_time_element = flight.xpath(flight_result_xpath['departure_time'])
                if len(departure_time_element) == 1:
                    departure_time = departure_time_element[0].text.strip()
                else:
                    departure_time = 'n.a.'

                arrival_time_element = flight.xpath(flight_result_xpath['arrival_time'])
                if len(arrival_time_element) == 1:
                    arrival_time = arrival_time_element[0].text.strip()
                else:
                    arrival_time = 'n.a.'

                day_shift_element = flight.xpath(flight_result_xpath['day_shift'])
                if len(day_shift_element) == 1:
                    day_shift = day_shift_element[0].text.strip()
                else:
                    day_shift = '0'

                airline_element = flight.xpath(flight_result_xpath['airline'])
                if len(airline_element) == 1:
                    airline = airline_element[0].text.strip()
                else:
                    airline = 'n.a.'

                duration_element = flight.xpath(flight_result_xpath['duration'])
                if len(duration_element) == 1:
                    duration = duration_element[0].text.strip()
                else:
                    duration = 'n.a.'

                stopover_element = flight.xpath(flight_result_xpath['stopover'])
                if len(stopover_element) == 1:
                    stopover = stopover_element[0].text.strip()
                else:
                    stopover = 'n.a.'

                price_element = flight.xpath(flight_result_xpath['price'])
                if len(price_element) == 1:
                    price = price_element[0].text.strip()
                else:
                    price = '999999'

                departure_date = self.search_config['departure_date']
                return_date = self.search_config['return_date']
                flight_obj = Flight(price, departure_time, arrival_time, departure_date, return_date, day_shift, duration, airline, stopover)
                result.append(flight_obj)

            self.wait(2.1)

            return result

        except Exception as e:
            print(e)

            raise RuntimeError(e)


if __name__ == '__main__':

    site_config = {
        'url': 'https://www.expedia.com/Flights',
        'xpath': {
            'tickettype': {
                'roundtrip': "//label[@id='flight-type-roundtrip-label-flp']",
                'oneway': "//label[@id='flight-type-one-way-label-flp']",
                'multistop': "//label[@id='flight-type-multi-dest-label-flp']",
            },
            'departure': {
                'form': "//input[@id='flight-origin-flp']",
                'option_select': "//a[@id='aria-option-0']",
            },
            'departure_date': "//input[@id='flight-departing-flp']",

            'destination': {
                'form': "//input[@id='flight-destination-flp']",
                'option_select': "//a[@id='aria-option-0']",
            },
            'return_date': "//input[@id='flight-returning-flp']",

            'persons': {
                'form': "//div[@id='traveler-selector-flp']//button",  # //button[@id='traveler-selector-flp']",
                'adults': "//div[@class='uitk-grid step-input-outside gcw-component gcw-component-step-input gcw-step-input gcw-component-initialized']",
                'children': "//div[@class='children-wrapper']",
                'infants': "//div[@class='infants-wrapper']",
                'controls': {
                    'incr_persons': "//button[@class='uitk-step-input-button uitk-step-input-plus']",
                    'decr_persons': "//button[@class='uitk-step-input-button uitk-step-input-minus']",
                    'persons_count': "//div[@class='uitk-col all-col-shrink uitk-step-input-value-wrapper traveler-selector-traveler-field']//span[@class='uitk-step-input-value']",
                }

            },
            'search_button': "//button[@class='btn-primary btn-action gcw-submit']",
            'flight_results': {
                'flight_listing': "//div[@id='flight-listing-container']",
                'flight_listing_item': ".//div[@data-test-id='listing-main']",
                'departure_time': ".//span[@data-test-id='departure-time']",
                'arrival_time': ".//span[@data-test-id='arrival-time']",
                'day_shift': ".//span[@data-test-id='arrives-next-day']",
                'airline': ".//span[@data-test-id='airline-name']",
                'duration': ".//span[@data-test-id='duration']",
                'stopover': ".//span[@class='number-stops']",
                'price': ".//span[@data-test-id='listing-price-dollars']",
            },
        },
    }

    search_config = {
        'tickettype': 'roundtrip',
        'departure': "MUC",
        'destination': "Amman",
        'departure_date': "04/01/2020",  # MM/DD/YYYY
        'return_date': "04/18/2020",  # MM/DD/YYYY
        'persons': {
            'adults': 2,
            'children': 0,  # if other than 0, more logic needs to be implemented
            'infants': 0  # if other than 0, more logic needs to be implemented
        }
    }

    browser = webdriver.Chrome(executable_path='chromedriver')

    date_dep = '03/20/2020'
    date_max = '04/18/2020'
    dur_min = 10
    dur_max = 16
    dt_dep = datetime.datetime.strptime(date_dep, '%m/%d/%Y')
    dt_max = datetime.datetime.strptime(date_max, '%m/%d/%Y')
    dt_step = datetime.timedelta(days=1)
    dep_dates = []
    ret_dates = []
    while dt_dep < dt_max:
        dep = dt_dep.strftime("%m/%d/%Y")
        for dur in range(dur_min, dur_max+1):
            dt_dur = datetime.timedelta(days=dur)
            dt_ret = dt_dep + dt_dur
            ret = dt_ret.strftime("%m/%d/%Y")
            if dt_ret < dt_max:
                dep_dates.append(dep)
                ret_dates.append(ret)
        dt_dep += dt_step


    for dep, ret in zip(dep_dates, ret_dates):
        print(f"Departure: {dep}, Return: {ret}")

    search_results = []
    for dep, ret in zip(dep_dates, ret_dates):
        try:
            search_config['departure_date'] = dep
            search_config['return_date'] = ret
            fs = FlightSearch(browser, site_config, search_config)
            fs.run()
            if fs.search_results:
                search_results.extend(fs.search_results)
        except:
            print(f"No flgiths found for depature {dep} and return {ret}")

    sorted_results = sorted(search_results,
                            key=lambda flight: int(float(flight.price.replace("$", "").replace(",", ""))))

    if len(sorted_results) > 200:
        for res in sorted_results[0:200]:
            print(res)
    else:
        for res in sorted_results:
            print(res)

    with open('results.txt', 'w') as f:
        if len(sorted_results) > 200:
            for res in sorted_results[0:200]:
                f.write(str(res))
        else:
            for res in sorted_results:
                f.write(str(res))
