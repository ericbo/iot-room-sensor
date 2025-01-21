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
wan.active(True)
wan.connect(ssid, password)

while not wan.isconnected():
    pass

print('Connection successful')
print(wan.ifconfig())

client_id = ubinascii.hexlify(machine.unique_id())


def connect_and_subscribe():
  global client_id, mqtt_server
  client = MQTTClient(client_id, mqtt_server)
  client.connect()
  print('Connected to %s MQTT broker!' % (mqtt_server))
  return client

def restart_and_reconnect():
  print('Failed to connect to MQTT broker. Reconnecting...')
  time.sleep(10)
  machine.reset()

try:
  client = connect_and_subscribe()
except OSError as e:
  restart_and_reconnect()


# Initialize the DHT22 sensor
DHT22 = dht.DHT22(machine.Pin(4))

# Read data from the sensor every 2 seconds
while True:
    try:
        DHT22.measure()
        temp = DHT22.temperature()  # Gets the temperature in Celsius
        humidity = DHT22.humidity()  # Gets the relative humidity in %

        print("Temperature: {:.2f}°C, Humidity: {:.2f}%".format(temp, humidity))
        client.publish(temp_topic, str(temp))
        client.publish(humid_topic, str(humidity))
    except OSError as e:
        print("Failed to read from DHT22 sensor:", e)

    time.sleep(2)
