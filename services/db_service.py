from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base
from constants import DATABASE
import sqlite3
import os
from collections import OrderedDict
import uuid
from sqlalchemy.ext.declarative import DeclarativeMeta

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