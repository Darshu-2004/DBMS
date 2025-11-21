"""
Database connection and utility functions
Handles MySQL connection pooling and query execution
"""

import mysql.connector
from mysql.connector import Error, pooling
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database configuration
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', 'Darshu@2004'),
    'database': os.getenv('DB_NAME', 'transport_system'),
    'pool_name': 'transport_pool',
    'pool_size': 5,
    'pool_reset_session': True
}

# Create connection pool
try:
    connection_pool = pooling.MySQLConnectionPool(**DB_CONFIG)
    print("[OK] Database connection pool created successfully")
except Error as e:
    print(f"✗ Error creating connection pool: {e}")
    connection_pool = None


def get_db_connection():
    """Get a connection from the pool"""
    try:
        if connection_pool:
            return connection_pool.get_connection()
        else:
            return mysql.connector.connect(
                host=DB_CONFIG['host'],
                user=DB_CONFIG['user'],
                password=DB_CONFIG['password'],
                database=DB_CONFIG['database']
            )
    except Error as e:
        print(f"✗ Error getting database connection: {e}")
        return None


def execute_sql_file(filename):
    """Execute SQL file for database setup"""
    try:
        conn = mysql.connector.connect(
            host=DB_CONFIG['host'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password'],
            autocommit=True
        )
        cursor = conn.cursor()
        
        with open(filename, 'r', encoding='utf-8') as file:
            sql_content = file.read()
            
        # Split by semicolon and execute each statement
        statements = sql_content.split(';')
        for statement in statements:
            statement = statement.strip()
            if statement and not statement.startswith('--'):
                try:
                    cursor.execute(statement)
                    # Consume any results
                    try:
                        cursor.fetchall()
                    except:
                        pass
                except Error as e:
                    if 'SELECT' in statement.upper():
                        # Skip SELECT statements used for status messages
                        pass
                    else:
                        print(f"Warning in {filename}: {e}")
        
        cursor.close()
        conn.close()
        print(f"✓ Executed: {filename}")
        return True
    except Error as e:
        print(f"✗ Error executing {filename}: {e}")
        return False


def execute_query(query, params=None, fetch=False):
    """Execute a SQL query with optional parameters"""
    conn = get_db_connection()
    if not conn:
        return None
    
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(query, params or ())
        
        if fetch:
            result = cursor.fetchall()
        else:
            conn.commit()
            result = cursor.lastrowid or cursor.rowcount
        
        cursor.close()
        conn.close()
        return result
    except Error as e:
        print(f"✗ Database error: {e}")
        if conn:
            conn.close()
        return None


def execute_query_one(query, params=None):
    """Execute a SQL query and return one result"""
    conn = get_db_connection()
    if not conn:
        return None
    
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(query, params or ())
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        return result
    except Error as e:
        print(f"✗ Database error: {e}")
        if conn:
            conn.close()
        return None


def test_connection():
    """Test database connection"""
    conn = get_db_connection()
    if conn and conn.is_connected():
        print("[OK] Database connection successful")
        conn.close()
        return True
    else:
        print("✗ Database connection failed")
        return False


if __name__ == "__main__":
    test_connection()
