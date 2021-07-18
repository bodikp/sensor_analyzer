from typing import List
import requests
from dataclasses import dataclass
import json
import datetime

@dataclass
class Sample:
    sensor_id: str
    observed: str
    temperature: float
    humidity: float

    def __init__(self, sensor, data):
        self.sensor = sensor
        self.observed = datetime.datetime.fromisoformat(data['observed'].replace('Z', '+00:00'))
        self.temperature = data['temperature']
        self.humidity = data['humidity']

    def str(self):
        return f'{self.sensor.name:20} {self.observed.strftime("%H:%M:%S"):<20} {self.temperature:<10} {self.humidity:<10}'

    @classmethod
    def print_samples(cls, samples: List['Sample']):
        print(f'{"sensor":20} {"time":<20} {"temp":<10} {"hum":<10}')
        for s in sorted(samples, key=lambda x: x.sensor.name + str(x.observed)):
            print(s.str())

@dataclass
class Sensor:
    id: str
    device_id: str = None
    name: str = None
    rssi: float = None
    battery_voltage: float = None

    def __init__(self, data):
        self.id = data['id']
        self.device_id = data['deviceId']
        self.name = data['name']
        self.rssi = data['rssi']
        self.battery_voltage = data['battery_voltage']

    def str(self):
        return f'{self.name:<20} {self.rssi:>10} {self.battery_voltage:>10}'

    @classmethod
    def print_sensors(cls, sensors: List['Sensor']):
        print(f'{"name":<20} {"rssi":>10} {"battery":>10}')
        for s in sorted(sensors, key=lambda x: x.name):
            print(s.str())


class SensorPushClient:
    def __init__(self, email, password):
        self.base_url = 'https://api.sensorpush.com/api/v1'

        self.email = email
        self.password = password

        self._access_token = None

        self._authorize()
        self._refresh_token()

    def _headers(self):
        headers = {
            'User-Agent':    'bodikp/sensorpush',
            'Accept':        'application/json',
            'Content-Type':  'application/json'
        }

        if self._access_token:
            headers['Authorization'] = self._access_token

        # print(f'using headers: {headers}')
        return headers

    def _post(self, path: str, body={}):
        return requests.post(f'{self.base_url}{path}', json=body, headers=self._headers())

    def _get(self, path: str):
        return requests.get(f'{self.base_url}{path}', headers=self._headers())

    def _authorize(self):
        response = self._post('/oauth/authorize', body={
            'email': self.email,
            'password': self.password
        })

        self._authorization = response.json()['authorization']
        self._api_key = response.json()['apikey']

        # print(f'token={self._authorization[:20]}..., apiKey={self._api_key}')

    def _refresh_token(self):
        response = self._post('/oauth/accesstoken',
                              body={'authorization': self._authorization})
        self._access_token = response.json()['accesstoken']

    def get_gateways(self):
        return self._post('/devices/gateways').json()

    def get_sensors(self) -> List[Sensor]:
        response = self._post('/devices/sensors').json()
        return [Sensor(r) for r in response.values()]

    def _get_samples(self):
        response = self._post('/samples').json()
        # print(json.dumps(response, indent=2))
        return response

    def get_samples(self, sensors):
        response = self._get_samples()
        samples = []

        for sensor_id in response['sensors'].keys():
            sensor = list(filter(lambda s: s.id==sensor_id, sensors))[0]
            # print(f'processing sensor: {sensor}')
            
            sensor_samples_raw = response['sensors'][sensor_id]
            # print(f'  got {len(sensor_samples_raw)} samples')

            sensor_samples = [Sample(sensor, d) for d in sensor_samples_raw]
            samples.extend(sensor_samples)

        return samples