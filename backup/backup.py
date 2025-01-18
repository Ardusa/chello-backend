import sqlite3
import os
from datetime import datetime

def backup_sqlite_with_api(db_file_path: str, backup_dir: str):
    """
    Backs up an SQLite database using SQLite's built-in backup API for consistency.
    
    Args:
        db_file_path (str): Path to the SQLite database file.
        backup_dir (str): Directory where the backup will be stored.
    """
    if not os.path.exists(db_file_path):
        print(f"Error: Database file {db_file_path} does not exist.")
        return
    
    # Ensure backup directory exists
    os.makedirs(backup_dir, exist_ok=True)
    
    # Create a timestamp for the backup filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = os.path.join(backup_dir, f"sqlite_backup_{timestamp}.db")
    
    try:
        # Connect to the source SQLite database
        conn = sqlite3.connect(db_file_path)
        # Connect to the backup database
        backup_conn = sqlite3.connect(backup_file)
        
        # Perform the backup operation
        with backup_conn:
            conn.backup(backup_conn)
        
        print(f"Backup successful: {backup_file}")
    except sqlite3.Error as e:
        print(f"Error occurred during backup: {e}")
    finally:
        conn.close()
        backup_conn.close()

# Example usage:
# backup_sqlite_with_api('/path/to/database.db', '/path/to/backup/directory')