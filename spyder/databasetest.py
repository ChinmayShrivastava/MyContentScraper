import psycopg2

# connect to database
conn = psycopg2.connect(
    host="localhost",
    port=5450,
    database="postgres",
    user="postgres",
    password="postgres"
)

# print all columns and first row of all tables in database
# cur.execute("SELECT * FROM urls")
# print(cur.fetchall())
# cur.execute("SELECT * FROM resources")
# print(cur.fetchall())