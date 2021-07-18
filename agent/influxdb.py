from typing import Dict
from datetime import datetime

from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS

class InfluxDbClient:
    def __init__(self, org, bucket, token):
        self.org = org
        self.bucket = bucket

        self.client = InfluxDBClient(url="https://eastus-1.azure.cloud2.influxdata.com", token=token)
        self.write_api = self.client.write_api(write_options=SYNCHRONOUS)

    def write(self, table: str, tags: Dict[str,str], field_name: str, field_value: float, time: datetime):
        point = Point(table)

        for tag_name in tags.keys():
            point = point.tag(tag_name, tags[tag_name])

        point.field(field_name, field_value).time(time)
        
        self.write_api.write(self.bucket, self.org, point)