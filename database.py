import pymysql

#===============connect backend(mysql) from frontend(python) 
def initialize_connection():
    try:
        conn = pymysql.connect(
            host="mysql-131b4494-sudhanshushekhar692004-ogi.b.aivencloud.com",
            user="avnadmin",
            password="AVNS_e7RWYi6DTJzwyJiyHLZ",
            database="sudhanshu",
            port=23815,
            connect_timeout=1000
        )
        cursor = conn.cursor()
        create_database(cursor)
        create_table(cursor)
        return conn, cursor
    except pymysql.MySQLError as e:
        print(f"Error: {e}")
        return None, None

#==============create database(sudhanshu), when database not created==========
def create_database(cursor):
    cursor.execute("SHOW DATABASES")
    temp = cursor.fetchall()
    databases = [item[0] for item in temp]
    
    if "sudhanshu" not in databases:
        cursor.execute("CREATE DATABASE sudhanshu")
    cursor.execute("USE sudhanshu")

#=================create table for user, when table(users not created)===================
def create_table(cursor):  
    cursor.execute("SHOW TABLES")
    temp = cursor.fetchall()
    tables = [item[0] for item in temp]
    
    if "users" not in tables:
        cursor.execute("""CREATE TABLE users(
            id INT AUTO_INCREMENT PRIMARY KEY,
            firstName VARCHAR(100),
            lastName VARCHAR(100),
            password VARCHAR(30),
            email VARCHAR(100) UNIQUE,
            gender VARCHAR(1),
            age INT,
            state VARCHAR(25)
        )""")

#=============fetch and login user from this command================ 
def login(cursor, data):
    cursor.execute("SELECT * FROM users WHERE email = %s AND password = %s", (data["email"], data["password"]))
    if cursor.fetchone() is not None:
        return True
    return False

#==========insert from this command of user=======================
def register(cursor, conn, data):
    print(data)

    # Check if user with the same email already exists
    cursor.execute("SELECT * FROM users WHERE email = %s", (data["email"],))
    if cursor.fetchone() is not None:
        print("User already exists with this email!")
        return False

    cursor.execute("""INSERT INTO users(firstName, lastName, password, email, gender, age, state) 
                      VALUES (%s, %s, %s, %s, %s, %s, %s)""", 
                   (data["firstName"], data["lastName"], data["password"], data["email"], data["gender"], data["age"], data["state"]))
    conn.commit()
    return True

# # Test the connection and register
# conn, cursor = initialize_connection()
# if conn and cursor:
#     data = {
#         "firstName": "John",
#         "lastName": "Doe",
#         "password": "Password123",
#         "email": "john.doe@example.com",
#         "gender": "M",
#         "age": 30,
#         "state": "California"
#     }
#     if register(cursor, conn, data):
#         print("User registered successfully!")
# initialize_connection()