from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base
from constants import DATABASE
import sqlite3
import os

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
