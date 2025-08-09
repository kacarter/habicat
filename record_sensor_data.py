import time
import board
import adafruit_sgp40
import adafruit_tsl2591
from adafruit_bme280 import advanced as adafruit_bme280

i2c = board.I2C()  # uses board.SCL and board.SDA
sgp = adafruit_sgp40.SGP40(i2c)
tsl = adafruit_tsl2591.TSL2591(i2c)
bme280 = adafruit_bme280.Adafruit_BME280_I2C(i2c)
bme280.standby_period = adafruit_bme280.STANDBY_TC_1000

while True:
    temperature_c = bme280.temperature
    temperature = (temperature_c * 9/5) + 32 # F = C * 9/5 + 32
    humidity = bme280.relative_humidity
    lux = tsl.lux
    infrared = tsl.infrared
    visible = tsl.visible

    # For compensated raw gas readings
    compensated_raw_gas = sgp.measure_raw(
        temperature=temperature, relative_humidity=humidity
    )
    print("Raw VOC:", compensated_raw_gas)

    # For Compensated voc index readings
    voc_index = sgp.measure_index(
    temperature=temperature, relative_humidity=humidity)

    print("VOC Index:", voc_index)
    print("Temperature: %0.1f F" % temperature)
    print("Humidity: %0.1f %%" % humidity)
    print("Pressure: %0.1f hPa" % bme280.pressure)
    print(f"Total light: {lux}lux")
    print(f"Infrared light: {infrared}")
    print(f"Visible light: {visible}")
    print("")
    time.sleep(2)
