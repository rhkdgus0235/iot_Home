import adafruit_dht
import board

dhtdevice=adafruit_dht.DHT11(board.D12)


while True:
    temperature_c = dhtdevice.temperature
    temperature_f = temperature_c * (9 / 5) + 32
    humidity = dhtdevice.humidity
    print(
        "Temp: {:.1f} F / {:.1f} C    Humidity: {}% ".format(
            temperature_f, temperature_c, humidity
        )
    )
