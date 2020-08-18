# Using the Selenium webdriver as my main webscraper here. Will be scraping data from Expedia Inc.
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.select import Select
import requests
import datetime

from tabulate import tabulate


#Will be using pandas to structure and rightly format my data.
import pandas as pd

#Will be using the time module in Python to halt the script from making multiple invalid 
#requests from the website.

import time
import datetime

#Will be requiring the smtplib module to be able to send us mails with the information.

import smtplib

#Using a webdriver to access Firefox.


driver = webdriver.Firefox()
#driver2 = webdriver.Firefox()
url = "https://www.expedia.ca/?pwaLob=wizard-flight-pwa"
#driver.get(url)

#Storing if it is a roundtrip, a one way trip or a multi city trip.


multi_ticket = "[aria-controls=wizard-flight-tab-multicity]"
one_way_ticket = "[aria-controls=wizard-flight-tab-oneway]"
round_ticket = "[aria-controls=wizard-flight-tab-roundtrip]"


def ticket_chooser(ticket_type):

    try:
        round_one = driver.find_elements_by_css_selector(ticket_type)
        #round_one will be a list: So we need to target it's inner child to and use the .click function to select the required type of the ticket.
        round_one[0].click()
    except Exception as e:
        print(e)
        exit(1)


#Following will be a function to choose the departure country.
def departure_from(dep_country):

    try:

        flying_from = driver.find_elements_by_xpath("//button[@class='uitk-faux-input']")
        #We will be targetting the first element in the list returned above as the location of departure is the first button on Expedia.
        flying_from[0].send_keys(' ' + dep_country)
        #Using this to let the dropdown menu to settle.
        time.sleep(0.5)
        options = driver.find_element_by_xpath("//ul[@class='uitk-typeahead-results no-bullet']")
        first_option = options.find_element_by_tag_name("button")
        #Clicking the first option.
        first_option.click()
        time.sleep(1)
    

    except Exception as e:
        print(e)
        exit(1)

#departure_from('Toronto')

def arrive_to(arrived_to):
    try:
        flying_to = driver.find_elements_by_xpath("//button[@class='uitk-faux-input']")
        #We will be targetting the second element in the list returned above as the location of arrival is the second button on Expedia.
        flying_to[1].send_keys(' ' + arrived_to)
        #Using this to let the dropdown menu to settle.
        time.sleep(0.5)
        mylist = driver.find_element_by_xpath("//li[@data-stid='location-field-leg1-destination-result-item']")
        first_option = mylist.find_element_by_tag_name("button")
        first_option.click()


    except Exception as e:
        print(e)
        exit(1)


#arrive_to('Dubai')

def departure_date(month, date, year):
    try:
        #First finding the departure button and clicking it to open the date options.
        my_departure = driver.find_element_by_xpath("//button[@class='uitk-faux-input uitk-form-field-trigger']")
        my_departure.click()
        time.sleep(1.5)

        dates = driver.find_element_by_xpath("//div[@class='uitk-new-date-picker-month']")
        
        date_parameter = month + ' ' + date + ', ' + year
        dates_final = dates.find_element_by_xpath("//button[@aria-label='%s']" %date_parameter)
        dates_final.click()

        done = driver.find_element_by_xpath("//button[@class='uitk-button uitk-button-small uitk-button-has-text uitk-button-primary uitk-flex-item uitk-flex-shrink-0 dialog-done']")
        done.click()

    except Exception as e:
        print(e)
        exit(1)


#departure_date('Aug','21','2020')



def arrival_date(month,date,year):
    try:
        my_departure = driver.find_elements_by_xpath("//button[@class='uitk-faux-input uitk-form-field-trigger']")
        my_departure[1].click()
        time.sleep(0.5)

        dates = driver.find_elements_by_xpath("//div[@class='uitk-new-date-picker-month']")

        date_parameter = month + ' ' + date + ', ' + year
        dates_final = dates[1].find_element_by_xpath("//button[@aria-label='%s']" %date_parameter)
        dates_final.click()
        #To close the window for choosing dates.
        done = driver.find_element_by_xpath("//button[@class='uitk-button uitk-button-small uitk-button-has-text uitk-button-primary uitk-flex-item uitk-flex-shrink-0 dialog-done']")
        done.click()
    
    except Exception as e:
        print(e)
        exit(1)



#arrival_date('Sep','25','2020')


def search_now():
    #using the search button to submit our input and get results.
    search_btn = driver.find_element_by_xpath("//button[@class='uitk-button uitk-button-large uitk-button-fullWidth uitk-button-has-text uitk-button-primary']")
    search_btn.click()
    #Have to use time.sleep for a longer time to allow the server to fetch the results.
    time.sleep(10)


#We should be having the result page open after the following command.
#search_now()

my_data_frame = pd.DataFrame(columns=['Departing at', 'Arriving at', 'Airlines', 'Price (CAD)', 'Duration', 'Stops', 'Link'])

def collecting_attributes():

    elems = driver.find_elements_by_xpath("//span[@data-test-id='departure-time']")
    dep_time_list = []
    for elem in elems:
        dep_time_list.append(elem.text)

    arrival_tags = driver.find_elements_by_xpath("//span[@data-test-id='arrival-time']")
    arrival_list = []
    for elem in arrival_tags:
        arrival_list.append(elem.text)


    airline_tags = driver.find_elements_by_xpath("//div[@class='secondary-content overflow-ellipsis inline-children']//span[@data-test-id='airline-name']")
    airlines = []
    for elem in airline_tags:
        airlines.append(elem.text)

    price_tags = driver.find_elements_by_xpath("//span[@data-test-id='listing-price-dollars']")
    prices = []
    for elem in price_tags:
        price_num = int(elem.text.split("$")[1].replace(',',''))
        prices.append(price_num)

    duration_tags = driver.find_elements_by_xpath("//span[@data-test-id='duration']")
    durations = []
    for elem in duration_tags:
        durations.append(elem.text)

    stop_tags = driver.find_elements_by_xpath("//span[@class='number-stops']")
    stops = []
    for elem in stop_tags:
    #Getting the number of stops as an integer rather than a string.
        attb = elem.get_attribute('data-test-num-stops')
        stops.append(attb)


#Getting information for the layover.
    layover_tags = driver.find_elements_by_xpath("//span[@data-test-id='layover-airport-stops']")
    layovers = []

    for elem in layover_tags:
    #If no layovers, the text is all capitalized. Found a common pattern in over 100 search results.
        if elem.text.isupper():
            layovers.append("None")

        else:
            layovers.append(elem.text)
    
#Let's create a neat dataframe to hold our values.

    
    for i in range(len(dep_time_list)):
        try:
            my_data_frame.at[i,'Departing at'] = dep_time_list[i]
        except Exception as e:
            pass

        try:
            my_data_frame.at[i, 'Arriving at'] = arrival_list[i]
        except Exception as e:
            pass


        try:
            my_data_frame.at[i,'Airlines'] = airlines[i]
        except Exception as e:
            pass

        
        try:
            my_data_frame.at[i,'Price (CAD)'] = prices[i]
        except Exception as e:
            pass


        try:
            my_data_frame.at[i,'Duration'] = durations[i]
        except Exception as e:
            pass

        try:
            my_data_frame.at[i, 'Stops'] = stops[i]
        except Exception as e:
            pass


        my_data_frame.at[i,'Link'] = driver.current_url

        #Now that our dataframe is ready, let's convert it into an Excel sheet for easy evaluations.
        #my_data_frame.to_excel(r'C:\Users\shiva\Desktop\Side Projects\Web_scraping\Airfare automation\Expedia_values.xlsx', index = False)


#collecting_attributes()

# The following program ends for data colllected from Expedia.com.


#Next target - Collect data from Kayak.com
#driver.close()

url = 'https://www.ca.kayak.com/flights'
#driver2.get(url)
#time.sleep(5)

#Firstly, let's get the button to decide what kind of a trip it is?

def trip_type(trip):
    allowed_trips = ['oneway', 'roundtrip']
    if trip not in allowed_trips:
        print("Invalid trip option.")
        return 

    trip_button = driver2.find_element_by_xpath("//div[@class=' _iVh _ibU _ibV _iaf _h-Y _imx _idj']")
    trip_button.click()
    time.sleep(2)

    options_list = driver2.find_element_by_xpath("//ul[@class='_iKm _id7 _iOC _iFZ _iA6 _iFW']")

    final_option = options_list.find_element_by_xpath("//li[@data-value='%s']"%trip)
    final_option.click()

#trip = input("Please enter your trip from the following options: ['oneway', 'roundtrip]")
#trip_type(trip)


def class_type(personal_class):
    allowed_classes = ['Premium Economy', 'Business', 'First', 'Economy']
    if personal_class not in allowed_classes:
        print("Invalid Cabin Type.")
        return 

    class_button = driver2.find_elements_by_xpath("//div[@class=' _iVh _ibU _ibV _iaf _h-Y _imx _idj']")[1]
    class_button.click()
    time.sleep(1.2)

    option = class_button.find_element_by_xpath("//li[@data-title='%s']"%personal_class)
    option.click()  


#class_type('Business')


def departing_from(departure):
    print("Patience is virtue.")


"""
departing_from_button = driver2.find_element_by_xpath("//div[@class='_ibU _ioS _ibV _iDB _idE _im8 _j0G _iai _j-p _j-q _j88 _j2g _ikc _j9j _iCV _iqF _iHV _j-v _j8a _ijv _j9d _j-r _j-s _j-t _j-u _jvW _iqs _iqt _j-0 _iqu _j-1 _iqv _jvU _is4 _iwM _iqH _ixK _iQF _j-Z _ibr _j-V _j-W _j-X _j-Y _j-2 _io5 _j-U selectTextOnFocus _iVh']")
departing_from_button.click()
time.sleep(4)

#Using backspace twice to clear the input field, if at all it is filled.
departing_from_button.send_keys(Keys.BACK_SPACE)
departing_from_button.send_keys(Keys.BACK_SPACE)
time.sleep(1.5)


trying = driver2.find_element_by_xpath("//div[@class='_ia1 _h-8 _itL']//input")
trying.send_keys(" " + "Canada")
time.sleep(1.5)

first_option = driver2.find_element_by_xpath("//ul[@class='flight-smarty']//li")
first_option.click()

time.sleep(1)

if trip == 'roundtrip':
    final_destination = driver2.find_elements_by_xpath("//div[@class='col _i0B _iac _iad _iae _iaa _iab _iys _iyv _iaW _iaX _iaY _iyq _iaS _iaU _iAU _iaV _iAV _izh _iaR _h-8 _ize']")[1]
else:
    final_destination = driver2.find_element_by_xpath("//div[@class='_ibU _ioS _ibV _iDB _idE _im8 _j0G _iai _j-p _j-q _j88 _j2g _ikc _j9j _iCV _iqF _iHV _j-v _j8a _ijv _j9d _j-r _j-s _j-t _j-u _j-J _j-K _j-L _icc _is4 _j-F _j-G _j-H _j-I _iwM _j-B _j-C _iqH _j-D _iQI _j-E _iqj _iOC _iFZ _iA6 _j-A _iFW _ioZ selectTextOnFocus _iVh']")
final_destination.click()


typing_final_destination = driver2.find_elements_by_xpath("//div[@class='_ia1 _h-8 _itL']//input")[1]
typing_final_destination.send_keys(" " + "Dubai")
time.sleep(1)
typing_final_destination.send_keys(Keys.ENTER)

time.sleep(2)



#Getting the dates for departure.

departure_date = driver2.find_element_by_xpath("//div[@class='_iaf _iEU _iam _iai']")
departure_date.click()
time.sleep(1.2)
date_button = departure_date.find_element_by_xpath("//div[@class='input _iKG _id7 _ial _ii0 _iQj _iaj _ihh _idE']")
date_button.send_keys("05/09/2020")
date_button.send_keys(Keys.ENTER)

time.sleep(1.2)

#Function for deciding return date.
if trip == 'roundtrip':
    return_dates_button = driver2.find_elements_by_xpath("//div[@class='_iVh']")[1]
    return_dates_button.click()
    time.sleep(1)
    final = return_dates_button.find_element_by_xpath("//div[@class='input _iKG _id7 _ial _ii0 _iQj _iaj _ihh _idE']")
    final.send_keys("17/09/2020")
    time.sleep(2)
    final.send_keys(Keys.ENTER)

#Function for searching.

search_button = driver2.find_element_by_xpath("//button[@class='Common-Widgets-Button-StyleJamButton theme-light SeparateIconAndTextButton Button-Gradient size-l searchButton _id7 _ihr _ihs _h-Y _im4 _ii0 _ihp _ihq _inw _iir _iae _jWT _iFQ _iFR _imQ _iv1']")
search_button.click()


#Kayak has multiple pop-ups and we also need to sign in to utilize it's features.

#Disabling the first pop-up:
time.sleep(3.5)
pop_up_button = driver2.find_element_by_xpath("//div[@class='Common-Widgets-Dialog-Dialog R9-Overlay a11y-focus-outlines extraRadius noShadow fromTop animate visible']//div[@class='viewport']//div//button")
pop_up_button.click()


#Finding departing_times:
departing_time_kayak = []
departing_times_normal = []
departing_times_rounded = []

def departing_times(trip):
    #List containing all the departing-times.

    departing_time_kayak = driver2.find_elements_by_xpath("//div[@class='resultInner']//ol//li//div[@class='section times']//span[@class='depart-time base-time']")
    #Need to check if the trip is rounded or not.
    if trip == 'roundtrip':
        counter = 0
        for elem in departing_time_kayak:
            if counter % 2 == 0:
                departing_times_normal.append(elem.text)
            else:
                departing_times_rounded.append(elem.text)
            counter += 1
    
    else:
        for elem in departing_time_kayak:
            departing_times_normal.append(elem.text)



#departing_times(trip)

arrival_time_kayak = []
return_time_normal = []
return_time_rounded = []

def arrival_times(trip):
    #List containing all the arrival-times.
    arrival_time_kayak = driver2.find_elements_by_xpath("//div[@class='resultInner']//ol//li//div[@class='section times']//span[@class='arrival-time base-time']")

    #Need to store arrival-times of both trips if the trip is rounded.

    #Checking if the trip is rounded.
    if trip == 'roundtrip':
        #We need to store return times in another list: return_time_rounded.
        counter = 0
        for elem in arrival_time_kayak:
            if counter % 2 == 0:
                return_time_normal.append(elem.text)
            else:
                return_time_rounded.append(elem.text)
            
            counter += 1
    
    else:
        for elem in arrival_time_kayak:
            return_time_normal.append(elem.text)



#arrival_times(trip)
time.sleep(1.2)

#Let's find the number of stops for each flight.

number_of_stops_return = []
number_of_stops_normal = []
def number_of_stops(trip):
    
    number_of_stops = driver2.find_elements_by_xpath("//div[@class='resultInner']//ol//li//div[@class='section stops']//div[@class='top']")
    counter = 0
    for elem in number_of_stops:
        #Formatting it in the right way.
        if elem.text == 'direct':
            final = 0
        else:
            final = elem.text.split(" ")[0]


        if trip == 'roundtrip':
            if counter % 2 == 0:
                number_of_stops_normal.append(final)
            else:
                number_of_stops_return.append(final)
            counter +=1
        else:
            number_of_stops.append(final) 


    print(number_of_stops_normal, number_of_stops_return)

#number_of_stops(trip)
#Waiting till the page responds; This URL is kinda slow.
#delay = 45
#myElem = WebDriverWait(driver2, delay).until(EC.presence_of_element_located((By.XPATH, "//div[@class='resultsPaginator']//div[@class='Common-Results-Paginator ButtonPaginator visible']")))

#To find the duration of the flights:
durations_normal = []
durations_rounded = []
def durations(trip):
    durations = driver2.find_elements_by_xpath("//div[@class='resultInner']//ol//li//div[@class='section duration allow-multi-modal-icons']//div[@class='top']")
    if trip == 'roundtrip':
        counter = 0
        for elem in durations:
            if counter % 2 == 0:
                durations_normal.append(elem.text)
            else:
                durations_rounded.append(elem.text)
            counter += 1
    
    else:
        for elem in durations:
            durations_normal.append(elem.text)

    print(durations_normal, durations_rounded)
    

#durations(trip)


#To find the pricings of these flights:
time.sleep(1)
price_normal = []
price_rounded = []
def price_findings(trip):
    pricings_tag = driver2.find_elements_by_xpath("//div[@class='Common-Booking-VerticalMultiBookDropdown Flights-Booking-FlightVerticalMultiBookDropdown align-right']//span[@class='price-text']")
    for elem in pricings_tag:
        print(elem.text)
        price_num = int(elem.text.split(" ")[1])
        price_normal.append(price_num)
        if trip == 'roundtrip':
            price_rounded.append(price_num)
    
    print(price_normal, price_rounded)

#price_findings(trip)



#To make a function to store airline names:
airlines_normal = []
airlines_rounded = []
def airline_names(trip):
    carrier_tags = driver2.find_elements_by_xpath("//div[@class='resultInner']//ol//li//div[@class='section times']")
    counter = 0
    for elem in carrier_tags:
        airline_name = elem.find_elements_by_tag_name('div')[1]
        if trip == 'roundtrip':
            if counter % 2 == 0:
                airlines_normal.append(airline_name.text)
            else:
                airlines_rounded.append(airline_name.text)
        
            counter += 1

        else:
            airlines_normal.append(airline_name.text)


#airline_names(trip)            


def add_to_dataframe():
    #Adding departing times:
    i = 65 #Continuing from the 66th row in our dataframe.

    #NOTE: Adding the very first departure time, even if it is a rounded flight.
        #Adding arrival_times: (The final arrival_time only)
    
    #Firstly, check if the two created list exists.

    if return_time_rounded:
        final_arrivals = return_time_rounded
    else:
        final_arrivals = return_time_normal




    # for j in range(len(departing_times_normal)):
    #     new_row_try = pd.Series(data = {"Departing at": departing_times_normal[j], "Arriving at": final_arrivals[j], "Airlines": airlines_normal[j], "Price (CAD)": price_normal[j], "Duration": durations_normal[j], "Stops": number_of_stops_normal[j]}, name=i)
    #     my_data_frame = my_data_frame.append(new_row_try, ignore_index = False)
    #     i += 1


    # return my_data_frame


    for j in range(len(departing_times_normal)):
        #Adding departing_times firstly.
        try:
            my_data_frame.at[i,'Departing at'] = departing_times_normal[j]
        except Exception as e:
            print(e)
            exit(1)
        



        try:
            my_data_frame.at[i, 'Arriving at'] = final_arrivals[j]
        except Exception as e:
            print(e)
            exit(1)
        

        #Adding the Airline name.
            #Adding only the airline name for the first flight.
        
        try:
            my_data_frame.at[i, 'Airlines'] = airlines_normal[j]
        except Exception as e:
            print(e)
            exit(1)
        

        #Adding the price.
        
        try:
            my_data_frame.at[i, 'Price (CAD)'] = price_normal[j]
        except Exception as e:
            print(e)
            exit(1)
        

        #Adding duration of the flights.
            #Adding only the duration of the first flight right now.
        
        try:
            my_data_frame.at[i, 'Duration'] = durations_normal[j]
        except Exception as e:
            print(e)
            exit(1)


        #Adding number of stops.

        try:
            my_data_frame.at[i,'Stops'] = number_of_stops_normal[j]
        except Exception as e:
            print(e)
            exit(1)

        #Storing the Link for later purposes.
        my_data_frame.at[i,'Link'] = driver2.current_url
        i += 1

    return my_data_frame

my_data_frame = add_to_dataframe()
driver2.close()

#Sorting the data_frame in ascending order of price to get the cheapest flight available.

#final_sorted_df = my_data_frame.sort_values('Price (CAD)')
#print(final_sorted_df)


#Getting data from the third and final website - skiplagged.


"""



url = 'https://skiplagged.com/'
driver.get(url)


def flying_from_notation(departing_from):
    input_button = driver.find_element_by_xpath("//input[@class='src-input ui-autocomplete-input']")
    input_button.click()
    time.sleep(1)

    input_button.send_keys(Keys.BACK_SPACE)
    input_button.send_keys('' + departing_from)
    time.sleep(1)

    input_options = driver.find_element_by_xpath("//ul[@class='ui-autocomplete ui-front ui-menu ui-widget ui-widget-content']//li//a//span")
    return input_options.text
    #input_options.click()


from_location = flying_from_notation('Toronto')


def arriving_at_notation(arrival):
    departing_button = driver.find_element_by_xpath("//input[@class='dst-input ui-autocomplete-input']")
    departing_button.click()
    time.sleep(0.5)

    departing_button.send_keys(Keys.BACK_SPACE)
    departing_button.send_keys('' + arrival)
    time.sleep(1)

    departing_options = driver.find_element_by_xpath("//ul[@class='ui-autocomplete ui-front ui-menu ui-widget ui-widget-content' and @id='ui-id-2']//li//a//span")
    return departing_options.text
    #departing_options.click()


to_location = arriving_at_notation('Dubai')

"""
#Choosing the departure date.
def departure_date(departing_date):
    departure_date_button = driver.find_element_by_xpath("//input[@class='date-input start-date hasDatepicker']")
    departure_date_button.click()

    my_dates = departing_date.split("/")
    day = my_dates[0]
    month = str(int(my_dates[1]) - 1)
    year = my_dates[2]

    date_finding = driver.find_elements_by_xpath("//div[@class='ui-datepicker-group ui-datepicker-group-first']//table[@class='ui-datepicker-calendar']//tbody//td[@data-handler='selectDay' and @data-month='{0}' and @data-year='{1}']//a".format(month,year))

    for elem in date_finding:
        try:
            if elem.text == day:
                try:
                    elem.click()
                except Exception:
                    pass
        except Exception:
            pass


def returning_date(return_date):

    return_button = driver.find_element_by_xpath("//input[@class='date-input end-date hasDatepicker']")
    return_button.click()


    #Rightly formating the date.
    try:
        my_dates = return_date.split("/")
        day = my_dates[0]
        month = str(int(my_dates[1]) - 1)
        year = my_dates[2]
    except Exception:
        return

    date_finding = driver.find_elements_by_xpath("//div[@class='ui-datepicker-group ui-datepicker-group-last']//table[@class='ui-datepicker-calendar']//tbody//td[@data-handler='selectDay' and @data-month='{0}' and @data-year='{1}']//a".format(month,year))

    for elem in date_finding:
        try:
            if elem.text == day:
                try:
                    elem.click()
                except Exception:
                    pass
        except Exception:
            pass
        
departing_date = str(input("Please enter the date of departure in the following format: dd/m/yyyy "))
returning_date_input = str(input("Please enter the date of return; if applicable; in the following format: dd/m/yy "))
departure_date(departing_date)
returning_date(returning_date_input)
"""

#Deciding what kind of a trip it will be.
"""
def trip_type_chooser():

    trip_chooser_button = driver.find_element_by_xpath("//div[@class='skip-select passengers-input-container trip-type-select']//button")
    trip_chooser_button.click()

    time.sleep(1)

    #Choosing from the list.

    trip = input("Please choose from the following options: ['One Way', 'Roundtrip'] ")
    trip = trip.lower()
    if 'oneway' in trip:
        option = trip_chooser_button.find_element_by_xpath("//div[@class='skip-select passengers-input-container trip-type-select']//div[@class='passengers-input__select fare-class-input__select']//div[@data-trip-type='one-way']")
    else:
        option = trip_chooser_button.find_element_by_xpath("//div[@class='skip-select passengers-input-container trip-type-select']//div[@class='passengers-input__select fare-class-input__select']//div[@data-trip-type='round-trip']")

    option.click()

trip_type_chooser()
"""

#Clicking the search button - Finishing the first page:
"""
def search_web():
    search_button = driver.find_element_by_xpath("//div[@class='form-row']//button").click()


#Searching for the flight details.
search_web()


#Getting the flight details.

#The new page takes time to load so let's wait for a max of 10 seconds?
time.sleep(10)


#Getting the departure time.

#departure_time = driver.find_element_by_xpath("//div[@class='span9 trip-path']//div[@class='trip-path-point-time' and @data-toggle='tooltip' and @data-container='body']")
#departure_times = driver.find_elements_by_xpath("//div[@class='span9 trip-path']//div[@class='trip-path-point-time ' and @data-container='body']")


# time.sleep(5)
# for elem in infinite_list:
#     print(elem.text)

mylist = []

last = driver.execute_script("return document.body.scrollHeight")
while True:
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(1) #let the page load
    new = driver.execute_script("return document.body.scrollHeight")
    infinite_list = driver.find_elements_by_xpath("//div[@class='infinite-trip-list']//div[@class='span1 trip-duration']")
    for elem in infinite_list:
        if elem not in mylist:
            mylist.append(elem.text)
    if new == last: #if new height is equal to last height then we have reached the end of the page so end the while loop
        break
    last = new #changing last's value to new

"""

#kayak_df = pd.DataFrame(columns=['Flight_Number','Departing_location', 'Arriving_location','Departing_at', 'Arriving_at', 'Airlines', 'Price (CAD)', 'Duration'])
kayak_df = pd.DataFrame(columns=['Flight_Number','Price','Stops', 'Duration', 'All_Airlines', 'Routes'])
def scrap_flights_details():

    depart_date = input("Enter the departure date in the following format -> yyyy-mm-dd: ")
    return_date = input("Enter the return date in the following format; if applicable -> yyyy-mm-dd: ")
    #return_date = ''
    counts_adults = 1
    counts_children = ''

    import dateutil.parser

    API_URL = 'https://skiplagged.com/api/search.php?from=' + from_location + '&to=' + to_location + '&depart=' + str(depart_date) + '&'\
        'return=' + str(return_date) + '&format=v3&counts%5Badults%5D=' + str(counts_adults) + '&counts%5Bchildren%5D=' + str(counts_children)

    print(API_URL)
    counter = 0
    flights_details = requests.get(API_URL,verify=False).json()


    for flight_number in flights_details['itineraries']['outbound']:
        #Extracting the flight_number for each flight from your starting location to the destination.
        number = flight_number['flight']
        kayak_df.at[counter,'Flight_Number'] = number

        #Getting the price.
    
        if return_date:
            price_cents = flight_number['min_round_trip_price']
        else:
            price_cents = flight_number['one_way_price']

        price = int(price_cents/100)
        price = '{:,.2f}'.format(price)
        kayak_df.at[counter,'Price'] = price


        total_duration_secs = flights_details['flights'][number]['duration']
        total_duration_hours = str(datetime.timedelta(seconds = int(total_duration_secs)))
        kayak_df.at[counter,'Duration'] = total_duration_hours

        #Getting the number of stops.
        stops = flights_details['flights'][number]['count']
        kayak_df.at[counter,'Stops'] = stops


        #Converting seconds to hours using the datetime module.
        routes = []
        airlines = []
        for elem in flights_details['flights'][number]['segments']:


            #To find the full-form of the flights.
            short_form_airline = elem['airline']
            full_airline_name = flights_details['airlines'][short_form_airline]['name']
            airlines.append(full_airline_name)
            
            departure_location_shortform = elem['departure']['airport']
            departure = flights_details['airports'][departure_location_shortform]
            #arrival = flights_details['airports'][arrival_location_shortform]
            routes.append(departure['name'])


        kayak_df.at[counter,'All_Airlines'] = airlines
        kayak_df.at[counter,'Routes'] = routes
        counter += 1




scrap_flights_details()

print(tabulate(kayak_df))
