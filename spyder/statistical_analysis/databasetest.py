import psycopg2

# connect to database
conn = psycopg2.connect(
    host="localhost",
    port=5450,
    database="postgres",
    user="postgres",
    password="postgres"
)

# create cursor
cur = conn.cursor()

# print all tables in database
cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema='public'")
print(cur.fetchall())

# print the column names inthe topics table
cur.execute("SELECT column_name FROM information_schema.columns WHERE table_name='topics'")
print(cur.fetchall())

# print the first 5 entries in the topics table
cur.execute("SELECT * FROM urls LIMIT 5")
print(cur.fetchall())

# delete topics_preprocessed column from topics table
cur.execute("ALTER TABLE topics DROP COLUMN topics_preprocessed")
conn.commit()

# SELECT pg_size_pretty(pg_total_relation_size('topics'));
# SELECT count(*) FROM topics;
# run the above queries in the database to get the size of the table and the number of rows
cur.execute("SELECT count(*) FROM topics WHERE id IS NULL; SELECT count(*) FROM topics WHERE id IN (SELECT id FROM topics GROUP BY id HAVING count(*) > 1);")
print(cur.fetchall())

# # print random 20 entries from the topics table
# cur.execute("SELECT * FROM topics ORDER BY RANDOM() LIMIT 20")
# print(cur.fetchall())

# close cursor
cur.close()

# close connection
conn.close()