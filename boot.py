import machine
import time
import dht
import network
import time
from umqttsimple import MQTTClient
import ubinascii
import micropython
import esp

esp.osdebug(None)
import gc

gc.collect()

ssid = 'SSID'
password = 'PASSWORD'
mqtt_server = 'HOSTNAME'
temp_topic = b'bedroom/esp32/temperature'
humid_topic = b'bedroom/esp32/humidity'

wan = network.WLAN(network.WLAN.IF_STA)
client_id = ubinascii.hexlify(machine.unique_id())
client = MQTTClient(client_id, mqtt_server)
DHT22 = dht.DHT22(machine.Pin(4))


def connect_to_wan():
    wan.active(True)
    while True:
        try:
            wan.connect(ssid, password)
            break
        except OSError:
            print("Failed to connect to WiFi, retrying")
            time.sleep(1)
            continue

    while not wan.isconnected():
        pass

    print('Connection successful')
    print(wan.ifconfig())

def connect_to_mqtt():
    while True:
        try:
            client.connect()
            break
        except OSError:
            print("Failed to connect to MQTT broker...")

def disconnect_from_wan():
    wan.disconnect()
    wan.active(False)

def disconnect_from_mqtt():
    client.disconnect()

def get_temp_and_humidity():
    """ Get 3 good readings from sensor and return the average """
    count = 0
    temperature = 0
    humidity = 0

    while count < 3:
        time.sleep(2)

        try:
            DHT22.measure()
            temp = DHT22.temperature()
            humid = DHT22.humidity()
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

    return round(temperature / 2, 2), round(humidity / 2, 2)

while True:
    temp, humidity = get_temp_and_humidity()
    print("Temperature: {:.2f}°C, Humidity: {:.2f}%".format(temp, humidity))

    connect_to_wan()
    connect_to_mqtt()

    client.publish(temp_topic, str(temp))
    client.publish(humid_topic, str(humidity))

    disconnect_from_mqtt()
    disconnect_from_wan()
    time.sleep(10)
