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
from ghost import Ghost

# save bandwidth by not loading images through ghost
ghost = Ghost(download_images=False)

def mkdirs(path):
	"""Make directory, if it doesn't exist."""
	if not os.path.exists(path):
		os.makedirs(path)

def download_file(local_filename, url, clobber=False):
	"""Download the given file. Clobber overwrites file if exists."""
	dir_name = os.path.dirname(local_filename)
	mkdirs(dir_name)

	if clobber or not os.path.exists(local_filename):
		i = requests.get(url)

		# if not exists
		if i.status_code == 404:
			print('Failed to download file:', local_filename, url)
			return False

		# write out in 1MB chunks
		chunk_size_in_bytes = 1024*1024  # 1MB
		with open(local_filename, 'wb') as local_file:
			for chunk in i.iter_content(chunk_size=chunk_size_in_bytes):
				local_file.write(chunk)

	return True

# Make a list of all image download links using img_ids
if __name__ == '__main__':
	# default parameters
	workdir = os.path.join(os.getcwd(), "macrochan-dump-" + time.strftime('%Y-%m-%d'))	# labeled with today's date
	mkdirs(workdir)				# ensure that the workdir exists
	site_url = "https://macrochan.org/search.php?&offset=%s"
	view_url = "https://macrochan.org/view.php?u=%s"
	img_down_url = "https://macrochan.org/images/%s/%s/%s"
	id_fname = 'img_ids.txt'			# filename of img_ids
	img_url_fname = 'img_urls.txt'		# filename of img_urls
	img_amt = sys.argv[1]		# image amount is first argument
	delay = 5		# currently set to 5 seconds by default
	offset = 20
	
	# create a new file to store img download urls
	with open(img_url_fname, 'w') as url_file:
		url_file.write("")
	
	# read each img_id from the img_ids text file
	with open(img_url_fname, 'r') as f:
		for img_url in f:
			# 3a. Use requests to download images (dump to `<1st-char>/<2nd-char>/`)
			download_file(img_url)
			
			# delay before next iteration
			print("Waiting for " + delay + " seconds...")
			time.sleep(delay)