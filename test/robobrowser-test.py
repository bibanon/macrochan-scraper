from robobrowser import RoboBrowser
from urllib.parse import urlparse
from urllib.parse import parse_qs
import os
import re

# create a robot browser
browser = RoboBrowser(history=True)

"""1 - Grab Search Query"""

# set URL to grab
url = "http://macrochan.org/search.php?&offset=0"

# open the webpage
browser.open(url)

# beautifulsoup - find all <a href=> HTML tags that are views
view_regex = re.compile(r"view")
for anchor in browser.find_all('a'):
	view_url = anchor.get('href', '/')
	if (re.search(view_regex, view_url)):
		print(parse_qs(urlparse(view_url).query)['u'][0])

"""2 - Grab image links"""

# set URL to grab
url = "http://macrochan.org/view.php?u=JNTW3GWLMYDGS7NLSLZTHGKGPNA3OHN3"

# open the webpage
browser.open(url)
    
# beautifulsoup - find all <img src=> HTML tags that are main images
img_regex = re.compile(r"images")
for anchor in browser.find_all('img'):
	img_tag = anchor.get('src', '/')
	if (re.search(img_regex, img_tag)):
		print(os.path.basename(img_tag))