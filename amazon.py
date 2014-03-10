#!/usr/bin/python
# coding=utf-8

# List of all imports the program uses
from bs4 import BeautifulSoup
import requests
import re
import sys
import argparse

# Define the filter criteria from command line
class FilterCriteria():
    'Contains parameters sent from command line as program arguments'
    item = ""
    sortBy = ""
    sortOrder = ""
    limit = "10"
    prime = "NO"

    def __str__(self):
        return 'FilterCriteria[ item = ' + str(self.item) + \
                ', sortBy = ' + str(self.sortBy) + \
                ', sortOrder = ' + str(self.sortOrder) + \
                ', limit = ' + str(self.limit) + \
                ', prime = ' + str(self.prime) + \
                ']'

# Define the Result class which contains data to be printed
class SearchResult():
    'Class which contains search results details that need to be printed.'
    resultId = ""
    name = ""
    price = ""
    rating = ""
    reviews = ""
    url = ""

    def __str__(self):
        return str(self.name) + \
            '\nPrice: ' + str(self.price) + \
            '\nRating: ' + str(self.get_rating_stars()) + \
            ' (' + str(self.get_review_count()) + ' reviews)' + \
            '\nUrl: ' + str(self.url)

    def get_rating_stars(self):
        oneStar = '★'
        zeroStar = '☆'
        ratingNum = 0 if self.rating == '' else self.rating[:self.rating.find(' ')]
        ratingNum = int(round(float(ratingNum), 0))

        # Prepeare the star listing based on rating number
        stars = ''
        for i in xrange(ratingNum):
            stars += oneStar
        for i in xrange( 5 - ratingNum ):
                stars += zeroStar
        
        return stars

    def get_review_count(self):
        return '0' if self.reviews.strip() == '' else self.reviews
    
    def get_price_as_number(self):
        price_as_number = self.price[1:] if self.price.find(' ') == -1 \
                            else self.price[1:self.price.find(' ')]
        return float(price_as_number)

    def __repr__(self):
        return repr((self.name, self.get_price_as_number(), self.rating))



def extract_search_result_from_div(htmlDiv):
    'Method to extract all printable information from a result DIV tag'
    searchResult = SearchResult()
    searchResult.resultId = htmlDiv.get('id')
    
    try:
        bSoup = BeautifulSoup(str(htmlDiv))
    
        # Parse name and URL
        for prodDiv in bSoup.find_all(class_='productTitle'):
            searchResult.name = prodDiv.text.strip()
            for child in prodDiv.contents:
                if str(child.name).lower() == 'a':
                    # Line below worked. However, I commented it to get it
                    # from the "child" object.
                    # searchResult.url = prodDiv.contents[0].get('href')
                    searchResult.url = child.get('href')
                    break # Exit the loop as we expect only 1 result anyway
    
        # Parse price
        for priceDiv in bSoup.find_all(class_='newPrice'):
            for child in priceDiv.contents:
                if str(child.name).lower() == 'span':
                    searchResult.price = child.text
                    break # Exit the loop
        
        # Parse review count
        for reviewCount in bSoup.find_all(class_='starsAndPrime'):
            searchResult.reviews = reviewCount.text.strip()[1:-1]

        # Parse rating
        for image in bSoup.find_all('img'):
            if image.get('title'):
                searchResult.rating = str(image.get('title'))
            
    
    except Exception as e:
        print 'Error when processing DIV: ' + str(htmlDiv)
        print 'Error details = ' + str(e)

    return searchResult


def get_results_from_amazon(filter):
    'This method requests results from Amazon and returns a list of results.'
    URL_PREFIX = 'http://www.amazon.com/s/?field-keywords='
    url = URL_PREFIX + filter.item
    # Reference: I read the code for AMAZON Prime from the below site:
    # www.pinchingyourpennies.com/forums/archive/index.php/t-165590.html
    url = url + '&emi=ATVPDKIKX0DER' if filter.prime == 'PRIME' else url

    print('Processing, please wait ...')

    # Call Amazon page for raw HTML, and parse it using BeautifulSoap
    r=requests.get(url)
    soup=BeautifulSoup(r.text)

    # Store all the SearchResult instances in this list
    resultList = list()

    # Go through all DIV tags in the page that match result_XX pattern
    for htmlDiv in soup.find_all(id=re.compile('result_[0-9]*', re.I)):
        sResult = extract_search_result_from_div(htmlDiv)
        if sResult.price != '': # Ignore banner rows
            resultList.append(sResult)

    return resultList


def prepare_filter():
    'This method reads command line arguments and returns the filter criteria'
    # Parse command line parameters
    parser = argparse.ArgumentParser(
                    description='Utility to scrape search results from Amazon')
    parser.add_argument('-i', '--item',
                    help = 'Item description to query',
                    required = True)
    parser.add_argument('-s', '--sort',
                    help = 'Sort the result set by',
                    choices = ['rating', 'price', 'name'],
                    default = 'price',
                    required = False)
    parser.add_argument('-a', '--asc',
                    help = 'Sort order ascending',
                    nargs = '?',
                    const = 'ASC',
                    default = 'asc',
                    required = False)
    parser.add_argument('-d', '--desc',
                    help = 'Sort order descending',
                    nargs = '?',
                    const = 'DESC',
                    required = False)
    parser.add_argument('-l','--limit',
                    help = 'Limit the number of results displayed to how many',
                    required = False)
    parser.add_argument('-p','--prime',
                    help = 'Show only results with Prime shipping',
                    nargs = '?',
                    const = 'PRIME',
                    required = False)
    args = parser.parse_args()

    # Populate the filter criteria with these options
    filter = FilterCriteria()
    filter.item = args.item
    filter.sortBy = args.sort
    filter.sortOrder = 'ASC' if args.asc else filter.sortOrder
    filter.sortOrder = 'DESC' if args.desc else filter.sortOrder
    filter.limit = args.limit if args.limit else "10"
    filter.prime = 'PRIME' if args.prime else filter.prime

    return filter


def sort_results(filter, resultList):
    'Method to sort results based on request by user'
    sortedList = list()
    
    if filter.sortBy == 'price':
        sortedList = sorted( resultList, key=lambda searchResult: searchResult.get_price_as_number())
    elif filter.sortBy == 'name':
        sortedList = sorted( resultList, key=lambda searchResult: searchResult.name)
    elif filter.sortBy == 'rating':
        sortedList = sorted( resultList, key=lambda searchResult: searchResult.rating)

    if filter.sortOrder == 'DESC':
        sortedList.reverse()
    
    return sortedList

def main_program():
    'This method contains the control logic for using other functions defined'
    try:
        filter = prepare_filter()
        resultList = get_results_from_amazon(filter)
        sortedList = sort_results(filter, resultList)
        
        counter = 0;
        for result in sortedList: # Print sorted results to console
            print result
            print # Give an emtpy line on console after each result
            counter += 1
            if counter >= int(filter.limit, base = 10):
                break # Print only the top limit values when specified
    except Exception as e:
        print 'Unfortunately, an error occured when running this program.'
        print 'Please provide the following details to help me resolve it.'
        print 'Error details = ' + str(e)

# Execute the program
main_program()

