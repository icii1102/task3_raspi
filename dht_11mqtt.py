import asyncio
import json
import time
import board
import adafruit_dht
from aiomqtt import Client, MqttError


# ==== KONFIGURASI ====
MQTT_BROKER = "192.168.0.115"
MQTT_PORT = 1883
MQTT_TOPIC = "sensor/dht11"
DHT_PIN = board.D4

# ==== INISIALISASI SENSOR ====
dhtDevice = adafruit_dht.DHT11(DHT_PIN)

# ==== FUNGSI ASYNC BACA SENSOR ====
async def read_dht():
    """Baca sensor DHT11 dalam thread terpisah agar tidak blocking"""
    try:
        # Jalankan di thread lain agar tidak blok event loop
        temperature = await asyncio.to_thread(lambda: dhtDevice.temperature)
        humidity = await asyncio.to_thread(lambda: dhtDevice.humidity)
        return temperature, humidity
    except RuntimeError as e:
        print("Error pembacaan sensor:", e.args[0])
        return None, None
    except Exception as e:
        print("Error umum:", e)
        dhtDevice.exit()
        return None, None

# ==== FUNGSI UTAMA ASYNC ====
async def main():
    try:
        async with Client(MQTT_BROKER, port=MQTT_PORT) as client:
            print(f"✅ Terhubung ke broker MQTT {MQTT_BROKER}:{MQTT_PORT}")

            while True:
                temperature, humidity = await read_dht()

                if temperature is not None and humidity is not None:
                    payload = json.dumps({
                        "temperature": temperature,
                        "humidity": humidity
                    })
                    await client.publish(MQTT_TOPIC, payload)
                    print(f"📡 Dikirim: {payload}")
                else:
                    print("⚠️ Data sensor tidak valid")

                await asyncio.sleep(5)  # jeda 5 detik antar kirim
    except MqttError as e:
        print(f"❌ Gagal konek ke broker: {e}")
    finally:
        dhtDevice.exit()

# ==== JALANKAN ====
if __name__ == "__main__":
    asyncio.run(main())
