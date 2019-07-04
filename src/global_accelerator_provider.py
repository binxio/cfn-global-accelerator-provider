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
    "properties": {
        "Name": {"type": "string"},
        "IpAddressType": {"type": "string", "default": "IPV4"},
        "Enabled": {"type": "boolean", "default": True},
    },
}


class GlobalAcceleratorProvider(ResourceProvider):
    def __init__(self):
        super(GlobalAcceleratorProvider, self).__init__()
        self._value = None
        self.request_schema = request_schema
        self.ga = boto3.client("globalaccelerator", region_name="us-west-2")

    def create_kwargs(self):
        kwargs = copy.deepcopy(self.properties)
        kwargs.pop("ServiceToken", None)
        if self.request_type != "Create":
            kwargs["AcceleratorArn"] = self.physical_resource_id
        else:
            kwargs["IdempotencyToken"] = self.request_id
        return kwargs

    def convert_property_types(self):
        self.heuristic_convert_property_types(self.properties)

    def wait_until_deployed(self, arn, status="IN_PROGRESS"):
        while status != "DEPLOYED":
            log.info(
                f"waiting for Global Accelerator {arn} to be in status DEPLOYED, got {status}"
            )
            time.sleep(10)
            response = self.ga.describe_accelerator(AcceleratorArn=arn)
            status = response["Accelerator"]["Status"]
        log.info(f"Global Accelerator {arn} in status DEPLOYED")

    def set_attributes(self, response):
        ip_addresses = next(
            iter(
                filter(
                    lambda s: s["IpFamily"].upper()
                    == self.get("IpAddressType").upper(),
                    response["Accelerator"]["IpSets"],
                )
            ),
            None,
        )
        if ip_addresses:
            self.set_attribute("IpAddresses", ",".join(ip_addresses["IpAddresses"]))

    def create(self):
        kwargs = self.create_kwargs()
        try:
            response = self.ga.create_accelerator(**kwargs)
            self.physical_resource_id = response["Accelerator"]["AcceleratorArn"]
            self.set_attributes(response)
        except ClientError as e:
            self.fail(f"{e}")
            return

        self.wait_until_deployed(
            self.physical_resource_id, response["Accelerator"]["Status"]
        )

    def update(self):
        kwargs = self.create_kwargs()
        response = self.ga.update_accelerator(**kwargs)
        self.set_attributes(response)
        self.wait_until_deployed(
            self.physical_resource_id, response["Accelerator"]["Status"]
        )

    def disable(self):
        response = self.ga.update_accelerator(
            AcceleratorArn=self.physical_resource_id, Enabled=False
        )
        self.wait_until_deployed(
            self.physical_resource_id, response["Accelerator"]["Status"]
        )

    def delete(self):
        try:
            if re.match(r"arn:.*", self.physical_resource_id):
                self.disable()
                self.ga.delete_accelerator(AcceleratorArn=self.physical_resource_id)
        except ClientError as e:
            self.fail(f"{e}")


provider = GlobalAcceleratorProvider()


def handler(request, context):
    return provider.handle(request, context)
