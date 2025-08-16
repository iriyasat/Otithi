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
    
    def ensure_connection(self):
        """Ensure database connection is active, reconnect if needed"""
        try:
            if not self.connection or not self.connection.is_connected():
                print("Database connection lost, reconnecting...")
                self.connect()
        except Error as e:
            print(f"Error checking connection: {e}")
            self.connect()

    def execute_query(self, query, params=None):
        """Execute a SELECT query"""
        try:
            self.ensure_connection()
            if not self.connection:
                print("Error executing query: MySQL Connection not available")
                return []
                
            cursor = self.connection.cursor(dictionary=True)  # Always use dictionary cursor
            cursor.execute(query, params or ())
            result = cursor.fetchall()
            cursor.close()
            return result
        except Error as e:
            print(f"Error executing query: {e}")
            # Try to reconnect and retry once
            try:
                self.connect()
                if self.connection:
                    cursor = self.connection.cursor(dictionary=True)
                    cursor.execute(query, params or ())
                    result = cursor.fetchall()
                    cursor.close()
                    return result
            except:
                pass
            return []
    
    def execute_insert(self, query, params=None):
        """Execute an INSERT query and return the last inserted ID"""
        try:
            self.ensure_connection()
            if not self.connection:
                print("Error executing insert: MySQL Connection not available")
                return None
                
            cursor = self.connection.cursor(dictionary=True)  # Use dictionary cursor
            cursor.execute(query, params or ())
            last_id = cursor.lastrowid
            cursor.close()
            return last_id
        except Error as e:
            print(f"Error executing insert: {e}")
            # Try to reconnect and retry once
            try:
                self.connect()
                if self.connection:
                    cursor = self.connection.cursor(dictionary=True)
                    cursor.execute(query, params or ())
                    last_id = cursor.lastrowid
                    cursor.close()
                    return last_id
            except:
                pass
            return None
    
    def execute_update(self, query, params=None):
        """Execute an UPDATE/DELETE query"""
        try:
            self.ensure_connection()
            if not self.connection:
                print("Error executing update: MySQL Connection not available")
                return 0
                
            cursor = self.connection.cursor(dictionary=True)  # Use dictionary cursor
            cursor.execute(query, params or ())
            affected_rows = cursor.rowcount
            cursor.close()
            return affected_rows
        except Error as e:
            print(f"Error executing update: {e}")
            # Try to reconnect and retry once
            try:
                self.connect()
                if self.connection:
                    cursor = self.connection.cursor(dictionary=True)
                    cursor.execute(query, params or ())
                    affected_rows = cursor.rowcount
                    cursor.close()
                    return affected_rows
            except:
                pass
            return 0
    
    def close(self):
        """Close database connection"""
        if self.connection and self.connection.is_connected():
            self.connection.close()
            print("MySQL connection closed")

# Global database instance
db = Database()

def get_db_connection():
    """Get database connection for compatibility with messages.py"""
    return db.connection
