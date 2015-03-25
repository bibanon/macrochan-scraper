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
import requests
from urllib.parse import urlparse
from urllib.parse import parse_qs
from ghost import Ghost

# our own libraries
from utils import *

# save bandwidth by not loading images through ghost
ghost = Ghost(download_images=False)

# Make a list of all image download links using img_ids
if __name__ == '__main__':
	# default parameters
	workdir = os.path.join(os.getcwd(), "macrochan-dump-" + time.strftime('%Y-%m-%d'))	# labeled with today's date
	mkdirs(workdir)				# ensure that the workdir exists
	site_url = "https://macrochan.org/search.php?&offset=%s"
	view_url = "https://macrochan.org/view.php?u=%s"
	img_down_url = "https://macrochan.org/images/%s/%s/%s"
	db_fname = os.path.join(workdir, 'macrochan.db' )		# filename of database
	delay = 5		# currently set to 5 seconds by default
	offset = 20
	
	# connect to the database to store image 
	conn = sqlite3.connect(db_fname)
	c = conn.cursor()

	# sql query to obtain all imageids from database sorted by rowid
	c.execute('SELECT imageid FROM images ORDER BY rowid')
	data = c.fetchall()

	# determine amount of rows in table, and calculate where to stop
	# should be 0 for empty database
	c.execute('SELECT COUNT(*) FROM images')
	count = c.fetchall()
	row_amt = count[0][0]
	print("Table 'images' has {} rows.".format(row_amt))
	stop = row_amt - (row_amt % offset)

	# determine amount of rows in table with imageext, and calculate where to start
	# should be 0 at beginning
	c.execute('SELECT COUNT(*) FROM images WHERE imageext IS NOT NULL')
	count = c.fetchall()
	row_amt = count[0][0]
	print("Starting at {} on table 'images'.".format(row_amt))
	start = row_amt - (row_amt % offset)

	# read each img_id from the database
	for index, row in enumerate(data):
		# SQL queries are stored in tuples, only need first value 
		img_id = row[0]

		# inform user of progress
		print("Obtaining Image Download URL # %d:" % index + 1, view_url % img_id)

		# set URL by img_id
		url = view_url % img_id

		# open the webpage
		page = ghost.open(url)

		# retrieve all img links
		img_urls = ghost.evaluate("""
								var listRet = [];   // empty list
								// grab all `<img src=>` tags with `view`
								var links = document.querySelectorAll("img[src*=images]");
								
								// loop to check every link
								for (var i=0; i<links.length; i++){
									// return src= links
									listRet.push(links[i].src);
								}
								listRet;            // return list
								""")
		
		# open the file and save the link to it
		img_url = ""		# storing first img_url for JSON dumping
		img_ext = ""		# storing image file extension for JSON dumping
		with open(img_url_fname, 'a') as url_file:
			for line in img_urls[0]:
				img_url = line
				temp_url, img_ext = os.path.splitext(img_url)
				url_file.write("%s\n" % img_url)

		# scrape tags from image view URL and dump to <image-id>.json
		tag_urls = ghost.evaluate("""
				var listRet = [];   // empty list
				// grab all `<a href=>` tags with `tags`
				var links = document.querySelectorAll("a[href*=tags]");
				
				// loop to check every link
				for (var i=0; i<links.length; i++){
					// return href= links
					listRet.push(links[i].href);
				}
				listRet;            // return list
				""")
		
		# extract tag strings from tag urls
		tags = []
		for tag_url in tag_urls[0]:
			tags.append(parse_qs(urlparse(tag_url).query)['tags'][0])	
		
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
