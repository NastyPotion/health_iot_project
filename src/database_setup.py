import sqlite3
from pymongo import MongoClient
from neo4j import GraphDatabase
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.config import SQL_CONFIG, MONGO_CONFIG, NEO4J_CONFIG

class DatabaseSetup:
    def __init__(self):
        self.setup_sql()
        self.setup_mongodb()
        self.setup_neo4j()
    
    def setup_sql(self):
        """Initialize SQL database"""
        print("🔧 Setting up SQL database...")
        
        os.makedirs('data', exist_ok=True)
        
        conn = sqlite3.connect(SQL_CONFIG['database'])
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                age INTEGER,
                gender TEXT,
                weight_kg REAL,
                height_cm REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS health_alerts (
                alert_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                alert_type TEXT,
                message TEXT,
                severity TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        ''')
        
        sample_users = [
            (101, 'John Doe', 30, 'Male', 75.5, 178.0),
            (102, 'Jane Smith', 28, 'Female', 62.0, 165.0),
            (103, 'Bob Johnson', 45, 'Male', 88.5, 175.0)
        ]
        
        cursor.executemany('''
            INSERT OR IGNORE INTO users (user_id, name, age, gender, weight_kg, height_cm)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', sample_users)
        
        conn.commit()
        conn.close()
        print("✅ SQL database ready!")
    
    def setup_mongodb(self):
        """Initialize MongoDB"""
        print("🔧 Setting up MongoDB...")
        
        client = MongoClient(MONGO_CONFIG['uri'])
        db = client[MONGO_CONFIG['database']]
        
        try:
            db.create_collection("heart_rate_readings", {
                "timeseries": {
                    "timeField": "timestamp",
                    "metaField": "user_id",
                    "granularity": "seconds"
                }
            })
        except Exception as e:
            print(f"Collection may already exist: {e}")
        
        try:
            db.create_collection("daily_steps", {
                "timeseries": {
                    "timeField": "timestamp",
                    "metaField": "user_id",
                    "granularity": "minutes"
                }
            })
        except Exception as e:
            print(f"Collection may already exist: {e}")
        
        db.heart_rate_readings.create_index([("user_id", 1), ("timestamp", -1)])
        db.daily_steps.create_index([("user_id", 1), ("timestamp", -1)])
        
        client.close()
        print("✅ MongoDB ready!")
    
    def setup_neo4j(self):
        """Initialize Neo4j"""
        print("🔧 Setting up Neo4j...")
        
        driver = GraphDatabase.driver(
            NEO4J_CONFIG['uri'],
            auth=(NEO4J_CONFIG['user'], NEO4J_CONFIG['password'])
        )
        
        with driver.session() as session:
            session.run("CREATE CONSTRAINT user_id IF NOT EXISTS FOR (u:User) REQUIRE u.user_id IS UNIQUE")
            
            sample_users = [
                (101, 'John Doe', 30, 'Male'),
                (102, 'Jane Smith', 28, 'Female'),
                (103, 'Bob Johnson', 45, 'Male')
            ]
            
            for user_id, name, age, gender in sample_users:
                session.run("""
                    MERGE (u:User {user_id: $user_id})
                    SET u.name = $name, u.age = $age, u.gender = $gender
                """, user_id=user_id, name=name, age=age, gender=gender)
        
        driver.close()
        print("✅ Neo4j ready!")

if __name__ == "__main__":
    print(" Starting database setup...\n")
    setup = DatabaseSetup()
    print("\n All databases initialized successfully!")
