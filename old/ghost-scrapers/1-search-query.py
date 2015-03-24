#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# BASC Macrochan Scraper: 1-search-query.py
#
# This script utilizes Macrochan's search queries to 
# gather all image IDs into the file `img_ids.txt`.
#
# Because Macrochan's HTML pages utilize Javascript to 
# initiate queries, the Ghost.js headless browser is 
# required to generate HTML views. It is also useful for
# gathering data with Javascript parsing.
# 
# Dependencies:
#    pip install bs4
#    pip install Ghost.py

import json
import os
import sys
import time
import sqlite3
from ghost import Ghost

# our own libraries
from utils import *
from sqlfuncs import *

# save bandwidth by not loading images through ghost
ghost = Ghost(download_images=False)

def mkdirs(path):
	"""Make directory, if it doesn't exist."""
	if not os.path.exists(path):
		os.makedirs(path)

if __name__ == '__main__':
	# check if an argument was given
	if(len(sys.argv) < 2):
		print("Please provide the total amount of images on Macrochan.")
		print("You can find this on: https://macrochan.org/search.php")
		print("Usage: %s <amount-of-images>" % sys.argv[0])
		sys.exit(1)

	# default parameters
	workdir = os.path.join(os.getcwd(), "macrochan-dump-" + time.strftime('%Y-%m-%d'))	# labeled with today's date
	mkdirs(workdir)				# ensure that the workdir exists
	site_url = "https://macrochan.org/search.php?&offset=%s"
	view_url = "https://macrochan.org/view.php?u=%s"
	img_down_url = "https://macrochan.org/images/%s/%s/%s"
	id_path = os.path.join(workdir, 'img_ids.txt')			# filename of img_ids
	db_fname = os.path.join(workdir, 'macrochan.db' )		# filename of database
	img_amt = int(sys.argv[1])			# image amount is first argument
	delay = 5		# currently set to 5 seconds by default
	offset = 20
	
	# calculate final offset with this algorithm:
	#   finalOffset = numOfImages - (numOfImages % 20)
	finaloffset = img_amt - (img_amt % offset)

	# connect to the database to store image metadata
	conn = sqlite3.connect(db_fname)
	c = conn.cursor()

	# determine amount of rows in table, and calculate first offset
	# should be 0 for empty database
	c.execute('SELECT COUNT(*) FROM images')
	count = c.fetchall()
	row_amt = count[0][0]
	print("Table 'images' has {} rows.".format(row_amt))
	firstoffset = row_amt - (row_amt % offset)

	# Make search queries and place image IDs in list
	for i in range(firstoffset, finaloffset + 1, offset):				# for loop, jumps by offset
		# set URL by offset
		url = site_url % str(i)
		
		# inform user of progress, in which section
		print("Downloading offset: %d-%d" % (i + 1, i + offset) )

		# open the webpage
		page = ghost.open(url)

		# retrieve all imageview `view.php` links from the web page into python list
		img_ids = ghost.evaluate("""
								var listRet = [];   // empty list
								// grab all `<a href=>` tags with `view`
								var links = document.querySelectorAll("a[href*=view]");

								// regex to find img_ids
								var find_img_id = /^.+\?u=(.+)$/g;
								
								// loop to check every link
								for (var i=0; i<links.length; i++){
									// only return img_ids
									listRet.push(links[i].href.replace(find_img_id, "$1"));
								}
								listRet;            // return list
								""")
			
		# save all image ids to the database
		for img_id in img_ids[0]:
			# we don't know imageext or imageurl yet, so send NULL
			list = [img_id, None, None, view_url % img_id]
			c.execute('INSERT OR IGNORE INTO images (imageid, imageext, imageurl, imageview) VALUES (?,?,?,?)', list)
		# save changes to database when finished
		conn.commit()

		# delay before next iteration
		print("Waiting for " + str(delay) + " seconds...")
		time.sleep(delay)
	
	# close the database at the end of loop
	c.close()
	print("Dump complete. Now run 2-list-image-urls.py .")
