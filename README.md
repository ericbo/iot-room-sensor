# Flashing
This is assumming you are flashing a `ESP32-wroom-32` with a `dht22` sensor plugged into `GPIO04`. 
You will have to make modifications of `boot.py` to connect to a wifi router.  Assuming your ESP32 is the 
only USB serial device connected, your port name should be `/dev/ttyUSB0`.

```
# Create a Virtual Environment if You're Cool 
virtualenv -p python venv
source venv/bin/activate

pip install -r requirements.txt
esptool.py -p <PORT> flash_id
```
*Note:* Replace `<PORT>` with you serial port. List of serial connects can be listed with `ls /dev/ttyUSB*`

# Flash MicroPython
You should visit [MicroPython's Offical ESP32 Page](https://micropython.org/download/ESP32_GENERIC/) to download the latest image.

```
esptool.py erase_flash

wget https://micropython.org/resources/firmware/ESP32_GENERIC-20241129-v1.24.1.bin

esptool.py --baud 460800 write_flash 0x1000 ESP32_GENERIC-20241129-v1.24.1.bin
```

# Upload Firmware
Using a tool like thonny, upload the `boot.py` and `umqttsimple.py`. You can find the original repo/source for
umqttsimple on [GitHub](https://raw.githubusercontent.com/RuiSantosdotme/ESP-MicroPython/master/code/MQTT/umqttsimple.py).

you can install thonny on debian based distra via the following command:
```
sudo apt update && sudo apt install thonny -y
```

# Erasing the Flash
```
esptool.py erase_flash
```

