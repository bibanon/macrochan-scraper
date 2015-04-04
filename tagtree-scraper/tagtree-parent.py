#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# BASC Macrochan Scraper: tagtree.py
# This script imports a hierarchical tagtree, finds each tag's parent, and puts it into the SQLite database.

import json

def main():
	tagtree = json.loads(open("tagtree.json").read())
	
	print(tagtree["#Animals"])
	
	# find each item's parent
	for i in tagtree.keys():
		if (i.items())
		print()

if __name__ == "__main__":
	main()