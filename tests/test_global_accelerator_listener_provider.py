import uuid
import logging
from provider import handler
from cfn import cfn, delete_all_resources
from test_global_accelerator_provider import Request as GARequest

logging.basicConfig(level=logging.INFO)


def test_crud():
    physical_resource_id = None
    listener = {
        "AcceleratorArn": "",
        "PortRanges": [{"FromPort": "53", "ToPort": "53"}],
        "Protocol": "UDP",
        "ClientAffinity": "SOURCE_IP",
    }
    try:

        name = f"test-{uuid.uuid4()}"
        request = GARequest("Create", name)
        response = cfn(handler, request, {})
        assert response["Status"] == "SUCCESS", response["Reason"]
        acceleratorArn = response.get("PhysicalResourceId")

        listener = {
            "AcceleratorArn": acceleratorArn,
            "PortRanges": [{"FromPort": "53", "ToPort": "53"}],
            "Protocol": "UDP",
            "ClientAffinity": "SOURCE_IP",
        }
        request = Request("Create", listener)
        response = cfn(handler, request, {})
        assert response["Status"] == "SUCCESS", response["Reason"]
        assert response.get("PhysicalResourceId")
        physical_resource_id = response.get("PhysicalResourceId")

        listener["PortRanges"][0]["ToPort"] = "1553"
        listener["ClientAffinity"] = "SOURCE_IP"

        request = Request("Update", listener, physical_resource_id)
        response = cfn(handler, request, {})
        assert response["Status"] == "SUCCESS", response["Reason"]
        assert response.get("PhysicalResourceId") == physical_resource_id
    finally:
        if physical_resource_id:
            request = Request("Delete", listener, physical_resource_id)
            response = cfn(handler, request, {})
            assert response["Status"] == "SUCCESS", response["Reason"]
        delete_all_resources(handler)


class Request(dict):
    def __init__(self, request_type, listener, physical_resource_id=None):
        request_id = "request-%s" % uuid.uuid4()
        self.update(
            {
                "RequestType": request_type,
                "ResponseURL": "https://httpbin.org/put",
                "StackId": "arn:aws:cloudformation:us-west-2:EXAMPLE/stack-name/guid",
                "RequestId": request_id,
                "ResourceType": "Custom::GlobalAcceleratorListener",
                "LogicalResourceId": f"MyCustomAcceleratorListener",
                "ResourceProperties": listener,
            }
        )

        if physical_resource_id:
            self["PhysicalResourceId"] = physical_resource_id
