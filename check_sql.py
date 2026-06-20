import sqlite3

print("Connecting to SQL Database...")
conn = sqlite3.connect('data/health_users.db')
cursor = conn.cursor()

print("\n--- Registered Users ---")
cursor.execute("SELECT user_id, name, age FROM users")
for row in cursor.fetchall():
    print(f"ID: {row[0]}, Name: {row[1]}, Age: {row[2]}")

print("\n--- Generated Alerts ---")
cursor.execute("SELECT user_id, alert_type, severity FROM health_alerts")
alerts = cursor.fetchall()
if alerts:
    for row in alerts:
        print(f"User {row[0]}: {row[1]} ({row[2]})")
else:
    print("No alerts generated yet.")

conn.close()