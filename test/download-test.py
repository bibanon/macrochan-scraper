import utils

url = "http://macrochan.org/view.php?u=JNTW3GWLMYDGS7NLSLZTHGKGPNA3OHN3"
local_filename = "./view.php.html"
utils.download_file(local_filename, url, clobber=True)