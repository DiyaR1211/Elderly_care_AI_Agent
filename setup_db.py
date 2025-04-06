import sqlite3
import pandas as pd

# Load the CSV data into pandas DataFrames
caretakers_df = pd.read_csv('C:\\Users\\diyar\\OneDrive\\Desktop\\caregiver.csv')  # CSV for caretakers
elderly_df = pd.read_csv('C:\\Users\\diyar\\OneDrive\\Desktop\\elderly.csv')        # CSV for elderly

# Connect to SQLite database (it will be created if it doesn't exist)
conn = sqlite3.connect('care_system.db')
c = conn.cursor()

# Create table for elderly if it doesn't exist
c.execute('''
    CREATE TABLE IF NOT EXISTS elderly (
        device_id TEXT PRIMARY KEY, 
        name TEXT, 
        password TEXT
    )
''')

# Create table for caretakers if it doesn't exist
c.execute('''
    CREATE TABLE IF NOT EXISTS caretakers (
        username TEXT PRIMARY KEY, 
        password TEXT
    )
''')

# Insert caretaker data from CSV into the database
for index, row in caretakers_df.iterrows():
    c.execute("INSERT OR IGNORE INTO caretakers (username, password) VALUES (?, ?)",
              (row['username'], row['password']))

# Insert elderly data from CSV into the database
for index, row in elderly_df.iterrows():
    c.execute("INSERT OR IGNORE INTO elderly (device_id, name, password) VALUES (?, ?, ?)",
              (row['device_id'], row['name'], row['password']))

# Commit the changes and close the connection
conn.commit()
conn.close()

print("Database setup complete with data from CSV files.")
