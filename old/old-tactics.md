Here are some old tactics we used to use, but no longer need now. However, they might be useful in the future.

## Ghost.py

For some sites, when obtaining the HTML, we encounter a dilemma. Sometimes the data we need is procedurally generated with Javascript. This is a big issue, since it requires an entire Javascript engine (like on your hulking browser) to generate, more than what `requests` or `urllib` can provide.

The only solution is to use a real browser, that uses the Webkit engine. But not just any browser: a scriptable, robot-commandable, API interface driven browser, such as PhantomJS, or Ghost.py. This isn`t as insane as it sounds: Ghost.py uses the handy Webkit engine provided by PyQt/PySide: which most Linux users probably have installed already.

Here's an example, where we grab data from Macrochan.

We first create a Ghost object, and save bandwidth by telling it not to download thumbnails that we won't use.

```python
# save bandwidth by not loading images through ghost
ghost = Ghost(download_images=False)
```

We then use Ghost.py to open a website, inside the `for` loop:

```python
for i in range(0, img_amt, offset):
	# open the webpage
	page = ghost.open("https://macrochan.org/search.php?&offset=%d" % i)
```

Since Ghost.py can execute arbitrary Javascript as well, we use the following Javascript code with `.querySelectorAll()` to grab the image ids:

```js
// the output of this javascript is evaluated through ghost, and copied over to the list `img_ids` in Python.
// img_ids = ghost.evaluate("""<insert javascript here>""")
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
listRet;            // return list to python as `img_ids` list
```

### 2-list-images.py

I use the following javascript on Ghost.py to obtain all the image URLs, and extensions:

```js
var listRet = [];   // empty list
// grab all `<img src=>` tags with `view`
var links = document.querySelectorAll("img[src*=images]");
// loop to check every link
for (var i=0; i<links.length; i++){
	// return src= links
	listRet.push(links[i].src);
}
listRet;            // return list
```

Then, this javascript is used to obtain all tags:

```js
var listRet = [];   // empty list
// grab all `<a href=>` tags with `tags`
var links = document.querySelectorAll("a[href*=tags]");

// loop to check every link
for (var i=0; i<links.length; i++){
	// return href= links
	listRet.push(links[i].href);
}
listRet;            // return list
```

To grab the pure tag names, and get rid of the rest of the URL, we use `urllib.parse`:

```python
# extract tag strings from tag urls
tags = []
for tag_url in tag_urls[0]:
	tags.append(parse_qs(urlparse(tag_url).query)['tags'][0])	
```
 
## Create JSON Metadata

> **Note:** Since we use a SQLite database, there is no need for flat file JSON metadata anymore, which can be difficult to update. If we do create a website in the future, just procedurally generate the JSON from the database, just like an API.

We need to create an accompanying JSON metadata file for each image to store source URL, file extensions, and all tags. We'll use the filename `<image-ID>.json`. The format will be as follows:

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

Here are the scripts we used to dump metadata to JSON. We used this before we moved to a SQLite database. 

```python
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
```