#!/usr/bin/env python
# -*- coding: utf-8 -*-
# BASC Macrochan Scraper: tagtree.py
# This script downloads and saves the tagtree HTML list to a file.
# Then, it processes the tagtree to convert it into a recursive JSON dict.

from robobrowser import RoboBrowser
import json

tagtree_fname = "tagtree.html"
json_fname = "tagtree.json"

# Converts HTML list to JSON, each entry with child entry (recursive, until None is found)
# http://stackoverflow.com/a/17850788
def dictify(ul):
    result = {}
    for li in ul.find_all("li", recursive=True):
        key = next(li.stripped_strings)
        ul = li.find("ul")
        if ul:
            result[key] = dictify(ul)
        else:
            result[key] = None
    return result

def main():
	# obtain tagtree page
	browser = RoboBrowser(history=True)
	browser.open("http://macrochan.org/tagTree.php")
	
	# dump taglist to `tagtree.html`, well-indented
	f = open(tagtree_fname, 'w')
	f.write(browser.find("ul").prettify())
	
	# convert to python dictionary
	tagtree_dict = dictify(browser.find("ul"))

	# write to formatted json
	with open(json_fname, 'w') as json_file:
		json_file.write(json.dumps(tagtree_dict, sort_keys=True, indent=2, separators=(',', ': ')))

if __name__ == '__main__':
	main()