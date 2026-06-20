# MQTT Configuration
MQTT_CONFIG = {
    'broker': 'localhost',
    'port': 1883,
    'keepalive': 60,
    'topics': [
        'health/+/heart_rate',
        'health/+/steps',
        'health/+/activity_level'
    ]
}

# SQL Configuration (SQLite)
SQL_CONFIG = {
    'database': 'data/health_users.db'
}

# MongoDB Configuration
MONGO_CONFIG = {
    'uri': 'mongodb://admin:password123@localhost:27017/',
    'database': 'health_timeseries',
    'auth_source': 'admin'
}

# Neo4j Configuration
NEO4J_CONFIG = {
    'uri': 'bolt://localhost:7687',
    'user': 'neo4j',
    'password': 'password123'
}