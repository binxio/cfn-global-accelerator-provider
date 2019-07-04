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
    "required": ["ListenerArn", "EndpointGroupRegion"],
    "properties": {
        "ListenerArn": {"type": "string"},
        "EndpointGroupRegion": {"type": "string"},
    },
}


class GlobalAcceleratorEndpointGroupProvider(ResourceProvider):
    def __init__(self):
        super(GlobalAcceleratorEndpointGroupProvider, self).__init__()
        self._value = None
        self.request_schema = request_schema
        self.ga = boto3.client("globalaccelerator", region_name="us-west-2")
        self.non_updateable = ["ListenerArn", "EndpointGroupRegion"]

    def convert_property_types(self):
        self.heuristic_convert_property_types(self.properties)

    def create_kwargs(self):
        kwargs = copy.deepcopy(self.properties)
        kwargs.pop("ServiceToken", None)
        if self.request_type != "Create":
            for name in self.non_updateable:
                kwargs.pop(name, None)
            kwargs["EndpointGroupArn"] = self.physical_resource_id
        else:
            kwargs["IdempotencyToken"] = self.request_id
        return kwargs

    def create(self):
        kwargs = self.create_kwargs()
        try:
            response = self.ga.create_endpoint_group(**kwargs)
            self.physical_resource_id = response["EndpointGroup"]["EndpointGroupArn"]
        except ClientError as e:
            self.fail(f"{e}")

    def is_valid_update(self):
        if self.request_type != 'Update':
            return True

        for name in self.non_updateable:
            if self.get_old(name, self.get(name)) != self.get(name):
                self.fail(f"{name} cannot be updated")
                return False
        return True

    def is_valid_cfn_request(self):
        return super(GlobalAcceleratorEndpointGroupProvider, self).is_valid_cfn_request() and self.is_valid_update()

    def update(self):
        kwargs = self.create_kwargs()
        self.ga.update_endpoint_group(**kwargs)

    def delete(self):
        try:
            if re.match(r"arn:.*", self.physical_resource_id):
                self.ga.delete_endpoint_group(
                    EndpointGroupArn=self.physical_resource_id
                )
        except ClientError as e:
            self.fail(f"{e}")


provider = GlobalAcceleratorEndpointGroupProvider()


def handler(request, context):
    return provider.handle(request, context)
