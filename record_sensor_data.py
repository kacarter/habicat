import time
import datetime
import board
import adafruit_sgp40
import adafruit_tsl2591
from adafruit_bme280 import advanced as adafruit_bme280
import influxdb_client, os
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS

# TODO decide on Python IDE
# TODO decide on way to export env variable to persist across rebooting etc
# TODO create service to run all this
# TODO change code to run in service
# TODO set service to run on startup
# TODO finish setting up grafana
# TODO refactor python code to be less hideous
# TODO add error handling for sensor etc errors including a way to notify me

i2c = board.I2C()
sgp = adafruit_sgp40.SGP40(i2c)
tsl = adafruit_tsl2591.TSL2591(i2c)
bme280 = adafruit_bme280.Adafruit_BME280_I2C(i2c)
bme280.standby_period = adafruit_bme280.STANDBY_TC_1000

token = os.environ.get("INFLUXDB_TOKEN")
org = "Environment Monitoring"
url = "http://localhost:8086"

write_client = influxdb_client.InfluxDBClient(url=url, token=token, org=org)
bucket="Habicat"

write_api = write_client.write_api(write_options=SYNCHRONOUS)
i = 0

while True:
    temperature_c = bme280.temperature
    temperature = (temperature_c * 9/5) + 32 # F = C * 9/5 + 32
    humidity = bme280.relative_humidity
    lux = tsl.lux
    infrared = tsl.infrared
    visible = tsl.visible
    dewpoint = temperature - ((100 - humidity) / 5)  # Td = T - ((100 - RH) / 5)
    timestamp = datetime.datetime.now(datetime.UTC)
    pressure = bme280.pressure

    # For compensated raw gas readings
    compensated_raw_gas = sgp.measure_raw(
        temperature=temperature_c, relative_humidity=humidity
    )
    #print("Raw VOC:", compensated_raw_gas)

    # For Compensated voc index readings
    voc_index = sgp.measure_index(
        temperature=temperature_c, relative_humidity=humidity)

    #print("VOC Index:", voc_index)
    #print("Temperature: %0.1f F" % temperature)
    #print("Humidity: %0.1f %%" % humidity)
    #print("Pressure: %0.1f hPa" % pressure)
    #print(f"Total light: {lux}lux")
    #print(f"Infrared light: {infrared}")
    #print(f"Visible light: {visible}")
    #print(i)
    #print("")

    if i >= 300:
      point = (
        Point("environmental_data")
          .tag("location", "office")
          .tag("light_sensor", "adafruit_tsl2591")
          .tag("voc_sensor", "adafruit_sgp40")
          .tag("temp_sensor", "adafruit_bme280")
          .field("temperature", temperature)
          .field("humidity", humidity)
          .field("pressure", pressure)
          .field("lux", lux)
          .field("infrared", infrared)
          .field("visible", visible)
          .field("dewpoint", dewpoint)
          .field("compensated_raw_gas", compensated_raw_gas)
          .field("voc_index", voc_index)
          .time(timestamp)
        )

      write_api.write(bucket=bucket, org=org, record=point)
      i = 0

    time.sleep(1)
    i = i + 1

