# import mysql.connector
#
# mydb = mysql.connector.connect(
#     host="localhost",
#     user="root",
#     passwd="rootpass"
# )
#
# my_cursor = mydb.cursor()
#
# my_cursor.execute("CREATE DATABASE our_users")

import pymysql

# Establish the connection
mydb = pymysql.connect(
    host="localhost",
    user="root",
    passwd="rootpass"
)

# Create a cursor object
my_cursor = mydb.cursor()

# Execute a SQL command
# my_cursor.execute("CREATE DATABASE test")

# Close the connection
my_cursor.close()
mydb.close()

