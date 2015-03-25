#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# BASC Macrochan Scraper: 2-list-image-urls.py
#
# This script uses the file `img_ids.txt` to check
# Macrochan's image views, so the image URLs (with the
# all important filename extension) are saved to
# `img_urls.txt`.
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
import time
import sqlite3
import re
import sys
from urllib.parse import urlparse
from urllib.parse import parse_qs
from robobrowser import RoboBrowser

# our own libraries
from utils import *

# Make a list of all image download links using img_ids
if __name__ == '__main__':
	# default parameters
	workdir = os.path.join(os.getcwd(), "macrochan-dump")
	mkdirs(workdir)				# ensure that the workdir exists
	site_url = "https://macrochan.org/search.php?&offset=%s"
	view_url = "https://macrochan.org/view.php?u=%s"
	macrochan_url = "https://macrochan.org"
	img_down_url = "https://macrochan.org/images/%s/%s/%s"
	db_fname = os.path.join(workdir, 'macrochan.db' )		# filename of database
	delay = 5		# currently set to 5 seconds by default
	offset = 20
	
	# create a robot browser
	browser = RoboBrowser()
	
	# connect to the database to store image 
	conn = sqlite3.connect(db_fname)
	c = conn.cursor()

	# sql query to obtain all imageids from database sorted by rowid, store as list for later
	c.execute('SELECT imageid FROM images ORDER BY rowid')
	data = c.fetchall()

	# determine amount of rows in table, and calculate where to stop
	# should be 0 for empty database
	c.execute('SELECT COUNT(*) FROM images')
	count = c.fetchall()
	row_amt = count[0][0]
	print("Table 'images' has {} rows.".format(row_amt))
	stop = row_amt

	# determine amount of rows in table with imageext, and calculate where to start
	# should be 0 at beginning
	c.execute('SELECT COUNT(*) FROM images WHERE imageext IS NOT NULL')
	count = c.fetchall()
	row_amt = count[0][0]
	print("Starting at {} on table 'images'.".format(row_amt + 1))
	start = row_amt

	# read each img_id from the database
	for index in range(start, stop):
		# SQL queries are stored in tuples of tuples, only need first value of each query
		img_id = data[index][0]

		# set URL by img_id
		url = view_url % img_id

		# inform user of progress
		print("Obtaining Image Download URL # {}: {}".format(index + 1, url))


		# open the webpage, check for connection error
		try:
			browser.open(url)
		except requests.exceptions.RequestException as e:
			print("Unable to connect to Macrochan, restore your internet connection.")
			print("Run this script again to continue where you left off.")
			sys.exit(1)

		# beautifulsoup - find first <img src=> HTML tag of main image to obtain file extension
		img_url = macrochan_url + browser.find('img').get('src', '/')
		img_ext = os.path.splitext(img_url)[1]

		# beautifulsoup - find all <a href=> HTML tags that contain image tags
		tags = []
		tag_regex = re.compile(r"tags")
		for anchor in browser.find_all('a'):
			this_tag = anchor.get('href', '/')
			if (re.search(tag_regex, this_tag)):
				# extract tag strings from tag urls
				# http://macrochan.org/search.php?tags=Motivational+Poster
				tags.append(parse_qs(urlparse(this_tag).query)['tags'][0])
		
		# download the images
		# save images to folder `macrochan-dump-*/images/<1st-char>/<2nd-char>/<image-id>.ext`
		img_filename = os.path.join(workdir, "images", img_id[:1], img_id[1:2], img_id + img_ext)
		try:
			download_file(img_filename, img_url, clobber=True)
		except requests.exceptions.RequestException as e:
			print("Unable to connect to Macrochan, restore your internet connection.")
			print("Run this script again to continue where you left off.")
			sys.exit(1)
		
		# add img_ext and img_url to current img_id in database
		list = [img_ext, img_url, img_id]
		c.execute("""UPDATE images SET imageext = ?, imageurl = ? WHERE imageid = ?""", list)

		# insert tag data into database
		# OR IGNORE used to avoid duplicating tags
		for tag in tags:
			c.execute('INSERT OR IGNORE INTO tags VALUES (?)', [tag])

		# link current images to many tags
		# OR IGNORE used to avoid duplicating taglinks
		for tag in tags:
			c.execute('INSERT OR IGNORE INTO taglink (imageid, tagname) VALUES (?,?)', [img_id, tag])

		# display all linking table data for current image entry
		for row in c.execute('SELECT imageid, tagname FROM taglink WHERE imageid = ? ORDER BY tagname', [img_id]):
		        print(row)

		# Save (commit) the database changes
		conn.commit()

		# delay before next iteration
		print("Waiting for %d seconds..." % delay)
		time.sleep(delay)

	# close sqlite database once finished
	conn.close()
