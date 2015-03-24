#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# BASC Macrochan Scraper: 2-list-image-urls.py
# 
# This script is designed to transition from our original flat file
# url dump structure, and migrate to a sqlite database.
# It is only meant to recover our preexisting work with flat 
# files, and is not needed for future users.

import os
import time
import sqlite3

# provides mkdirs and download_file
from utils import *

# Open up list of all image download links using img_ids
if __name__ == '__main__':
	id_fname = 'img_ids.txt'			# filename of img_ids
	view_url = "https://macrochan.org/view.php?u=%s"

	# connect to the database to store image metadata
	conn = sqlite3.connect('macrochan.db')
	c = conn.cursor()

	# read each img_id from the img_ids text file
	with open(id_fname, 'r') as f:
		for index, line in enumerate(f):
			# tell user what number we are on
			print("Inserting ID # %d" % index)

			# strip all whitespace/newlines from line
			img_id = line.rstrip()

			# insert image data into database
			# don't know img_exts or img_url yet, those are null
			list = [img_id, None, None, view_url % img_id]
			c.execute('INSERT OR IGNORE INTO images (imageid, imageext, imageurl, imageview) VALUES (?,?,?,?)', list)

			# sanity check, but it slows things down
			"""
			# display current image entry
			for row in c.execute('SELECT imageid FROM images WHERE imageid = ?', [img_id]):
					print(row)
			"""

			# Save (commit) the database changes
			conn.commit()

	# close sqlite database
	conn.close()
