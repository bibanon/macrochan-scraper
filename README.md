Macrochan is a gigantic archive of ancient 4chan images. It doesn't have image upload support, and has changed hands many times. Currently, it uses PHP as it's backend.

Because of it's 45,175+ image collection containing images that date from 4chan's earliest history, it would be a massive tragedy if the site were to ever collapse. The latest image came from around 2012, so this site is definitely abandoned.

This is an effort by the Bibliotheca Anonoma to archive Macrochan, using custom built Python scraping scripts to reduce strain on the server, and avoid the many pitfalls encountered by scraping an automatically generated database view.

It might also be possible to adapt this scraping script to other Image/Flash Collection websites, such as Dagobah, or even SWFChan.

## Using this Scraper

The scraper only supports Python3, so make sure to use that.

First, install all dependencies:

	sudo pip3 install robobrowser lxml

Then, run the following scripts, one by one, to dump Macrochan's entire image collection, as well as all tags:

1. Create the SQLite database, with all the necessary tables and relationships.

		python3 0-create-database.py

2. Grab all the image ids on Macrochan's database. Make sure to provide the total amount of images currently on Macrochan (as of this post, `45175`). This can take a few hours: if you lose connection, just run the same command again to continue where you left off.

		python3 1-search-query.py 45175

3. Obtain all the images themselves, and put all tags into the database. This can take a few hours: if you lose connection, just run the same command again to continue where you left off. Once this script is finished, your Macrochan dump is complete.

		python3 2-get-images.py

4. (Optional) One of the features on the author's wishlist was to have tag inheritance as shown on the [TagTree](https://macrochan.org/tagtree.php): basically, all child tags are also tagged with their parent tag, such as `Ceiling Cat` with `Cat`. If you want tag inheritance, run this script.

		python3 3-inherit-tagtree.py

Everything is stored under `macrochan-dump`, from the SQLite database `macrochan.db` to the `images/` folder. All images are sorted into folders named by their first two characters (to reduce strain on file explorers).

You can use this exported data to create your own web viewable Macrochan! Though please, make a real API with generated JSON, so we won't have to go through this horrifying export process again.