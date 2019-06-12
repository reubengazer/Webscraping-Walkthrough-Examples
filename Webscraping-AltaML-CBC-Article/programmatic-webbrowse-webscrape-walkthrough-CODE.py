from selenium import webdriver
from lxml import html

# Start URL.
url = 'https://www.cbc.ca/news'

# If you want to do this in the BACKGROUND without the browser opening, run this instead of lines 23, 25 and 26. #

#def start_driver():
#    """Start the selenium driver."""
#    # Suppress actual physical browser opening, put in background.
#    options = Options()
#    options.add_argument('--headless') 
#    # Initiate browser session with the above options
#    driver = webdriver.Firefox(options=options)
#    wait_time = 10 # seconds
#    driver.implicitly_wait(wait_time) # this lets webdriver wait 10 seconds for the website to load
#    return(driver)
#
#driver = start_driver()

# Initiate webdriver.
driver = webdriver.Firefox()
# Wait time for website to load elements.
wait_time = 10 # seconds
driver.implicitly_wait(wait_time)
# Go to the page.
driver.get(url)
# Find and click the search button to expand the text-search box.
driver.find_element_by_id('searchButton').click()
# Find the text-search box itself.
search_box = driver.find_element_by_id("gn-search")
# Submit a string to the search box
search_string = "AltaML"
search_box.send_keys(search_string)
# Click the "Search" button to submit it 
driver.find_element_by_class_name("searchButton").click()
# Click on the first article available (the only one for this example)
driver.find_element_by_class_name("card-content").click()
# Extract the HTML source code and make it a searchable tree
page_html = driver.page_source
html = html.fromstring(page_html)

# Scrape the title, subtitle and text from the HTML content.
def scrape_article():
    """Return the title, subtitle and text content of the CBC article."""
    title = html.xpath("//h1[@class='detailHeadline']/text()")[0] 
    subtitle = html.xpath("//h2[@class='deck']/text()")[0]
    paragraphs = html.xpath("//div[@class='story']/span/p/text()")
    paragraphs = "".join(paragraphs)
    paragraphs = paragraphs.replace('\xa0', ' ')
    return title, subtitle, paragraphs

# Print this content.
def print_article():
    """Print the retrieved AltaML article from the CBC website."""
    print(f"Title :\n{title}")
    print("\n")
    print(f"Subtitle :\n{subtitle}")
    print("\n")
    print(f"Body :\n{paragraphs}")
    
print_article()
    
title, subtitle, paragraphs = scrape_article()    
print_article()

# Close the driver if not closing the browser manually
driver.close()
    