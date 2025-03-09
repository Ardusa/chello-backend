from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base
from constants import DATABASE
import sqlite3
import os
from collections import OrderedDict
import uuid
from sqlalchemy.ext.declarative import DeclarativeMeta
from datetime import datetime

engine = create_engine(DATABASE.URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def fetch_table_data(table_name):
    """
    This function fetches the table data from SQLite database and formats it as a string.
    The table name is passed in, so you can dynamically query any table.
    """
    conn = sqlite3.connect("chello.db")
    cursor = conn.cursor()
    
    # Query the table data dynamically based on the table name
    cursor.execute(f"SELECT * FROM {table_name}")
    rows = cursor.fetchall()

    # Format the rows into a string
    formatted_data = " | ".join([description[0] for description in cursor.description]) + "\n"
    formatted_data += "-" * 100 + "\n"  # To visually separate headers
    for row in rows:
        formatted_data += " | ".join(str(value) for value in row) + "\n"

    conn.close()
    return formatted_data

def save_table_to_file(table_name, data):
    """
    This function saves the table data to a text file named after the table.
    """
    file_path = os.path.join("tables", f"{table_name}.txt")
    with open(file_path, "w") as file:
        file.write(data)

def custom_serializer(obj):
    print("Custom serializer called")
    obj_type = type(obj)
    print(f"Serializing object of type {obj_type}")
    if isinstance(obj, OrderedDict):
        print(f"Serializing OrderedDict: {obj}")
        return {custom_serializer(k): custom_serializer(v) for k, v in obj.items()}
    if isinstance(obj, uuid.UUID):
        print(f"Serializing UUID: {obj}")
        return str(obj)
    if isinstance(obj.__class__, DeclarativeMeta):
        # SQLAlchemy model instance
        print(f"Serializing SQLAlchemy model: {obj}")
        return {c.name: getattr(obj, c.name) for c in obj.__table__.columns}
    if hasattr(obj, '__dict__'):
        print(f"Serializing object with __dict__: {obj}")
        return obj.__dict__
    print(f"TypeError: Object of type {obj.__class__.__name__} is not JSON serializable")
    raise TypeError(f"Object of type {obj.__class__.__name__} is not JSON serializable")

def convert_uuid_keys_to_str(data):
    if isinstance(data, dict):
        return {str(k) if isinstance(k, uuid.UUID) else k: convert_uuid_keys_to_str(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [convert_uuid_keys_to_str(i) for i in data]
    else:
        return data

def convert_to_json(data):
    try:
        print("Converting to JSON")
        print(f"Data to be serialized: {data}")
        data_with_str_keys = convert_uuid_keys_to_str(data)
        return data_with_str_keys
    except TypeError as e:
        print(f"Serialization error: {e}")
        raise e

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