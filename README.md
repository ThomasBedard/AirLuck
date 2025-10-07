# 🌤️ AirLuck — IoT Weather Monitoring System

**AirLuck** is a fully functional **IoT weather station using Raspberry PI** built with **Python** and a physical **temperature & humidity sensor**.  
It reads live environmental data from connected hardware (such as a DHT22 or BME280 sensor), logs it locally, and serves the results through a simple web interface.

> Originally developed as a hands-on IoT project to measure real-time weather data and explore sensor integration with Python.

---

## 🧠 Overview

AirLuck combines **hardware sensors**, **Python-based data processing**, and an optional **Flask web dashboard** into a single system that:

- Collects temperature, humidity, and air pressure data in real-time  
- Logs data to `sensor_data.txt` for analysis and persistence  
- Optionally displays readings on a local Flask web page  
- Can be extended to send data to remote APIs or databases  

---

## 🛠️ **Hardware Requirements**

| Component | Description |
|------------|-------------|
| **Raspberry Pi / Arduino** | Main controller (runs Python code) |
| **DHT22 or BME280 Sensor** | Measures temperature, humidity, and optionally pressure |
| **Jumper wires** | Connect sensor to GPIO pins |



## 🧩 **Software Requirements**

- **Python 3.10+**
- Libraries:
  - `Adafruit_DHT` (for DHT11/DHT22 sensors)
  - `Flask` (optional, for web UI)
  - `datetime`, `time`, `csv`
  - (Optional) `matplotlib` for graphing historical data

Install dependencies:
```bash
pip install Adafruit_DHT Flask matplotlib

## ⚙️ **Project Structure**
AirLuck/
├── instance/             # Config or runtime files
├── templates/            # HTML templates for Flask dashboard
├── static/               # Optional CSS/JS for the dashboard
├── main.py               # Main program that reads from the sensor
├── sensor_data.txt       # Local log file storing readings
├── requirements.txt      # Python dependencies
└── README.md             # Project documentation

🚀 How It Works

1. Read data from the sensor every few seconds via GPIO pins.

2. Timestamp the data and log it into sensor_data.txt.

3. (Optional) Serve the latest readings on a simple Flask dashboard at http://localhost:5000/.

4. Persist and visualize results over time (e.g., using matplotlib
