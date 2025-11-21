import asyncio
import json
import time
import board
import adafruit_dht
import aiomqtt

# ==== KONFIGURASI ====
MQTT_BROKER = "192.168.0.114"
MQTT_PORT = 1883
MQTT_TOPIC = "raspi/log"   # <-- Ubah ke topic baru
DHT_PIN = board.D4
DEVICE_ID = "raspi-dht11-01"

# ==== INISIALISASI SENSOR ====
dhtDevice = adafruit_dht.DHT11(DHT_PIN)

# ==== FUNGSI ASYNC BACA SENSOR ====
async def read_dht():
    """Baca sensor DHT11 di thread terpisah agar tidak blocking"""
    try:
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

# ==== FUNGSI UTAMA ====
async def main():
    try:
        async with aiomqtt.Client(MQTT_BROKER, port=MQTT_PORT) as client:
            print(f"✅ Terhubung ke broker MQTT {MQTT_BROKER}:{MQTT_PORT}")

            while True:
                temperature, humidity = await read_dht()

                if temperature is not None and humidity is not None:
                    # Format payload DeviceLogRaw
                    payload = json.dumps({
                        "type": "DeviceLogRaw",
                        "device_id": DEVICE_ID,
                        "timestamp": int(time.time()),
                        "data": {
                            "temperature": temperature,
                            "humidity": humidity
                        }
                    })
                    
                    await client.publish(MQTT_TOPIC, payload)
                    print(f"📡 Dikirim ke '{MQTT_TOPIC}': {payload}")
                else:
                    print("⚠️ Gagal membaca sensor")

                await asyncio.sleep(5)
    except aiomqtt.MqttError as e:
        print(f"❌ Gagal konek ke broker: {e}")
    finally:
        dhtDevice.exit()

# ==== ENTRY POINT ====
if __name__ == "__main__":
    asyncio.run(main())
