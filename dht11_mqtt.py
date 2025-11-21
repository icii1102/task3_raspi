import time
import board
import adafruit_dht
import paho.mqtt.client as mqtt
import json

# ==== KONFIGURASI ====
MQTT_BROKER = "192.168.0.115"   # Ganti dengan IP laptop tempat broker MQTT berjalan
MQTT_PORT = 1883
MQTT_TOPIC = "sensor/dht11"
DHT_PIN = board.D4               # GPIO4 pada Raspberry Pi (pin data DHT11)

# ==== INISIALISASI ====
dhtDevice = adafruit_dht.DHT11(DHT_PIN)
client = mqtt.Client("RaspberryPi-DHT11")

# ==== KONEKSI KE BROKER ====
try:
    client.connect(MQTT_BROKER, MQTT_PORT, 60)
    print("Terhubung ke broker MQTT:", MQTT_BROKER)
except Exception as e:
    print("Gagal terhubung ke broker:", e)
    exit()

# ==== LOOP KIRIM DATA ====
while True:
    try:
        temperature = dhtDevice.temperature
        humidity = dhtDevice.humidity

        if temperature is not None and humidity is not None:
            payload = {
                "temperature": temperature,
                "humidity": humidity
            }
            client.publish(MQTT_TOPIC, json.dumps(payload))
            print(f"Dikirim: {payload}")
        else:
            print("Gagal membaca sensor")

    except RuntimeError as error:
        print("Error pembacaan sensor:", error.args[0])

    except Exception as e:
        dhtDevice.exit()
        print("Error umum:", e)
        break

    time.sleep(5)  # kirim tiap 5 detik
