import mysql.connector

def connect():
    """Function to connect to MySQL database."""
    connection = mysql.connector.connect(
        host="localhost",
        user="",      
        password="",  
        database="language_dataset"   
    )
    return connection
