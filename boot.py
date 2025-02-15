import time

import dht
import esp
import machine
import network
import ubinascii

from umqttsimple import MQTTClient

esp.osdebug(None)
import gc

gc.collect()

WAN_SSID = ''
WAN_PASSWORD = ''
MQTT_SERVER = 'assistant.local'
TEMPERATURE_TOPIC = b'living-room/esp32/temperature'
HUMIDITY_TOPIC = b'living-room/esp32/humidity'
PUBLISH_INTERVAL_MIN = 15

wan = network.WLAN(network.WLAN.IF_STA)
client_id = ubinascii.hexlify(machine.unique_id())
client = MQTTClient(client_id, MQTT_SERVER)
DHT22 = dht.DHT22(machine.Pin(4))

def connect_to_wan(wan) -> None:
    wan.active(True)

    wan.connect(WAN_SSID, WAN_PASSWORD)

    while not wan.isconnected():
        time.sleep(0.1)

    ipv4_addr: tuple = wan.ipconfig('addr4')
    if isinstance(ipv4_addr, tuple):
        print(f"Connected to {WAN_SSID} successfully with IP {ipv4_addr[0]}")
    else:
        print(f"Connected to {WAN_SSID} successfully with unknown IP.")

def connect_to_mqtt(client) -> None:
    while True:
        try:
            client.connect()
            break
        except OSError:
            print("Failed to connect to MQTT broker...")
    print(f"Connected to MQTT broker {MQTT_SERVER}")

def disconnect_from_wan(wan) -> None:
    wan.disconnect()
    wan.active(False)
    print(f"Disconnected from {WAN_SSID}.")

def disconnect_from_mqtt(client) -> None:
    client.disconnect()
    print(f"Disconnected from MQTT broker {MQTT_SERVER}")

def get_temp_and_humidity(sensor: dht.DHT22) -> tuple[float, float]:
    """ Get 3 good readings from sensor and return the average """
    TOTAL_READINGS = 3

    count = 0
    temperature = 0
    humidity = 0

    while count < TOTAL_READINGS:
        time.sleep(2)

        try:
            sensor.measure()
            temp = sensor.temperature()
            humid = sensor.humidity()
        except OSError:
            print("Failed to read sensor, retrying")
            continue

        if not isinstance(temp, (float, int)):
            print("Bad temperature reading, retrying")
            continue

        if not isinstance(humid, (float, int)):
            print("Bad humidity reading, retrying")
            continue

        temperature += temp
        humidity += humid
        count += 1

    return round(temperature / count, 2), round(humidity / count, 2)

while True:
    print("Reading from DHT22 sensor...")
    temp, humidity = get_temp_and_humidity(DHT22)
    print("Temperature: {:.2f}°C, Humidity: {:.2f}%".format(temp, humidity))

    connect_to_wan(wan)
    connect_to_mqtt(client)

    client.publish(TEMPERATURE_TOPIC, str(temp))
    client.publish(HUMIDITY_TOPIC, str(humidity))
    time.sleep(0.1) # Needed to allow topics to publish to MQTT
    disconnect_from_mqtt(client)
    disconnect_from_wan(wan)

    print(f"Sleeping for {PUBLISH_INTERVAL_MIN} min...")
    time.sleep(PUBLISH_INTERVAL_MIN * 60)


