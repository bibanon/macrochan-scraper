import sqlite3

# connect to database and create cursor
conn = sqlite3.connect('macrochan.db')
c = conn.cursor()

# enable foreign key support
c.execute('''PRAGMA foreign_keys = ON''')

# Create table
c.execute('''CREATE TABLE images (
  imageid text PRIMARY KEY,
  imageext text,
  imageurl text,
  imageview text
)''')


# insert just one list
list = ['6EUABP4KV52YOVJDVFBOJ3AIBI5NKCNU', '.jpeg', 'https://macrochan.org/images/6/E/6EUABP4KV52YOVJDVFBOJ3AIBI5NKCNU.jpeg', 'https://macrochan.org/view.php?u=6EUABP4KV52YOVJDVFBOJ3AIBI5NKCNU']
c.execute('INSERT INTO images (imageid, imageext, imageurl, imageview) VALUES (?,?,?,?)', list)

# insert another list
list = ['3324LOI4WONSJVHJO5CI6NVPFPQIDOAN', '.jpeg', 'https://macrochan.org/images/3/3/3324LOI4WONSJVHJO5CI6NVPFPQIDOAN.jpeg', 'https://macrochan.org/view.php?u=3324LOI4WONSJVHJO5CI6NVPFPQIDOAN']
c.execute('INSERT INTO images (imageid, imageext, imageurl, imageview) VALUES (?,?,?,?)', list)

# retrieve data
for row in c.execute('SELECT * FROM images ORDER BY imageid'):
        print(row)

# create tags table
c.execute('''CREATE TABLE tags (
  tagname text PRIMARY KEY
)''')

# insert data into tags table
tags = ['Screenshots', 'Cat', 'Longcat', 'Motivational Poster']
for tag in tags:
  list = [tag]
  c.execute('INSERT INTO tags VALUES (?)', list)

# retrieve data
for row in c.execute('SELECT * FROM tags ORDER BY tagname'):
        print(row)

# create linking table
c.execute('''CREATE TABLE taglink (
  imageid text,
  tagname text,
  FOREIGN KEY(imageid) REFERENCES images(imageid)
  FOREIGN KEY(tagname) REFERENCES tags(tagname)
)''')

# add tags 
for tag in tags:
  list = ['6EUABP4KV52YOVJDVFBOJ3AIBI5NKCNU', tag]
  c.execute('INSERT INTO taglink (imageid, tagname) VALUES (?,?)', list)

# add tags for second image
tags = ['Motivational Poster']
for tag in tags:
  list = ['3324LOI4WONSJVHJO5CI6NVPFPQIDOAN', tag]
  c.execute('INSERT INTO taglink (imageid, tagname) VALUES (?,?)', list)

# attempt to violate foreign key support with bad tag
tags = ['lulz']
for tag in tags:
  list = ['3324LOI4WONSJVHJO5CI6NVPFPQIDOAN', tag]
  c.execute('INSERT INTO taglink (imageid, tagname) VALUES (?,?)', list)

# retrieve data
for row in c.execute('SELECT * FROM taglink ORDER BY tagname'):
        print(row)

print()

# display all data for one image entry
img_id = '6EUABP4KV52YOVJDVFBOJ3AIBI5NKCNU'
list = [img_id]
for row in c.execute('SELECT imageid, tagname FROM taglink WHERE imageid = ? ORDER BY tagname', list):
        print(row)

# Save (commit) the changes
conn.commit()

# We can also close the connection if we are done with it.
# Just be sure any changes have been committed or they will be lost.
conn.close()