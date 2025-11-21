"""
Database Setup Script
Executes all SQL files in correct order to create the database schema
"""

import os
import glob
from database import execute_sql_file

def setup_database():
    """Execute all SQL files in the database folder in order"""
    print("\n" + "="*60)
    print("  TRANSPORT SYSTEM DATABASE SETUP")
    print("="*60 + "\n")
    
    # Get the database folder path
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    db_folder = os.path.join(base_dir, 'database')
    
    if not os.path.exists(db_folder):
        print(f"✗ Database folder not found: {db_folder}")
        return False
    
    # Get all SQL files and sort them
    sql_files = sorted(glob.glob(os.path.join(db_folder, '*.sql')))
    
    if not sql_files:
        print(f"✗ No SQL files found in {db_folder}")
        return False
    
    print(f"Found {len(sql_files)} SQL files to execute:\n")
    
    success_count = 0
    failed_count = 0
    
    # Execute each SQL file
    for sql_file in sql_files:
        filename = os.path.basename(sql_file)
        print(f"Executing: {filename}")
        
        if execute_sql_file(sql_file):
            success_count += 1
        else:
            failed_count += 1
    
    print("\n" + "="*60)
    print(f"Database Setup Complete!")
    print(f"✓ Successful: {success_count} files")
    if failed_count > 0:
        print(f"✗ Failed: {failed_count} files")
    print("="*60 + "\n")
    
    return failed_count == 0


if __name__ == "__main__":
    setup_database()
