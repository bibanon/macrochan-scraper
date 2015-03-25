from robobrowser import RoboBrowser
from urllib.parse import urlparse
from urllib.parse import parse_qs
import os
import re

if __name__ == '__main__':

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
	img_down_url_sml = "https://macrochan.org"
	img_url = browser.find('img').get('src', '/')
	print(img_down_url_sml + img_url)
	print(os.path.splitext(img_url)[1])
			
	"""3 - Grab Image Tags"""

	# set URL to grab
	url = "http://macrochan.org/view.php?u=HS4I4BGZ3VWZXMRMIY7AWFW6ZZ6HCNDT"

	# open the webpage
	browser.open(url)
		
	# beautifulsoup - find all <a href=> HTML tags that contain image tags
	tag_regex = re.compile(r"tags")
	for anchor in browser.find_all('a'):
		this_tag = anchor.get('href', '/')
		if (re.search(tag_regex, this_tag)):
			print(parse_qs(urlparse(this_tag).query)['tags'][0])
			