import paho.mqtt.client as mqtt
import json
from datetime import datetime
import sqlite3
from pymongo import MongoClient
from neo4j import GraphDatabase
import sys
import os
import time

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.config import MQTT_CONFIG, SQL_CONFIG, MONGO_CONFIG, NEO4J_CONFIG

class HealthMonitoringSystem:
    def __init__(self):
        print("🔌 Initializing Health Monitoring System...")
        
        # Initialize databases
        self.sql_conn = sqlite3.connect(SQL_CONFIG['database'])
        self.mongo_client = MongoClient(MONGO_CONFIG['uri'])
        self.mongo_db = self.mongo_client[MONGO_CONFIG['database']]
        self.neo4j_driver = GraphDatabase.driver(
            NEO4J_CONFIG['uri'],
            auth=(NEO4J_CONFIG['user'], NEO4J_CONFIG['password'])
        )
        
        # MQTT Client
        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        
        print("✅ System initialized!")
    
    def on_connect(self, client, userdata, flags, rc):
        print(f"\n🔗 Connected to MQTT broker with result code {rc}")
        for topic in MQTT_CONFIG['topics']:
            self.client.subscribe(topic)
            print(f"📡 Subscribed to: {topic}")
    
    def on_message(self, client, userdata, msg):
        try:
            topic_parts = msg.topic.split('/')
            user_id = int(topic_parts[1])
            data_type = topic_parts[2]
            payload = json.loads(msg.payload.decode())
            
            print(f"\n📨 Received: User {user_id} - {data_type}")
            
            # Process based on data type
            if data_type == 'heart_rate':
                self.process_heart_rate(user_id, payload)
            elif data_type == 'steps':
                self.process_steps(user_id, payload)
            elif data_type == 'activity_level':
                self.process_activity(user_id, payload)
                
        except Exception as e:
            print(f"❌ Error processing message: {e}")
    
    def process_heart_rate(self, user_id, data):
        """Process heart rate data"""
        timestamp = datetime.now()
        heart_rate = data.get('value')
        
        # Store in MongoDB
        self.mongo_db.heart_rate_readings.insert_one({
            'timestamp': timestamp,
            'user_id': user_id,
            'heart_rate': heart_rate,
            'hrv': data.get('hrv', 0),
            'device_id': data.get('device_id', 'simulated')
        })
        
        # Store in Neo4j
        with self.neo4j_driver.session() as session:
            session.run("""
                MERGE (u:User {user_id: $user_id})
                SET u.last_heart_rate = $heart_rate,
                    u.last_updated = $timestamp
            """, user_id=user_id, heart_rate=heart_rate, timestamp=str(timestamp))
            
            # Check for abnormal heart rate
            if heart_rate > 100 or heart_rate < 60:
                severity = 'Critical' if (heart_rate > 120 or heart_rate < 50) else 'Warning'
                
                session.run("""
                    MATCH (u:User {user_id: $user_id})
                    CREATE (a:Alert {
                        type: 'Abnormal Heart Rate',
                        severity: $severity,
                        heart_rate: $heart_rate,
                        timestamp: $timestamp
                    })
                    CREATE (u)-[:TRIGGERED_ALERT]->(a)
                """, user_id=user_id, severity=severity, 
                    heart_rate=heart_rate, timestamp=str(timestamp))
                
                # Store alert in SQL
                self.store_alert_sql(user_id, 'Abnormal Heart Rate', 
                                   f'Heart rate: {heart_rate} bpm', severity)
                
                print(f"⚠️  ALERT: User {user_id} - Heart rate {heart_rate} bpm ({severity})")
        
        print(f"✅ Heart rate {heart_rate} bpm stored for user {user_id}")
    
    def process_steps(self, user_id, data):
        """Process steps data"""
        timestamp = datetime.now()
        
        self.mongo_db.daily_steps.insert_one({
            'timestamp': timestamp,
            'user_id': user_id,
            'steps': data.get('steps', 0),
            'calories_burned': data.get('calories', 0)
        })
        
        # Update Neo4j
        with self.neo4j_driver.session() as session:
            session.run("""
                MERGE (u:User {user_id: $user_id})
                SET u.total_steps = coalesce(u.total_steps, 0) + $steps
            """, user_id=user_id, steps=data.get('steps', 0))
        
        print(f"✅ Steps stored for user {user_id}")
    
    def process_activity(self, user_id, data):
        """Process activity level"""
        activity_type = data.get('activity_type')
        duration = data.get('duration')
        intensity = data.get('intensity')
        
        with self.neo4j_driver.session() as session:
            session.run("""
                MATCH (u:User {user_id: $user_id})
                MERGE (a:Activity {type: $activity_type, intensity: $intensity})
                MERGE (u)-[:PERFORMED_ACTIVITY {
                    duration: $duration,
                    timestamp: $timestamp
                }]->(a)
            """, user_id=user_id, activity_type=activity_type, 
                duration=duration, intensity=intensity, timestamp=str(datetime.now()))
        
        print(f"✅ Activity '{activity_type}' stored for user {user_id}")
    
    def store_alert_sql(self, user_id, alert_type, message, severity):
        """Store critical alerts in SQL"""
        cursor = self.sql_conn.cursor()
        cursor.execute("""
            INSERT INTO health_alerts (user_id, alert_type, message, severity)
            VALUES (?, ?, ?, ?)
        """, (user_id, alert_type, message, severity))
        self.sql_conn.commit()
    
    def start(self):
        """Start the MQTT client"""
        print("\n Starting MQTT client...")
        self.client.connect(MQTT_CONFIG['broker'], MQTT_CONFIG['port'], MQTT_CONFIG['keepalive'])
        self.client.loop_forever()
    
    def stop(self):
        """Stop the system"""
        print("\n🛑 Stopping system...")
        self.client.disconnect()
        self.mongo_client.close()
        self.neo4j_driver.close()
        self.sql_conn.close()

if __name__ == "__main__":
    system = HealthMonitoringSystem()
    try:
        system.start()
    except KeyboardInterrupt:
        system.stop()