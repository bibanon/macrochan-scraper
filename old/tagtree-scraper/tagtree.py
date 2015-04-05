#!/usr/bin/env python
# -*- coding: utf-8 -*-
# BASC Macrochan Scraper: tagtree.py
# This script downloads and saves the tagtree HTML list to a file.
# Then, it processes the tagtree to convert it into a recursive JSON dict.

from robobrowser import RoboBrowser
import json

# current working directory
workdir = os.path.join(os.getcwd(), "macrochan-dump")
mkdirs(workdir)				# ensure that the workdir exists
# filename of database
db_fname = os.path.join(workdir, 'macrochan.db')
tagtree_fname = os.path.join(workdir, 'tagtree.html')

# The first step is to obtain the tagtree page. We do this using good ol' RoboBrowser, and use it's BeautifulSoup bindings to find the first `ul` list. (We then clean out all the a href links, but preferably this should not be necessary)
# The next step is to dump this `ul` nested list to an html file, so it can be imported with LXML in the next step. LXML provides an easy getancestors() function.

def main():
	# obtain tagtree page
	browser = RoboBrowser(history=True)
	browser.open("http://macrochan.org/tagTree.php")
	
	# obtain list of items from html
	tagtree = browser.find("ul")
	
	# remove all <a href=> tags to facilitate parsing
	for match in tagtree.findAll('a'):
		match.replaceWithChildren()
	
	# dump taglist to `tagtree.html`
	f = open(tagtree_fname, 'w')
	f.write(str(tagtree))

if __name__ == '__main__':
	main()