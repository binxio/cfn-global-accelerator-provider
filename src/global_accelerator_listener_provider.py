import copy
import logging
import os
import re
import time

import boto3
from botocore.exceptions import ClientError
from cfn_resource_provider import ResourceProvider

log = logging.getLogger()
log.setLevel(os.environ.get("LOG_LEVEL", "INFO"))


request_schema = {
    "type": "object",
    "required": ["AcceleratorArn", "PortRanges", "Protocol"],
    "properties": {
        "AcceleratorArn": {"type": "string"},
        "PortRanges": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["FromPort", "ToPort"],
                "properties": {
                    "FromPort": {"type": "integer"},
                    "ToPort": {"type": "integer"},
                },
            },
        },
        "Protocol": {"type": "string"},
        "ClientAffinity": {"type": "string", "default": "NONE"},
    },
}


class GlobalAcceleratorListenerProvider(ResourceProvider):
    def __init__(self):
        super(GlobalAcceleratorListenerProvider, self).__init__()
        self._value = None
        self.request_schema = request_schema
        self.ga = boto3.client("globalaccelerator", region_name="us-west-2")

    def convert_property_types(self):
        self.heuristic_convert_property_types(self.properties)

    def create_kwargs(self):
        kwargs = copy.deepcopy(self.properties)
        kwargs.pop("ServiceToken", None)
        if self.request_type != "Create":
            kwargs["ListenerArn"] = self.physical_resource_id
            kwargs.pop("AcceleratorArn", None)
        else:
            kwargs["IdempotencyToken"] = self.request_id
        return kwargs

    def create(self):
        kwargs = self.create_kwargs()
        try:
            response = self.ga.create_listener(**kwargs)
            self.physical_resource_id = response["Listener"]["ListenerArn"]
        except ClientError as e:
            self.fail(f"{e}")
            return

    def update(self):
        if self.get_old('AcceleratorArn', self.get('AcceleratorArn')) == self.get('AcceleratorArn'):
            kwargs = self.create_kwargs()
            self.ga.update_listener(**kwargs)
        else:
            self.fail('AcceleratorArn cannot be updated')
            return


    def delete(self):
        try:
            if re.match(r"arn:.*", self.physical_resource_id):
                self.ga.delete_listener(ListenerArn=self.physical_resource_id)
        except ClientError as e:
            self.fail(f"{e}")


provider = GlobalAcceleratorListenerProvider()


def handler(request, context):
    return provider.handle(request, context)
