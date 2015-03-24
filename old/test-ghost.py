from ghost import Ghost

url = "http://macrochan.org/view.php?u=SFOKRTC3YTTYBNS4YSMZKBFPQUAAFU7Q"
# save bandwidth by not loading images through ghost
ghost = Ghost(download_images=False)

# open the webpage
page = ghost.open(url)

img_urls = ghost.evaluate("""
						var listRet = [];   // empty list
						// grab all `<a href=>` tags with `tags`
						var links = document.querySelectorAll("a[href*=tags]");
						
						// loop to check every link
						for (var i=0; i<links.length; i++){
							// return href= links
							listRet.push(links[i].href);
						}
						listRet;            // return list
						""")
# Print the links
for l in img_urls[0]:
    print(l)