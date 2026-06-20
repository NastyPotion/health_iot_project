import paho.mqtt.client as mqtt
import json
import time
import random
from datetime import datetime
import sys
import os

# Add the parent directory to the path so we can import config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.config import MQTT_CONFIG

class WearableSimulator:
    def __init__(self, user_id):
        self.user_id = user_id
        self.client = mqtt.Client()
        self.client.connect(MQTT_CONFIG['broker'], MQTT_CONFIG['port'], 60)
        print(f"📱 Simulator {user_id} connected to MQTT broker")
        
    def simulate_heart_rate(self):
        """Simulate heart rate readings"""
        # 10% chance to generate an abnormal heart rate to test alerts
        if random.random() < 0.1:  
            base_hr = random.choice([random.randint(40, 55), random.randint(110, 140)])
        else:
            base_hr = random.randint(65, 95)
        
        return {
            'value': base_hr,
            'hrv': random.randint(30, 60),
            'device_id': f'wearable_{self.user_id}',
            'timestamp': datetime.now().isoformat()
        }
    
    def simulate_steps(self):
        """Simulate step counter"""
        return {
            'steps': random.randint(50, 200),
            'calories': random.randint(20, 80)
        }
    
    def simulate_activity(self):
        """Simulate activity detection"""
        activities = ['Walking', 'Running', 'Cycling', 'Swimming', 'Resting']
        intensities = ['Low', 'Medium', 'High']
        
        return {
            'activity_type': random.choice(activities),
            'duration': random.randint(5, 60),
            'intensity': random.choice(intensities)
        }
    
    def publish_data(self):
        """Publish all sensor data"""
        # Heart rate
        hr_data = self.simulate_heart_rate()
        self.client.publish(
            f'health/{self.user_id}/heart_rate',
            json.dumps(hr_data)
        )
        
        # Steps
        steps_data = self.simulate_steps()
        self.client.publish(
            f'health/{self.user_id}/steps',
            json.dumps(steps_data)
        )
        
        # Activity
        activity_data = self.simulate_activity()
        self.client.publish(
            f'health/{self.user_id}/activity_level',
            json.dumps(activity_data)
        )
        
        print(f"📤 Published data for user {self.user_id}")

def main():
    print("\n🚀 Starting Wearable Simulators...")
    
    # Create simulators for 3 users
    simulators = [WearableSimulator(i) for i in [101, 102, 103]]
    
    try:
        while True:
            for sim in simulators:
                sim.publish_data()
            time.sleep(5)  # Publish every 5 seconds
    except KeyboardInterrupt:
        print("\n Simulation stopped")

if __name__ == "__main__":
    main()