#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# BASC Macrochan Scraper: 3-inherit-tagtree.py
# 
# 1. **Obtain the tagtree page.** We do this using good ol' RoboBrowser, and use it's BeautifulSoup bindings to find the first `ul` list. Then we dump the `ul` nested list to an html file.
# 2. **Import the nested list as XHTML through LXML etree**.  We then used xpaths to grab the parents of every single tag, for insertion in a `tags` table entry, `parent`.
# 3. **Grab the ancestors of every single tag.** This way, we can implement tag inheritance, by inserting all ancestor tags into every child tag's images. LXML provides an easy getancestors() function.

import os
import json
import sqlite3
from lxml import etree
from robobrowser import RoboBrowser

# our own libraries
from utils import *

# tagtree URL
tagtree_url = "http://macrochan.org/tagTree.php"

# current working directory
workdir = os.path.join(os.getcwd(), "macrochan-dump")
mkdirs(workdir)				# ensure that the workdir exists
# filename of database
db_fname = os.path.join(workdir, 'macrochan.db')
tagtree_fname = os.path.join(workdir, 'tagtree.html')
tagtree_clickable_fname = os.path.join(workdir, 'tagtree-clickable.html')
json_fname = os.path.join(workdir, 'tagtree-ancestors.json')

def main():
	# obtain tagtree page
	browser = RoboBrowser(history=True)
	browser.open(tagtree_url)
	
	# obtain list of items from html
	tagtree = browser.find("ul")
	
	# dump taglist to `tagtree-clickable.html`, clickable, pretty printed
	with open(tagtree_clickable_fname, 'w') as f:
		f.write(tagtree.prettify())
	
	# remove all <a href=> tags to facilitate parsing
	for match in tagtree.findAll('a'):
		match.replaceWithChildren()
	
	# dump taglist to `tagtree.html`, plain, no <a href>
	with open(tagtree_fname, 'w') as f:
		f.write(str(tagtree))
	
	# obtain xml data from file
	treexml = etree.parse(tagtree_fname)
	
	# connect to the database
	conn = sqlite3.connect(db_fname)
	c = conn.cursor()

	# create a dict from XHTML matching tags to their ancestors
	treedict = {}
	for element in treexml.getiterator():
		# ignore repeated elements
		if (str(element.text) != "None"):
			# find all ancestor elements
			ancestorlist = []
			for ancestor in element.iterancestors():
				if (str(ancestor.tag) != "ul"): # ignore ul tags
					ancestorlist.append(ancestor.text)
			
			# add element and ancestors to dictionary (if not empty)
			if len(ancestorlist) != 0:
				treedict[element.text] = ancestorlist

	# write treedict to formatted json
	with open(json_fname, 'w') as json_file:
		json_file.write(json.dumps(treedict, sort_keys=True, indent=2, separators=(',', ': ')))

	# insert into SQLite database
	for tagname, ancestors in treedict.items():
		# element[0] is always the first parent, so insert that
		c.execute("""UPDATE tags SET parent = ? WHERE tagname = ?""", [ancestors[0], tagname])
		
		# find all images with this tagname and add additional tags for it
		image_query = c.execute("""SELECT imageid FROM taglink WHERE tagname = ?""", [tagname])
		
		for img_id in image_query:
			# link current images to all ancestor tags
			# OR IGNORE used to avoid duplicating taglinks
			for tag in ancestors:
				c.execute("""INSERT OR IGNORE INTO taglink (imageid, tagname) VALUES (?,?)""", [img_id[0], tag])
				
	# Save (commit) the database changes
	conn.commit()
		
	# close sqlite database once finished
	conn.close()

if __name__ == "__main__":
	main()