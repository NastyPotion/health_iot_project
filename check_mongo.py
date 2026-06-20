from pymongo import MongoClient

print("Connecting to MongoDB...")
client = MongoClient('mongodb://admin:password123@localhost:27017/', authSource='admin')
db = client['health_timeseries']

print("\n--- Recent Heart Rate Readings ---")
for doc in db.heart_rate_readings.find().limit(5):
    print(f"User {doc['user_id']}: {doc['heart_rate']} bpm at {doc['timestamp']}")

print("\n--- Recent Steps Records ---")
for doc in db.daily_steps.find().limit(5):
    print(f"User {doc['user_id']}: {doc['steps']} steps")

client.close()
print("\nDone!")
