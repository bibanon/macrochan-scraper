#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# BASC Macrochan Scraper: 0-create-database.py
#
# This script creates a database to hold all the
# image metadata in a queriable location. Macrochan
# is an image database after all, it should be exported
# into one.

import sqlite3
import time

def mkdirs(path):
	"""Make directory, if it doesn't exist."""
	if not os.path.exists(path):
		os.makedirs(path)

if __name__ == '__main__':
	# current working directory
	workdir = os.path.join(os.getcwd(), "macrochan-dump-" + time.strftime('%Y-%m-%d'))	# labeled with today's date
	mkdirs(workdir)				# ensure that the workdir exists
	# filename of database
	db_fname = os.path.join(workdir, 'macrochan.db')

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

	# Save (commit) the database changes
	conn.commit()

	# close sqlite database
	conn.close()
