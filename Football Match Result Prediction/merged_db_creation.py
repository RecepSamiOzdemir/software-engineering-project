import sqlite3
import pandas as pd
import os

# CSV dosyasının bulunduğu dizini al
script_dir = os.path.dirname(os.path.abspath(__file__))

# CSV dosyasının yolunu oluştur
file_path = os.path.join(script_dir, "merged_data.csv")

# CSV dosyasını pandas ile oku
data = pd.read_csv(file_path)

# Sütun adlarındaki boşlukları "_" ile değiştir
data.columns = data.columns.str.replace(' ', '_')

# SQLite veritabanına bağlan (yoksa oluşturur)
db_file = "merged.db"
conn = sqlite3.connect(db_file)
cursor = conn.cursor()

# FOOTBALL tablosunu oluştur (id sütunu ve PRIMARY KEY olmadan)
create_football_table_query = """
CREATE TABLE IF NOT EXISTS FOOTBALL (
    League TEXT,
    Date TEXT,
    Home_Team TEXT,
    Away_Team TEXT,
    Home_Score INTEGER,
    Away_Score INTEGER
)
"""
cursor.execute(create_football_table_query)

# FOOTBALL tablosuna verileri ekle
data.to_sql('FOOTBALL', conn, if_exists='append', index=False)

# Users tablosunu oluştur
create_users_table_query = """
CREATE TABLE IF NOT EXISTS Users (
    username TEXT UNIQUE,
    password TEXT
)
"""
cursor.execute(create_users_table_query)

# Varsayılan kullanıcıları Users tablosuna ekle
insert_users_query = """
INSERT OR IGNORE INTO Users (username, password) VALUES (?, ?)
"""
default_users = [
    ("admin", "123"),
    ("Gulsum", "123"),
    ("Zeynep", "123")
]

cursor.executemany(insert_users_query, default_users)

# İşlemleri tamamla ve bağlantıyı kapat
conn.commit()
conn.close()

print("Data and Users table created successfully!")
