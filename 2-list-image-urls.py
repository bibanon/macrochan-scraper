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
from urllib.parse import urlparse
from urllib.parse import parse_qs
from ghost import Ghost

# save bandwidth by not loading images through ghost
ghost = Ghost(download_images=False)

def mkdirs(path):
	"""Make directory, if it doesn't exist."""
	if not os.path.exists(path):
		os.makedirs(path)

# Make a list of all image download links using img_ids
if __name__ == '__main__':
	# default parameters
	workdir = os.path.join(os.getcwd(), "macrochan-dump-" + time.strftime('%Y-%m-%d'))	# labeled with today's date
	mkdirs(workdir)				# ensure that the workdir exists
	site_url = "https://macrochan.org/search.php?&offset=%s"
	view_url = "https://macrochan.org/view.php?u=%s"
	img_down_url = "https://macrochan.org/images/%s/%s/%s"
	id_fname = os.path.join(workdir, 'img_ids.txt')			# filename of img_ids
	img_url_fname = os.path.join(workdir, 'img_urls.txt')		# filename of img_urls
	db_fname = os.path.join(workdir, 'macrochan.db' )		# filename of database
	delay = 5		# currently set to 5 seconds by default
	offset = 20
	
	# create a new file to store img download urls
	with open(img_url_fname, 'w') as url_file:
		url_file.write("")
	
	# create a database to store macrochan data
	conn = sqlite3.connect(db_fname)
	c = conn.cursor()

	# enable foreign key support
	c.execute('''PRAGMA foreign_keys = ON''')

	# create `images` table
	c.execute('''CREATE TABLE images (
	  imageid text PRIMARY KEY,
	  imageext text,
	  imageurl text,
	  imageview text
	)''')

	# create tags table
	c.execute('''CREATE TABLE tags (
	  tagname text PRIMARY KEY
	)''')

	# create linking table
	c.execute('''CREATE TABLE taglink (
	  imageid text,
	  tagname text,
	  FOREIGN KEY(imageid) REFERENCES images(imageid)
	  FOREIGN KEY(tagname) REFERENCES tags(tagname)
	)''')

	# read each img_id from the img_ids text file
	with open(id_fname, 'r') as f:
		for index, line in enumerate(f):
			# strip all whitespace/newlines from line
			img_id = line.rstrip()

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

			# create folders to store JSON
			img_dir = os.path.join(workdir, img_id[:1], img_id[1:2])
			mkdirs(img_dir)
			json_fname = img_id + ".json"
			json_path = os.path.join(img_dir, json_fname)
			
			# construct json for this image
			json_data = [
				  {
				    "image-ext": img_ext,
				    "image-id": img_id,
				    "image-url": img_url,
				    "image-view": view_url,
				    "tags": tags
				  }
				]
			
			# save json to file
			with open(json_path, 'w') as json_file:
				json_file.write(json.dumps(json_data, sort_keys=True, indent=2, separators=(',', ': ')))
			
			# insert image data into database
			list = [img_id, img_ext, img_url, view_url]
			c.execute('INSERT INTO images (imageid, imageext, imageurl, imageview) VALUES (?,?,?,?)', list)

			# insert tag data into database
			# OR IGNORE used to avoid duplicating tags, since we will encounter them many times 
			for tag in tags:
				list = [tag]
				c.execute('INSERT OR IGNORE INTO tags VALUES (?)', list)

			# link current images to many tags
			for tag in tags:
				list = [img_id, tag]
				c.execute('INSERT INTO taglink (imageid, tagname) VALUES (?,?)', list)

			# display all linking table data for current image entry
			list = [img_id]
			for row in c.execute('SELECT imageid, tagname FROM taglink WHERE imageid = ? ORDER BY tagname', list):
			        print(row)

			# Save (commit) the database changes
			conn.commit()

			# delay before next iteration
			print("Waiting for %d seconds..." % delay)
			time.sleep(delay)

		# close sqlite database
		conn.close()