#!/bin/bash
# BASC Macrochan Scraper: Makefile
# 
# This is a build script that makes it easy to run all the 
# python scripts you need to scrape Macrochan, in order.
# 
# You can choose to just run `./dump.sh` to start the whole process.

# amount of images currently on macrochan
IMGAMT=45175

# step 0: create the database `macrochan-dump-*/macrochan.db`
python3 0-create-database.py

# step 1: start the search query
python3 1-search-query.py $IMGAMT

# step 2: obtain image URLs
python3 2-get-images.py

# step 3: implement tag inheritance
python3 3-inherit-tagtree.py

# delete all dump folders
#rm -rf macrochan-dump