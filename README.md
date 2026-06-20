Health & Wellness IoT Monitoring System

Project Description
This project is an integrated IoT system capable of collecting, processing, and storing large volumes of health data from simulated wearable devices. It uses the MQTT protocol for real-time data transmission and **Python** for data processing. 

The system demonstrates a multi-database architecture, routing data to the most appropriate storage engine based on its characteristics:
- SQL (SQLite): Structured data (User profiles, critical alerts).
- MongoDB: High-volume time-series data (Heart rate readings, daily steps).
- Neo4j: Relationship-based data (User-Activity connections, Alert graphs).

System Architecture
[Wearable Simulator] --(MQTT)--> [Mosquitto Broker] --(Python Client)--> [SQL / MongoDB / Neo4j]
