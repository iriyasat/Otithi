import mysql.connector
from mysql.connector import Error
from config import Config
import logging

class Database:
    def __init__(self):
        self.connection = None
        self.connect()
    
    def connect(self):
        """Create database connection"""
        try:
            self.connection = mysql.connector.connect(
                host=Config.MYSQL_HOST,
                port=Config.MYSQL_PORT,
                user=Config.MYSQL_USER,
                password=Config.MYSQL_PASSWORD,
                database=Config.MYSQL_DATABASE,
                autocommit=True
            )
            if self.connection.is_connected():
                print(f"Successfully connected to MySQL database '{Config.MYSQL_DATABASE}'")
        except Error as e:
            print(f"Error connecting to MySQL: {e}")
            # Try to create database if it doesn't exist
            self.create_database()
    
    def create_database(self):
        """Create database if it doesn't exist"""
        try:
            temp_connection = mysql.connector.connect(
                host=Config.MYSQL_HOST,
                port=Config.MYSQL_PORT,
                user=Config.MYSQL_USER,
                password=Config.MYSQL_PASSWORD,
                autocommit=True
            )
            
            cursor = temp_connection.cursor()
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {Config.MYSQL_DATABASE}")
            cursor.close()
            temp_connection.close()
            
            print(f"Database '{Config.MYSQL_DATABASE}' created successfully")
            
            # Now connect to the newly created database
            self.connect()
            
            # Initialize database schema
            self.initialize_schema()
            
        except Error as e:
            print(f"Error creating database: {e}")
    
    def initialize_schema(self):
        """Initialize database schema from SQL file"""
        try:
            with open('database/otithi_schema.sql', 'r') as sql_file:
                sql_commands = sql_file.read().split(';')
                
                cursor = self.connection.cursor()
                for command in sql_commands:
                    command = command.strip()
                    if command:
                        cursor.execute(command)
                cursor.close()
                
                print("Database schema initialized successfully")
                
        except FileNotFoundError:
            print("Schema file not found. Please create database/otithi_schema.sql")
        except Error as e:
            print(f"Error initializing schema: {e}")
    
    def execute_query(self, query, params=None):
        """Execute a SELECT query"""
        try:
            cursor = self.connection.cursor(dictionary=True)
            cursor.execute(query, params or ())
            result = cursor.fetchall()
            cursor.close()
            return result
        except Error as e:
            print(f"Error executing query: {e}")
            return []
    
    def execute_insert(self, query, params=None):
        """Execute an INSERT query and return the last inserted ID"""
        try:
            cursor = self.connection.cursor()
            cursor.execute(query, params or ())
            last_id = cursor.lastrowid
            cursor.close()
            return last_id
        except Error as e:
            print(f"Error executing insert: {e}")
            return None
    
    def execute_update(self, query, params=None):
        """Execute an UPDATE/DELETE query"""
        try:
            cursor = self.connection.cursor()
            cursor.execute(query, params or ())
            affected_rows = cursor.rowcount
            cursor.close()
            return affected_rows
        except Error as e:
            print(f"Error executing update: {e}")
            return 0
    
    def close(self):
        """Close database connection"""
        if self.connection and self.connection.is_connected():
            self.connection.close()
            print("MySQL connection closed")

# Global database instance
db = Database()
