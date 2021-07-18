import yaml
from sensorpush import SensorPushClient, Sensor, Sample
from influxdb import InfluxDbClient

with open('../secret.yaml') as f:
    secrets = yaml.load(f, Loader=yaml.FullLoader)

sensorpush_client = SensorPushClient(secrets['sensorpush']['email'], secrets['sensorpush']['password'])
influxdb_client = InfluxDbClient(secrets['influxdb']['org'], secrets['influxdb']['bucket'], secrets['influxdb']['token'])

gateways = sensorpush_client.get_gateways()
print(gateways)

sensors = sensorpush_client.get_sensors()
print(sensors)
Sensor.print_sensors(sensors)

# samples = sensorpush_client._get_samples()
samples = sensorpush_client.get_samples(sensors)
Sample.print_samples(samples)

for sample in samples:
    influxdb_client.write("sensordata", {'sensor': sample.sensor.name}, "temperature", sample.temperature, sample.observed)
    influxdb_client.write("sensordata", {'sensor': sample.sensor.name}, "humidity", sample.humidity, sample.observed)