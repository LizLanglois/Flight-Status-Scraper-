from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
from pywebio.output import put_text, put_image, use_scope, put_file
from datetime import datetime
from pywebio.input import *
import time
import csv

#logo for GUI
put_image(open('logo2.PNG', 'rb').read())

#menu for user input to select date to check
answer = radio("Which date would you like to check?", options=['23APR', '24APR', '25APR'])
date = answer[:2]
month = answer[-3:]
filename = answer+".csv"
csv_file_path = answer+"updated.csv"

num_month = ""

if month == 'JAN':
    num_month = '1'
elif month == 'FEB':
    num_month = '2'
elif month == 'MAR':
    num_month = '3'
elif month == 'APR':
    num_month = '4'
elif month == 'MAY':
    num_month = '5'
elif month == 'JUN':
    num_month = '6'
elif month == 'JUL':
    num_month = '7'
elif month == 'AUG':
    num_month = '8'
elif month == 'SEP':
    num_month = '9'
elif month == 'OCT':
    num_month = '10'
elif month == 'NOV':
    num_month = '11'
else:
    num_month = '12'


class Flights:

    def __init__(self, airline, flightnum, origin, destination, dtime, atime, update='checking'):
        self.airline = airline
        self.flightnum = flightnum
        self.origin = origin
        self.destination = destination
        self.dtime = dtime
        self.atime = atime
        self.update = update
    #set url to check
    def set_url(self):
        return f"https://www.flightstats.com/v2/flight-tracker/{self.airline}/{self.flightnum}?year=2023&month={num_month}&date={date}"
    #check flight status
    def status(self):
        options = Options()
        options.headless = True

        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        driver.get(self.set_url())

        soup = BeautifulSoup(driver.page_source, 'lxml')
        flifo = soup.find(class_="ticket__StatusContainer-sc-1rrbl5o-17")
        driver.quit()
        try:
            return flifo.get_text(separator=" ")
        except AttributeError:
            return 'checking'

    def check(self):
        self.update = self.status()
    #display for updated flight info
    def display(self):
        return f"\t{self.airline} \t {self.flightnum:04} \t {self.origin: >8}  {self.destination: >8}\t\t {self.dtime: >12} \t {self.atime: >12} \t\t  {self.update}"
    #write status to csv file
    def update_csv_file(flts, csv_file_path):
        with open(csv_file_path, mode='w', newline='') as csv_file:
            writer = csv.writer(csv_file)
            for i in flight_instances:
                writer.writerow([i.airline, i.flightnum, i.origin, i.destination, i.dtime, i.atime, i.update])

#read original air report
df = pd.read_csv(filename, header=None)
flts = df.values.tolist()
flight_instances = []
#create objects for each line in air report
for f in flts:
    flight_instances.append(Flights(*f))


df['Status'] = "checking"
print(df)

#date scope for GUI
@use_scope('DATE')
def show_date():
    put_text('Showing flights for ', answer)

#original time scope for GUI
@use_scope('TIME', clear=True)
def show_time():
    put_text('please wait while we gather flight status information')

#subsequent time scope for GUI after status updates
@use_scope('TIME', clear=True)
def show_time2():
    put_text('last updated:', datetime.now().isoformat(timespec='minutes', sep=' '))

#flight display for GUI
@use_scope('FLIGHTS', clear=True)
def show_flights():
    for i in flight_instances:
        x = i.update
        if x[0:7] == 'Arrived':
            pass
        else:
            put_text((Flights.display(i))).style('border-bottom-style: solid; border-width: 1px;padding-right: 30px')

#updated csv link for GUI
@use_scope('link', clear=True)
def show_link():
    content = open(csv_file_path, 'rb').read()
    put_file('updated_air.csv', content)

show_date()
show_time()
show_flights()


count = 0
while True:
    for i in flight_instances:
        x = i.update
        if x[0:7] == 'Arrived':
            pass
        else:
            Flights.check(i)
            print(Flights.display(i))

    Flights.update_csv_file(flts, csv_file_path)

    show_flights()
    show_time2()
    show_link()

    count += 1
    time.sleep(6)

    if count == 25:
        break
