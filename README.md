## Archiving Macrochan

Macrochan is a gigantic archive of ancient 4chan images. It doesn't have image upload support, and has changed hands many times. Currently, it uses PHP as it's backend.

Because of it's 45,175+ image collection, we have to archive it somehow. Unfortunately, due to it's tag structure design, conventional scraping is not the best option (and we'll probably end up in infinite loops clicking random.php or every single tag link in every page).

The three things we need to preserve are:

* The Filename. This way we can retrieve it. Also
* The Tags. They should probably be stored as image metadata, or maybe used on Hydrus. 
  * **The Tag Cloud.** - Also grab the nice tag cloud

## URL Structure

Macrochan is based on an image database written in PHP (used to be Python). Thus, you make queries to the database via the web interface to get what you want, though the responses are limited to 20 files per page.

### Get List of Every Image

To get a list of every single image, rather than just one tag, just go straight to `search.php` with no arguments:

    https://macrochan.org/search.php

This will give you a page browsing system that will show all 45,175 images in the collection, 20 files at a time. The offset will increment by 20 each time.

    https://macrochan.org/search.php?&offset=0
    https://macrochan.org/search.php?&offset=20
    https://macrochan.org/search.php?&offset=40

As of 2015-03-22, since there are 45,175 images, the last page is:

    https://macrochan.org/search.php?&offset=45160

We simply need to make a list of numbers incremented by 20, all the way up to the final offset, and attach the URL `https://macrochan.org/search.php?&offset=` to the beginning. A for loop with a python script would work nicely.

The algorithm for generating the final offset (from the number of images) is:

    finalOffset = numOfImages - (numOfImages % 20)
    # example
    finalOffset = 45175 - (45175 % 20) # = 45160

The amount of images that exist in the page can be found by checking the top of [the search query,](https://macrochan.org/search.php) or by parsing the following tag: 

```html
<br><center><div id=datebar>Showing 0-20 of 45175<a href="/search.php?&offset=20"> &gt;&gt; </a></div><BR></center>
```

Since `search.php` uses Javascript to make search queries, we will need to obtain a static HTML version of each view. We put together the Bash + Wget script `1-search-query.sh` to create a whole folder of these.

Once we have a list of all the offset pages, we need to extract the image view URLs from it. [Ghost.py](http://jeanphix.me/Ghost.py/) will be necessary to make the Javascript run, and also allows us to execute handy Javascript functions such as `.querySelectorAll()`.

The key is to extract any URL encased with the following tag:

```html
<a href='/view.php?u={{image-ID}}'>
```

We use the following Javascript code to grab the image ids:

```js
var listRet = [];   // empty list
// grab all `<a href=>` tags with `view`
var links = document.querySelectorAll("a[href*=view]");

// regex to find img_ids
var find_img_id = /^.+\?u=(.+)$/g;

// loop to check every link
for (var i=0; i<links.length; i++){
	// only return img_ids
	listRet.push(links[i].href.replace(find_img_id, "$1"));
}
listRet;            // return list
```

### Obtaining the images

Now that we've obtained the image view URLs, we need to download the image itself, and then the tags on the image.

First, an image URL has the following format:

    https://macrochan.org/view.php?u=<image-ID>
    # example
    https://macrochan.org/view.php?u=FCKU54O3VGXCPJMQ5RNSZ7P7ZRQBBL4F

However, this gives you the full HTML page, rather than just the image itself. You need to use a different URL structure to grab the full image itself, since the images are stored under two nested folders of 1st ID character and 2nd ID character.

    https://macrochan.org/images/<1st-char-of-ID>/<2nd-char-of-ID>/<image-ID>
    # example
    https://macrochan.org/images/F/C/FCKU54O3VGXCPJMQ5RNSZ7P7ZRQBBL4F.jpeg

In fact, we should probably replicate the practice of storing files under nested folders by 1st ID character and 2nd ID character (e.g. `/F/C/` for `FCKU54...`), since it is easy to generate and reduces the strain on file explorers of having to display over 40,000 images at once.

After downloading the image itself, we need to create an accompanying JSON metadata file to store source URL and all tags used. We'll use the filename `<image-ID>.json`. The format will be as follows:

```json
[
  {
    "image-ext": ".jpeg",
    "image-id": "6EUABP4KV52YOVJDVFBOJ3AIBI5NKCNU",
    "image-url": "https://macrochan.org/images/6/E/6EUABP4KV52YOVJDVFBOJ3AIBI5NKCNU.jpeg",
    "image-view": "https://macrochan.org/view.php?u=6EUABP4KV52YOVJDVFBOJ3AIBI5NKCNU",
    "tags": [
      "Screencap",
      "The Next Generation"
    ]
  }
]
```

We should also put this data into a `.sqlite` database for convenient viewing. This will require an `images` table storing ImageID and file extensions, and a `tags` table storing TagName and TagURL. It will also require a linking table `taglink`, to match many ImageIDs to many Tags. 

Make sure to enable foreign key support:

```python
# enable foreign key support
c.execute('''PRAGMA foreign_keys = ON''')
```

```sqllite
CREATE TABLE images (
  imageid text PRIMARY KEY,
  imageext text,
  imageurl text,
  imageview text
)
```

```python
list = [img_id, img_ext, img_url, view_url]
c.execute('INSERT INTO images (imageid, imageext, imageurl, imageview) VALUES (?,?,?,?)', list)
```

```sqllite
CREATE TABLE tags (
  tagname text PRIMARY KEY
)
```

```python
# OR IGNORE used to avoid duplicating tags, since we will encounter them many times
for tag in tags:
  list = [tag]
  c.execute('INSERT OR IGNORE INTO tags VALUES (?)', list)
```

```sqllite
CREATE TABLE taglink (
  imageid text,
  tagname text,
  FOREIGN KEY(imageid) REFERENCES images(imageid)
  FOREIGN KEY(tagname) REFERENCES tags(tagname)
)
```

```python
for tag in tags:
  list = [img_id, tag]
  c.execute('INSERT INTO taglink (imageid, tagname) VALUES (?,?)', list)
```

## The Tag Cloud

One of Macrochan's most important aspects is it's tagging system. Each image is tagged with a certain topic word, which is then shown in the tag tree, and clickable to find all images with that specific tag.

    https://macrochan.org/tagTree.php

While we will be saving individual image tags one by one, it might be advantageous to have a pregenerated list of all images that fit that tag.

To obtain the tag tree, we should save the HTML page and convert it to Markdown "tag-tree.md" with this kind of structure: (JSON won't work due to it's complicated, and not relationally matched tag cloud)

```markdown
* #Type
  * Animated
  * Screencap
    * Anime
  * Screenshots
  * Ready to paste
  * Editable blanks
  * Shirt
  * Figurines
    * Lego
  * Broken
  * Wallpaper
  * Papercraft
```

We should probably make a pandoc bash script to do this in one go. Might as well grab [the news page](http://macrochan.org/news.php) as well.

### Tag Inheritance

As stated by the owner, one of the things he wanted to do was give tags inheritance. For example,

### Tag List Generation

Then, we grab all the tags from every image's JSON file, and make a list of all filenames that fit a certain tag. (we could grab the links from the site, but that requires offsets, takes time, and uses up server bandwidth)
