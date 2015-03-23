import sqlite3

# connect to database and create cursor
conn = sqlite3.connect('images.db')
c = conn.cursor()

# Create table
c.execute('''CREATE TABLE images
             (imageid text primary key not null, image-ext text, image-url text, image-view text, price real)''')

# Insert a row of data
c.execute("INSERT INTO images VALUES ('2006-01-05','BUY','RHAT',100,35.14)")

# Larger example
for t in [('2006-03-28', 'BUY', 'IBM', 1000, 45.00),
          ('2006-04-05', 'BUY', 'MSOFT', 1000, 72.00),
          ('2006-04-06', 'SELL', 'IBM', 500, 53.00),
         ]:
    c.execute('INSERT INTO images VALUES (?,?,?,?,?)', t)

# insert just one list
list = ['6EUABP4KV52YOVJDVFBOJ3AIBI5NKCNU', '.jpeg', 'https://macrochan.org/images/6/E/6EUABP4KV52YOVJDVFBOJ3AIBI5NKCNU.jpeg', 'https://macrochan.org/view.php?u=6EUABP4KV52YOVJDVFBOJ3AIBI5NKCNU', 50.00]
c.execute('INSERT INTO images VALUES (?,?,?,?,?)', list)

# retrieve data
for row in c.execute('SELECT * FROM images ORDER BY price'):
        print(row)

# Save (commit) the changes
conn.commit()

# We can also close the connection if we are done with it.
# Just be sure any changes have been committed or they will be lost.
conn.close()