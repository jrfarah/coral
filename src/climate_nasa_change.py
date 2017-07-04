import re
import urllib2 
from BeautifulSoup import BeautifulSoup as soup
import ssl
import requests

url = "https://climate.nasa.gov"
context = ssl._create_unverified_context()
gcontext = ssl.SSLContext(ssl.PROTOCOL_TLSv1)
web_soup = soup(requests.get(url, verify=False).text)

l = []

# get main-content div
main_div = web_soup.findAll(name="div", attrs={'class': 'change_number'})
for element in main_div:
	print element
	l.append(float(str(element)[27:-7]))

print l