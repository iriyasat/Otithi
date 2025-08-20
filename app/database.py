import mysql.connector
from mysql.connector import Error
from config import Config
import logging
import time
import threading

class Database:
    def __init__(self):
        self.connection = None
        self._lock = threading.Lock()
        self.connect()
    
    def connect(self):
        """Create database connection with better error handling"""
        with self._lock:
            try:
                if self.connection and self.connection.is_connected():
                    self.connection.close()
                    
                self.connection = mysql.connector.connect(
                    host=Config.MYSQL_HOST,
                    port=Config.MYSQL_PORT,
                    user=Config.MYSQL_USER,
                    password=Config.MYSQL_PASSWORD,
                    database=Config.MYSQL_DATABASE,
                    autocommit=True,
                    connection_timeout=60,
                    charset='utf8mb4',
                    collation='utf8mb4_unicode_ci',
                    use_unicode=True,
                    get_warnings=True,
                    raise_on_warnings=False
                )
                if self.connection.is_connected():
                    print(f"Successfully connected to MySQL database '{Config.MYSQL_DATABASE}'")
            except Error as e:
                print(f"Error connecting to MySQL: {e}")
                self.connection = None
                # Try to create database if it doesn't exist
                self.create_database()
    
    def is_connection_healthy(self):
        """Check if connection is healthy and can execute queries"""
        try:
            if not self.connection:
                return False
            if not self.connection.is_connected():
                return False
            # Test with a simple query
            cursor = self.connection.cursor()
            cursor.execute("SELECT 1")
            cursor.fetchone()
            cursor.close()
            return True
        except Exception as e:
            print(f"Connection health check failed: {e}")
            # Force connection reset on any error
            self.connection = None
            return False
    
    def reset_connection(self):
        """Force reset the database connection"""
        try:
            if self.connection and self.connection.is_connected():
                self.connection.close()
        except Exception:
            pass
        self.connection = None
        print("Database connection reset")
    
    def ensure_connection(self):
        """Ensure we have a healthy connection, reconnect if needed"""
        if not self.is_connection_healthy():
            print("Database connection unhealthy, reconnecting...")
            self.reset_connection()
            self.connect()
            # Wait a bit for connection to stabilize
            time.sleep(0.2)
            return self.is_connection_healthy()
        return True
    
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
        """Execute a SELECT query with improved connection handling"""
        max_retries = 3
        for attempt in range(max_retries):
            try:
                if not self.ensure_connection():
                    if attempt < max_retries - 1:
                        print(f"Connection failed, retrying... (attempt {attempt + 1})")
                        time.sleep(0.5)
                        continue
                    else:
                        print("Max retries reached, returning empty result")
                        return []
                
                if not self.connection or not self.connection.is_connected():
                    print("Connection still not available after ensure_connection")
                    return []
                
                cursor = self.connection.cursor(dictionary=True)
                cursor.execute(query, params or ())
                result = cursor.fetchall()
                cursor.close()
                return result
                
            except (Error, IndexError, Exception) as e:
                print(f"Error executing query (attempt {attempt + 1}): {e}")
                self.reset_connection()
                
                if attempt < max_retries - 1:
                    print("Retrying with new connection...")
                    time.sleep(0.5)
                    continue
                else:
                    print("Max retries reached, returning empty result")
                    return []
        
        return []
    
    def execute_insert(self, query, params=None):
        """Execute an INSERT query with improved connection handling"""
        max_retries = 3
        for attempt in range(max_retries):
            try:
                if not self.ensure_connection():
                    if attempt < max_retries - 1:
                        print(f"Connection failed, retrying... (attempt {attempt + 1})")
                        time.sleep(0.5)
                        continue
                    else:
                        print("Max retries reached, returning None")
                        return None
                
                if not self.connection or not self.connection.is_connected():
                    print("Connection still not available after ensure_connection")
                    return None
                
                cursor = self.connection.cursor(dictionary=True)
                cursor.execute(query, params or ())
                last_id = cursor.lastrowid
                cursor.close()
                return last_id
                
            except (Error, IndexError, Exception) as e:
                print(f"Error executing insert (attempt {attempt + 1}): {e}")
                self.reset_connection()
                
                if attempt < max_retries - 1:
                    print("Retrying with new connection...")
                    time.sleep(0.5)
                    continue
                else:
                    print("Max retries reached, returning None")
                    return None
        
        return None
    
    def execute_update(self, query, params=None):
        """Execute an UPDATE/DELETE query with improved connection handling"""
        max_retries = 3
        for attempt in range(max_retries):
            try:
                if not self.ensure_connection():
                    if attempt < max_retries - 1:
                        print(f"Connection failed, retrying... (attempt {attempt + 1})")
                        time.sleep(0.5)
                        continue
                    else:
                        print("Max retries reached, returning 0")
                        return 0
                
                if not self.connection or not self.connection.is_connected():
                    print("Connection still not available after ensure_connection")
                    return 0
                
                cursor = self.connection.cursor(dictionary=True)
                cursor.execute(query, params or ())
                affected_rows = cursor.rowcount
                cursor.close()
                return affected_rows
                
            except (Error, IndexError, Exception) as e:
                print(f"Error executing update (attempt {attempt + 1}): {e}")
                self.reset_connection()
                
                if attempt < max_retries - 1:
                    print("Retrying with new connection...")
                    time.sleep(0.5)
                    continue
                else:
                    print("Max retries reached, returning 0")
                    return 0
        
        return 0
    
    def maintain_connection(self):
        """Periodically check and maintain connection health"""
        try:
            if self.connection and self.connection.is_connected():
                # Execute a simple query to keep connection alive
                cursor = self.connection.cursor()
                cursor.execute("SELECT 1")
                cursor.fetchone()
                cursor.close()
                return True
            else:
                print("Connection lost, reconnecting...")
                self.connect()
                return self.connection and self.connection.is_connected()
        except Exception as e:
            print(f"Connection maintenance failed: {e}")
            self.reset_connection()
            self.connect()
            return self.connection and self.connection.is_connected()
    
    def get_connection_info(self):
        """Get current connection status information"""
        if not self.connection:
            return "No connection"
        if not self.connection.is_connected():
            return "Disconnected"
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT VERSION()")
            version = cursor.fetchone()
            cursor.close()
            return f"Connected - MySQL {version[0] if version else 'Unknown'}"
        except Exception:
            return "Connected but unhealthy"
    
    def close(self):
        """Close database connection"""
        with self._lock:
            if self.connection and self.connection.is_connected():
                self.connection.close()
                print("MySQL connection closed")

# Global database instance
db = Database()
