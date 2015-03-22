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

Once we have a list of all the offset pages, we need to extract the image view URLs from it. `search.php` uses Javascript to recieve it's URL lists, so we will need to obtain a static version of the 

We will use Python's BeautifulSoup library to scrape the image view URLs.

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

In fact, we should probably replicate the practice of storing files under nested folders by 1st ID character and 2nd ID character, since it is easy to generate and reduces the strain on file explorers of having to display over 40,000 images at once.

After downloading the image itself, we need to create an accompanying YAML metadata file to store source URL and all tags used. We'll probably use the format `<image-ID>.yaml`. The format will probably be as follows (escape all double quotes in the tags):

```yaml
image-id: "FCKU54O3VGXCPJMQ5RNSZ7P7ZRQBBL4F"
image-ext: ".jpeg"
image-view: "https://macrochan.org/view.php?u=FCKU54O3VGXCPJMQ5RNSZ7P7ZRQBBL4F"
image-url: "https://macrochan.org/images/F/C/FCKU54O3VGXCPJMQ5RNSZ7P7ZRQBBL4F.jpeg"
tags:
    - "screenshots"
    - "motivational image"
    - "When you see it, you'll shit bricks"
```

## The Tag Cloud

One of Macrochan's most important aspects is it's tagging system. Each image is tagged with a certain topic word, which is then shown in the tag tree, and clickable to find all images with that specific tag.

    https://macrochan.org/tagTree.php

While we will be saving individual image tags one by one, it might be advantageous to have a pregenerated list of all images that fit that tag.

To obtain the tag tree, we should save the HTML page and convert it to Markdown "tag-tree.md" with this kind of structure: (YAML won't work due to it's complicated, and not relationally matched tag cloud)

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

Then, we grab all the tags from every image's YAML file, and make a list of all filenames that fit a certain tag. (we could grab the links from the site, but that requires offsets, takes time, and uses up server bandwidth)
