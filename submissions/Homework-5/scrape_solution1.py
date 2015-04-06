#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import sys
import time
import argparse
import logging
import requests
from BeautifulSoup import BeautifulSoup


log = logging.getLogger(__name__)
log.setLevel(logging.ERROR)
loghandler = logging.StreamHandler(sys.stderr)
loghandler.setFormatter(logging.Formatter("[%(asctime)s] %(message)s"))
log.addHandler(loghandler)

base_url = "http://www.tripadvisor.com/"

#TASK2 
#Gets a list of all the review pages
review_page_urls = []


#TASK2
#Dictionary of hotels and its stats
hotels_dict = {} 

user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2272.76 Safari/537.36"



def get_city_page(city, state, datadir):
    """ Returns the URL of the list of the hotels in a city. Corresponds to
    STEP 1 & 2 of the slides.

    Parameters
    ----------
    city : str

    state : str

    datadir : str


    Returns
    -------
    url : str
        The relative link to the website with the hotels list.

    """
    # Build the request URL
    url = base_url + "city=" + city + "&state=" + state
    # Request the HTML page
    headers = {'User-Agent': user_agent}
    response = requests.get(url, headers=headers)
    html = response.text.encode('utf-8')
    with open(os.path.join(datadir, city + '-tourism-page.html'), "w") as h:
        h.write(html)

    # Use BeautifulSoup to extract the url for the list of hotels in
    # the city and state we are interested in.

    # For example in this case we need to get the following href
    # <li class="hotels twoLines">
    # <a href="/Hotels-g60745-Boston_Massachusetts-Hotels.html" data-trk="hotels_nav">...</a>
    soup = BeautifulSoup(html)
    li = soup.find("li", {"class": "hotels twoLines"})
    city_url = li.find('a', href=True)
    return city_url['href']


def get_hotellist_page(city_url, page_count, city, datadir='data/'):
    """ Returns the hotel list HTML. The URL of the list is the result of
    get_city_page(). Also, saves a copy of the HTML to the disk. Corresponds to
    STEP 3 of the slides.

    Parameters
    ----------
    city_url : str
        The relative URL of the hotels in the city we are interested in.
    page_count : int
        The page that we want to fetch. Used for keeping track of our progress.
    city : str
        The name of the city that we are interested in.
    datadir : str, default is 'data/'
        The directory in which to save the downloaded html.

    Returns
    -------
    html : str
        The HTML of the page with the list of the hotels.
    """
    url = base_url + city_url
    # Sleep 2 sec before starting a new http request
    time.sleep(2)
    # Request page
    headers = { 'User-Agent' : user_agent }
    response = requests.get(url, headers=headers)
    html = response.text.encode('utf-8')
    # Save the webpage
    with open(os.path.join(datadir, city + '-hotelist-' + str(page_count) + '.html'), "w") as h:
        h.write(html)
    return html


#*TODO*
def get_hotel_page(hotel_url, hotel_name, datadir='data/'):

    url = base_url + city_url
    # Sleep 2 sec before starting a new http request
    time.sleep(2)
    # Request page
    headers = { 'User-Agent' : user_agent }
    response = requests.get(url, headers=headers)
    html = response.text.encode('utf-8')
    # Save the webpage
    with open(os.path.join(datadir, city + '-hotelist-' + str(page_count) + '.html'), "w") as h:
        h.write(html)
    return html


#ERROR OCCURS IN THIS FUNCTION 
def parse_hotellist_page(html):
    """Parses the website with the hotel list and prints the hotel name, the
    number of stars and the number of reviews it has. If there is a next page
    in the hotel list, it returns a list to that page. Otherwise, it exits the
    script. Corresponds to STEP 4 of the slides.

    Parameters
    ----------
    html : str
        The HTML of the website with the hotel list.

    Returns
    -------
    URL : str
        If there is a next page, return a relative link to this page.
        Otherwise, exit the script.
    """
    soup = BeautifulSoup(html)
    # Extract hotel name, star rating and number of reviews
    hotel_boxes = soup.findAll('div', {'class' :'listing wrap reasoning_v5_wrap jfy_listing p13n_imperfect'})
    if not hotel_boxes:
        log.info("#################################### Option 2 ######################################")
        hotel_boxes = soup.findAll('div', {'class' :'listing_info jfy'})
    if not hotel_boxes:
        log.info("#################################### Option 3 ######################################")
        hotel_boxes = soup.findAll('div', {'class' :'listing easyClear  p13n_imperfect'})

    for hotel_box in hotel_boxes:

        #TASK2 -- THIS IS WHERE I MAKE THE LIST OF HOTEL REVIEW LINKS
        #Grabs the link for the hotel's review page
        review_link = hotel_box.find("a",{"class": "property_title"})
        review_link = review_link['href']

        
        review_page_urls.append(review_link)
  

        #print "REVIEW PAGE LINK"
        #print review_link['href']

        

    
        
        #Hotel name
        hotel_name = hotel_box.find("a", {"target" : "_blank"}).find(text=True)
        log.info("Hotel name: %s" % hotel_name.strip())

        stars = hotel_box.find("img", {"class" : "sprite-ratings"})
        if stars:
            log.info("Stars: %s" % stars['alt'].split()[0])

        num_reviews = hotel_box.find("span", {'class': "more"}).findAll(text=True)
        if num_reviews:
            log.info("Number of reviews: %s " % [x for x in num_reviews if "review" in x][0].strip())

    # Get next URL page if exists, otherwise exit
    div = soup.find("div", {"class" : "pagination paginationfillbtm"})


    # check if this is the last page
    if div.find('span', {'class' : 'guiArw pageEndNext'}):
        log.info("We reached last page")
        sys.exit() #NEED TO CHANGE THIS LATER

    # If not, return the url to the next page
    hrefs = div.findAll('a', href= True)


    for href in hrefs:
        href_class = href['class']
        href_class = href_class.strip()
        if href_class == 'guiArw sprite-pageNext':
            log.info("Next url is %s" % href['href'])
            return href['href']


#TASK 2
#Parses review pages
def parse_review_page(url):
    #print "ALSO HERE"
    headers = {'User-Agent': user_agent}
    response = requests.get(url,headers=headers)
    html = response.text.encode('utf-8')
    soup = BeautifulSoup(html)



    #Gets the hotel name
    hotel_name_div = soup.find("h1",{"id":"HEADING"}).getText()

    #Gets the info box
    info_box = soup.find("div",{"class":"content wrap trip_type_layout"})

    #Gets the number of Excellent, Very Good, Average, Poor, et. ratings
    reviews = info_box.findAll("span",{"class":"text"})
    reviews_numbers = info_box.findAll("span",{"class":"compositeCount"})

    #Gets trip type (Family, Couples, Solo, etc) 
    type_div = info_box.find("div",{"class":"trip_type"})
    type_num = type_div.findAll("div",{"class":"value"})

    #Gets rating summary
    sum_box = info_box.find("div",{"id":"SUMMARYBOX"})
    imgs = sum_box.findAll("img",{"src":"http://e2.tacdn.com/img2/x.gif"})


    #print hotel_name_div
    
    #Gets types and converts to a list
    reviews_nums_list = []
    for n in reviews_numbers:
        v = n.getText()
        v = v.replace(',',"")
        reviews_nums_list.append(int(v))
        
        
    type_nums_list = []
    for n in type_num:
        v = n.getText()
        v = v.replace(',',"")
        type_nums_list.append(int(v))
        
    rate_sum_list = []
    for n in imgs:
        v = n['alt'].split()
        rate_sum_list.append(float(v[0]))



  

    hotels_dict[hotel_name_div] = {}

    hotels_dict[hotel_name_div]['Excellent'] = reviews_nums_list[0]
    hotels_dict[hotel_name_div]['Very good'] = reviews_nums_list[1]
    hotels_dict[hotel_name_div]['Average'] = reviews_nums_list[2]
    hotels_dict[hotel_name_div]['Poor'] = reviews_nums_list[3]
    hotels_dict[hotel_name_div]['Terrible'] = reviews_nums_list[4]

    hotels_dict[hotel_name_div]['Families'] = type_nums_list[0]
    hotels_dict[hotel_name_div]['Couples'] = type_nums_list[1]
    hotels_dict[hotel_name_div]['Solo'] = type_nums_list[2]
    hotels_dict[hotel_name_div]['Business'] = type_nums_list[3]

    hotels_dict[hotel_name_div]['Location'] = rate_sum_list[0]
    hotels_dict[hotel_name_div]['Sleep Quality'] = rate_sum_list[1]
    hotels_dict[hotel_name_div]['Rooms'] = rate_sum_list[2]
    hotels_dict[hotel_name_div]['Service'] = rate_sum_list[3]
    hotels_dict[hotel_name_div]['Value'] = rate_sum_list[4]
    hotels_dict[hotel_name_div]['Cleanliness'] = rate_sum_list[5]

    



 

            
    

#Returns the finshied hotels_dict after parse_review_page
def task2_dict():
    return hotels_dict
    
    
#Returns the list of review_page_urls after scrape_hotels has run 
def task2_list():
    return review_page_urls
    

    

#TASK 2
def parse_all_reviews(pg_urls):
    print "HERE"
    
    

    for link in pg_urls:
        headers = {'User-Agent': user_agent}
        
        url = base_url+link
        #print url
        #print
 #       response = requests.get(url,headers=headers)
 #       print response
 #       html = response.text.encode('utf-8')
        parse_review_page(url)
        
        
    

        


    
    

#TASK 2
#TODO
#Parses all the review pages
def parse_review_pages():
    return None

def scrape_hotels(city, state, datadir='data/'):
    """Runs the main scraper code

    Parameters
    ----------
    city : str
        The name of the city for which to scrape hotels.

    state : str
        The state in which the city is located.

    datadir : str, default is 'data/'
        The directory under which to save the downloaded html.
    """

    # Get current directory
    current_dir = os.getcwd()
    # Create datadir if does not exist
    if not os.path.exists(os.path.join(current_dir, datadir)):
        os.makedirs(os.path.join(current_dir, datadir))

    # Get URL to obtaint the list of hotels in a specific city
    city_url = get_city_page(city, state, datadir)
    c = 0
    while(True):
        c += 1
        html = get_hotellist_page(city_url, c, city, datadir)
        city_url = parse_hotellist_page(html)
        print review_page_urls
        

    

 



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Scrape tripadvisor')
    parser.add_argument('-datadir', type=str,
                        help='Directory to store raw html files',
                        default="data/")
    parser.add_argument('-state', type=str,
                        help='State for which the hotel data is required.',
                        required=True)
    parser.add_argument('-city', type=str,
                        help='City for which the hotel data is required.',
                        required=True)

    args = parser.parse_args()
    scrape_hotels(args.city, args.state, args.datadir)
