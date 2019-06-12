
# **15 Minute Webscraping in Python**

**Author:** Reuben S. Gazer, AltaML  
**Date Started:** June 6, 2019

There have been many occasions where I need to "scrape" data from a website or set of website pages.  
In this notebook, we will look at a few different ways to to web-scraping beginning with a simple retrieval and parsing of an HTML document.

The entire process of scraping data from a web-page boils down to these steps:

- **Step #1**: Identify the website URL from which you'd like to scrape data
- **Step #2**: Ask the website to give you the raw HTML document
- **Step #3**: Figure out which HTML-elements in the document contain the data you'd like to scrape
- **Step #4**: Extract the data from these HTML-elements and store them in some convenient way

### **Python "requests" Package: Basic HTML Retrieval (...but with problems!)**

The simplest way to retrieve the HTML content from a web-page is to use python's built-in _requests_ package.  
For example, let's pull the HTML content from AltaML website homepage with _requests_:


```python
import requests
url = 'https://www.altaml.com/'
response = requests.get(url)
```

    /usr/lib/python3/dist-packages/requests/__init__.py:80: RequestsDependencyWarning: urllib3 (1.25.2) or chardet (3.0.4) doesn't match a supported version!
      RequestsDependencyWarning)


To look at the HTML content, we can try to render it as a a plain-text string, bytes, or json dictionary.  
A json dictionary would be very convenient, but this is not guaranteed to work for all webpages (here it will yield an error).


```python
content = response.json()
```


    ---------------------------------------------------------------------------

    JSONDecodeError                           Traceback (most recent call last)

    <ipython-input-2-a2b3c62eb06b> in <module>
    ----> 1 content = response.json()
    

    /usr/lib/python3/dist-packages/requests/models.py in json(self, **kwargs)
        890                     # used.
        891                     pass
    --> 892         return complexjson.loads(self.text, **kwargs)
        893 
        894     @property


    /usr/lib/python3/dist-packages/simplejson/__init__.py in loads(s, encoding, cls, object_hook, parse_float, parse_int, parse_constant, object_pairs_hook, use_decimal, **kw)
        516             parse_constant is None and object_pairs_hook is None
        517             and not use_decimal and not kw):
    --> 518         return _default_decoder.decode(s)
        519     if cls is None:
        520         cls = JSONDecoder


    /usr/lib/python3/dist-packages/simplejson/decoder.py in decode(self, s, _w, _PY3)
        368         if _PY3 and isinstance(s, binary_type):
        369             s = s.decode(self.encoding)
    --> 370         obj, end = self.raw_decode(s)
        371         end = _w(s, end).end()
        372         if end != len(s):


    /usr/lib/python3/dist-packages/simplejson/decoder.py in raw_decode(self, s, idx, _w, _PY3)
        398             elif ord0 == 0xef and s[idx:idx + 3] == '\xef\xbb\xbf':
        399                 idx += 3
    --> 400         return self.scan_once(s, idx=_w(s, idx).end())
    

    JSONDecodeError: Expecting value: line 1 column 1 (char 0)


Let's look directly at the HTML text itself with the _.text_ attribute:


```python
content = response.text
```


```python
content[:1000] # only the first thousand characters as it is a VERY long string
```




    '<!DOCTYPE html>\n<html>\n<head>\n    <meta http-equiv="Content-Type" content="text/html; charset=UTF-8">\n    <meta name="viewport" content="initial-scale=1.0, user-scalable=no" />\n    <meta name="viewport" content="user-scalable=no, width=device-width, height=device-height, initial-scale=1, maximum-scale=1, minimum-scale=1, minimal-ui" />\n    <meta name="theme-color" content="#20345f" />\n    <meta name="msapplication-navbutton-color" content="#20345f" />\n    <meta name="apple-mobile-web-app-status-bar-style" content="#20345f" />\n    <meta name="description" content="Our focus always starts with the business use-case. We serve as a bridge between cutting-edge academic research and commercialization in industry.">\n    <meta name="author" content="AltaML Inc.">\n    <meta name="Geography" content="#1200, 10130 103 street Edmonton, AB T5J 3N9 Canada">\n    <meta name="Language" content="English">\n    <meta name="Copyright" content="AltaML Inc.">\n    <meta name="city" content="Edmonton">\n    <me'



This is hard to parse with our eyes, but we could feed this into a function that re-creates the HTML-tree from the string content.  
We can "travel" through the tree and access elements (this is webscraping).


```python
from lxml import html
html_tree = html.fromstring(content) # the content is a gigantic, complicated string that we looked at above.
```


```python
html_tree # we can call methods off of this to find children elements of this HTML document
```




    <Element html at 0x7f46d04e5e08>



With this HTML tree element, we can use either _xpath_ or _cssselector_ to select elements from the HTML doc.  
These are just different ways of asking the HTML-tree to give you specific elements given certain conditions.  
As an example, if you visit the homepage and right-click and "inspect element" on the main title text "Machine Learning. Applied." we see the HTML element is an _h1_ element with class = "__title".  
Don't worry about the details of _xpath_ or _cssselector_ at the moment, but to extract this we might do:


```python
title = html_tree.cssselect('h1.__title')
print(title)
```

**Even though this is the correct way to "select" this _h1_ element with the class __title, it returns nothing!**  
Using _requests_, then interpreting the response with the _lxml_ package, and then selecting CSS elements works about 40% of the time.  
This is quite easy way to scrape HTML content on _simple_ webpages, however it will spuriously return nothing on more complex pages, even when you're coding it all properly.  
**Why is this, and if this isn't the way to web-scrape, what _is_ the way for us to web-scrape effectively?**

### **The Problem with Python's "requests" Package for Web-Scraping HTML Content**

The problem with this method for retrieving all HTML content from a webpage is that **not all HTML content is immediately loaded upon initiation of the requests.get() command.**  
Often times there is a base layer of HTML that renders the bare necessities of the page, followed some short time later by a **javascript call** to load **additional HTML content**.  
**This additional content loaded by javascript is not received in the requests.get() call!**  
So, even if you right-click-inspect-element the page and are looking at a particular element in the HTML code on the website + browser, there is no guarantee requests.get() actually received that element.  
In our example above, the title is loaded by javascript and so we could not "find" it in the received HTML document (it's literally not there).  
If we could load the webpage, _wait a few seconds_ and _then_ retrieve the HTML document, we would receive _all_ of the loaded HTML content, even those added by javascript.

### **Selenium: A Package to do both "bot-like" Web Navigation and Web Scraping**

Selenium is the work-around that allows you to load both the base HTML layer as well as most things loaded some time afterwards by javascript.  
Not only this, but Selenium allows you do interact with a website programmatically in the exact same way you might by using a browser.  

For example, using Selenium you can:
- insert text into search boxes and search on a webpage
- click buttons or other interactive media on the webpage
- retrieve HTML content just like requests.get()
- retrieve _more_ HTML content than requests.get() by making selenium "wait" for the rest of the content to load through javascript

This allows Selenium to be a bit more powerful than just the _requests_ package, in that you can navigate around multiple web-pages in a point-and-click fashion programmatically.  

Instructions on installation of Selenium can be found here: https://pypi.org/project/selenium/

In the following example (see _webscraping-example-walkthrough.md_), we will scrape the 7-day weather forecast for a few different cities in Alberta using Selenium.  
I originally tried this using just _requests_ but the table containing our forecasts is loaded afterwards by javascript and thus we need selenium!

### **Example: Retrieving this week's forecast from The Weather Network for 5 Alberta cities**

If you go to this website:  

https://www.theweathernetwork.com/ca/weather/alberta/edmonton  

you will see a box somewhere on the page with the 7-day forecast for Edmonton.  

Say we had a list of cities in Canada, and wanted to retrieve the 7-day forecast for each city in one go. How would we do this?  

The entire process boils down to these steps:

- **Step #1**: Identify the website link that pulls up the 7-day forecast
- **Step #2**: Ask the website to give you the raw HTML document
- **Step #3**: Figure out which elements in this HTML page represent the 7-day forecast
- **Step #4**: Extract these values and store them in a DataFrame, a dictionary, etc.  

The weather link above was simply an example for Edmonton because we are centered here, which I found by googling "Edmonton weather".
Notice the URL itself explicitly states the city we are searching!  
We can take advantage of this and simply change the URL before pulling the HTML content to represent some specific city.  
We _could_ use selenium to actually search the word "Edmonton" in a search box on the homepage of the Weather Network, but we don't have to do this here given the simplicity of the URLs created when searching different cities.

### Step #1: Identify the website URLs that pull up the 7-day forecasts
Since the format of the weather website is identical for each city, we really only need to write a function that retrieves the forecast for a given city.


```python
def make_url(city):
    """Make the url from which to retrieve HTML content for scraping."""
    base_url = 'https://theweathernetwork.com/ca/weather/alberta/'
    url = base_url + city
    return url
```

### Step #2: Ask the website for the HTML content from which to extract the weather forecasts


```python
# This is what navigates around the web browser
from selenium import webdriver 

# I use Firefox, but there is an equivalent for Google Chrome - this import isn't actually necessary, 
# but is used to do everything in the background instead of opening an actual browser every time on your computer.
from selenium.webdriver.firefox.options import Options

# This is just to parse the actual html tree in the final steps.
from lxml import html 
```

The thing that actually navigates around in your web browser is called the DRIVER.   
Instantiating the driver is actually one line of code: _driver = webdriver.Firefox()_.    
However, we will add a few conditions to it:

- make sure to wait 10 seconds or so for everything to load before scraping the HTML content
- suppress the opening of a physical browser on my computer and do it in the background instead

I find it visually simple to stick this all in a nice little function:


```python
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
```

Now, let's start the driver, and ask it to retrieve the HTML content from the Edmonton Weather Network page shown a few cells above.  
Just like _requests.get()_, we will use the equivalent _driver.get()_.


```python
# Make the search URL.
url = make_url('edmonton')
# Start the driver.
driver = start_driver()
# Get the driver to get the page.
driver.get(url)
# Get the HTML from the page.
html_source = driver.page_source
# Push this big string of HTML through lxml.html() to make it a tree object that is easily searchable/navigated for specific elements.
html = html.fromstring(html_source)
```

Let's check out this html object:


```python
html
```




    <Element html at 0x7fcf6c06b368>



Perfect! Now we have an HTML-tree, just like a real HTML document, from which we can pull text from specific elements.  


### Step #3: Figure out which elements in the HTML tree represent the 7-day forecast.  
First, let's identify the specific data items we would like from the forecast, and then we will poke around in the HTML from the page to find it.  

<img src='img/webscraping-weather-1.png' > 

For each day, let's extract:

- the day of the week
- the text-forecast (eg. Rain, Risk of a thunderstorm, mainly sunny, etc.)
- the temperature
- the POP (percent-of-precipitation)

We could extract all of this information just as easily, but for brevity of this example we will keep it to three elements.  

Now that we've decided the data to scrape, where exactly in the HTML tree are these values? To know this, we have to physically visit the webpage (at least this one time) and snoop around in the HTML.  

Head over to https://www.theweathernetwork.com/ca/weather/alberta/edmonton, right-click on the page (specifically, on something you'd like to identify in the HTML tree) and click "Inspect" or "Inspect Element".  

I recommend right-clicking and inspecting where the first column says "Fri" (or whatever day of the week it is when you are reading this!)  
This is what I see (in Firefox - the inspect tools should look similar in Chrome):

<img src='img/webscraping-weather-2.png' >

By scrolling around the HTML code, the page will highlight page objects and tell you what the piece of HTML actually represents.  
It appears that each column of the table (each day's information) is stuck inside a _div_ element called _<div class="wxColumn wxColumn-seven dotw_5">.  
    
Actually, by closing this element, I notice that actually each column is represented by a similar div element, and the day is represented as an integer from 0 - 6 at the end of the "class" of the div.
    
<img src='img/webscraping-weather-3.png'>

We have located in the HTML the elements that contain our weather information.   
The entire table is div with a class "divTableBody" while each column is a child div of this with a unique class name.  
We could just extract these div elements from our HTML tree, but the div elements themselves are sort of meaningless - we want some information INSIDE each of these div elements.  
So, we should expand them and look around for the day, the temperature and the POP.

<img src='img/webscraping-weather-4.png'>

The day of the week is inside a SPAN element with the class="day".  

The "directions" in the HTML tree to this element should look something like this:

- For Friday, go to the DIV with the class="wxColumn wxColumn-seven dotw_5" because 5 is the number representing Friday (where Monday is 1)
- Inside of this div, go into the DIV with class="wxRow"
- Inside of this div, go into the SPAN with class="day"
- Grab the text inside this last SPAN element

This is admittedly a bit tedious, and there are quicker ways to extract these elements.

We can construct this "path" in the HTML tree by using **xpath**, a method of the html document (like XML-path).  
There is a "language" that describes a path to an element in the tree which **xpath** understands.  
Equivalently, we could use **css selectors**, a method of the html document just like **xpath**.   
This is also a "language" that describes a path to an element in the tree.  
Use whichever you prefer - here I will use **xpath**.
You don't need to know everything, but we'll go through the basics experientially.


```python
# The double slash jumps to ANY span element in the document - a single / means you are working down the tree in an absolute path from the very top.
# The condition in the square brackets is that the span element must have the class tag called "day".
# Remember to use double quote on the outside, and singles on the inside, or vice-versa.
html.xpath("//span[@class='day']")
```




    [<Element span at 0x7fcf6c06b818>,
     <Element span at 0x7fcf6c06b778>,
     <Element span at 0x7fcf6c06b4a8>,
     <Element span at 0x7fcf6c06b4f8>,
     <Element span at 0x7fcf6c06b7c8>,
     <Element span at 0x7fcf6c06b868>,
     <Element span at 0x7fcf6c06b908>]



Perfect! There are 7 _span_ elements with class="day", representing all 7 days of the week. To retrieve the text from these elements, just add /text() after inside the xpath:


```python
html.xpath("//span[@class='day']/text()")
```




    ['Sat', 'Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri']



These appear unordered from the image (the image starts at Friday), as I started this notebook on a Thursday, and returned to edit on Friday, meaning the next day in the forecast is really Saturday.  
Generally, these should be in the order they appear in the HTML document.

Let's define some functions that will pull out the info we want:

- the day of the week
- the text-forecast (eg. Rain, Risk of a thunderstorm, mainly sunny, etc.)
- the temperature
- the POP (percent-of-precipitation)

The input to each of these functions is the "day element" that defines each column, since inside each of these is the identical info of the weather forecast.
These elements here:

<img src='img/webscraping-weather-3.png'>

Define the day xpaths of the day elements.


```python
sunday = "//div[@class='wxColumn wxColumn-seven dotw_0']"
monday = "//div[@class='wxColumn wxColumn-seven dotw_1']"
tuesday = "//div[@class='wxColumn wxColumn-seven dotw_2']"
wednesday = "//div[@class='wxColumn wxColumn-seven dotw_3']"
thursday = "//div[@class='wxColumn wxColumn-seven dotw_4']"
friday = "//div[@class='wxColumn wxColumn-seven dotw_5']"
saturday = "//div[@class='wxColumn wxColumn-seven dotw_6']"

days = [sunday, monday, tuesday, wednesday, thursday, friday, saturday]
```

Each of these elements has it's own xpath, which can access all of their children elements.   
Make functions to extract info from each of these day elements, and search around in the Inspect-Element mode to find where each of the attributes we want are:


```python
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
```


```python
for day in days:
    dow = get_dow(day)
    forecast = get_forecast(day)
    temperature = get_temperature(day)
    pop = get_pop(day)
    
    print(f"Weather forecast for {dow}: {forecast}, {temperature} degrees C, POP% = {pop}")
```

    Weather forecast for Sun: Mainly sunny, 16 degrees C, POP% = 15
    Weather forecast for Mon: Chance of a shower, 18 degrees C, POP% = 18
    Weather forecast for Tue: Mainly sunny, 20 degrees C, POP% = 20
    Weather forecast for Wed: Mainly sunny, 23 degrees C, POP% = 24
    Weather forecast for Thu: A mix of sun and clouds, 22 degrees C, POP% = 23
    Weather forecast for Fri: A mix of sun and clouds, 21 degrees C, POP% = 22
    Weather forecast for Sat: A mix of sun and clouds, 13 degrees C, POP% = 11


### Ta-da! We've scraped weather data from The Weather Network for Edmonton.

**Your patience is admired. If you'd like to see only the relevant bits of code and run this easily from a single file, see the file in the local folder _"alberta-weather-webscraping-code.py"_.**
