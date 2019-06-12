from selenium import webdriver 
from selenium.webdriver.firefox.options import Options
from lxml import html 


def make_url(city):
    """Make the url from which to retrieve HTML content for scraping."""
    base_url = 'https://theweathernetwork.com/ca/weather/alberta/'
    url = base_url + city
    return url


def start_driver():
    """Start the selenium driver."""
    # Suppress actual physical browser opening, put in background.
    options = Options()
    options.add_argument('--headless') 
    # Initiate browser session with the above options
    driver = webdriver.Firefox(options=options)
    wait_time = 10 # seconds
    driver.implicitly_wait(wait_time) # this lets webdriver wait 10 seconds for the website to load
    return(driver)


def get_dow(day_path):
    """Get the day of the week from the HTML content."""
    dow_path = "//span[@class='day']/text()"
    xpath = day_path + dow_path
    dow = html.xpath(xpath)[0]
    return(dow)
    
    
def get_forecast(day_path):
    """Get the forecast (text) from the HTML content."""
    forecast_path = "//span[@class='wx_description daytime']/text()"
    xpath = day_path + forecast_path
    forecast = html.xpath(xpath)[0]
    return(forecast)
    
    
def get_temperature(day_path):
    """Get the temperature from the HTML content."""
    temperature_path = "//span[@class='wxperiod_temp daytime']/text()"
    xpath = day_path + temperature_path
    temperature = html.xpath(xpath)[0]
    return(temperature)
    
    
def get_pop(day_path):
    """Get the POP (percent of precipitation) from the HTML content."""
    pop_path = "//span[@class='wxObs daytime']/text()"
    xpath = day_path + pop_path
    pop = html.xpath(xpath)[0]
    return(pop)

# Where do you want the forecast for?
city = 'edmonton'
# Make the search URL.
url = make_url(city)
# Start the driver.
driver = start_driver()
# Get the driver to get the page.
driver.get(url)
# Get the HTML from the page.
html_source = driver.page_source
# Push this big string of HTML through lxml.html() to make it a tree object that is easily searchable/navigated for specific elements.
html = html.fromstring(html_source)

# Xpaths for each day element.
sunday = "//div[@class='wxColumn wxColumn-seven dotw_0']"
monday = "//div[@class='wxColumn wxColumn-seven dotw_1']"
tuesday = "//div[@class='wxColumn wxColumn-seven dotw_2']"
wednesday = "//div[@class='wxColumn wxColumn-seven dotw_3']"
thursday = "//div[@class='wxColumn wxColumn-seven dotw_4']"
friday = "//div[@class='wxColumn wxColumn-seven dotw_5']"
saturday = "//div[@class='wxColumn wxColumn-seven dotw_6']"
days = [sunday, monday, tuesday, wednesday, thursday, friday, saturday]

# Scrape data and print.
for day in days:
    dow = get_dow(day)
    forecast = get_forecast(day)
    temperature = get_temperature(day)
    pop = get_pop(day)
    
    print(f"Weather forecast for {dow}: {forecast}, {temperature} degrees C, POP% = {pop}")
    
# Close the driver 
driver.close()