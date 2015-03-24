#!/bin/bash
# BASC Macrochan Scraper: 1-search-query.sh
# This Bash script uses Wget to download all image search queries from Macrochan.
# The HTML search queries can then be parsed with other scripts to extract all image URLs/IDs.

# check if argument was provided
if [ $# -eq 0 ]; then
    echo "Usage: $0 <total images on Macrochan>"
    exit 1
fi

# arguments
IMAGEAMT=$1					# 1st arg: total amount of images
DEFAULTDELAY=5		  		# default delay is 5
DELAY=${2:-DEFAULTDELAY}	# 2nd arg: delay between each query download

# default parameters
SITE="https://macrochan.org/search.php?&offset="
OFFSET=20			# increment count per offset. default 20
OUTFOLDER="search"

# calculate final offset with this algorithm:
#   finalOffset = numOfImages - (numOfImages % 20)
FINALOFFSET=$(($IMAGEAMT - ($IMAGEAMT % $OFFSET)))

# create a folder to store search output
if [[ ! -e $OUTFOLDER ]]; then
    mkdir $OUTFOLDER
elif [[ ! -d $OUTFOLDER ]]; then
    echo "'$OUTFOLDER' already exists but is not a directory" 1>&2
fi

# wget loop until the total image amount is reached
COUNTER=0
while [  $COUNTER -lt $IMAGEAMT ]; do
	# download the search query as HTML, and save to search/#.html
	wget -O "$OUTFOLDER/$COUNTER.html" "$SITE$COUNTER"
	let COUNTER=COUNTER+FINALOFFSET		# offset each time
	sleep $DELAY						# delay between queries
done