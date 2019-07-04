import uuid
import logging
import pytest
from provider import handler
from cfn import cfn, delete_all_resources
from test_global_accelerator_provider import Request as GARequest
from test_global_accelerator_listener_provider import Request as ListenerRequest

logging.basicConfig(level=logging.INFO)


@pytest.fixture
def listenerArn():
    name = f"test-{uuid.uuid4()}"
    request = GARequest("Create", name)
    response = cfn(handler, request, {})
    assert response["Status"] == "SUCCESS", response["Reason"]
    acceleratorArn = response.get("PhysicalResourceId")

    listener = {
        "AcceleratorArn": acceleratorArn,
        "PortRanges": [{"FromPort": 53, "ToPort": 53}],
        "Protocol": "UDP",
        "ClientAffinity": "SOURCE_IP",
    }
    request = ListenerRequest("Create", listener)
    response = cfn(handler, request, {})
    assert response["Status"] == "SUCCESS", response["Reason"]
    assert response.get("PhysicalResourceId")
    listenerArn = response.get("PhysicalResourceId")

    return listenerArn


def test_crud(listenerArn):
    physical_resource_id = None
    endpoint_group = {
        "ListenerArn": listenerArn,
        "EndpointGroupRegion": "eu-central-1"
    }
    try:
        request = Request("Create", endpoint_group)
        response = cfn(handler, request, {})
        assert response["Status"] == "SUCCESS", response["Reason"]
        physical_resource_id = response.get("PhysicalResourceId")
        assert physical_resource_id

        endpoint_group["HealthCheckProtocol"] = "TCP"
        endpoint_group["HealthCheckPort"] = 80
        request = Request("Update", endpoint_group, physical_resource_id)
        response = cfn(handler, request, {})
        assert response["Status"] == "SUCCESS", response["Reason"]
        assert physical_resource_id == response.get("PhysicalResourceId")

    finally:
        if physical_resource_id:
            request = Request("Delete", endpoint_group, physical_resource_id)
            response = cfn(handler, request, {})
            assert response["Status"] == "SUCCESS", response["Reason"]
        delete_all_resources(handler)


class Request(dict):
    def __init__(self, request_type, endpoint_group, physical_resource_id=None):
        request_id = "request-%s" % uuid.uuid4()
        self.update(
            {
                "RequestType": request_type,
                "ResponseURL": "https://httpbin.org/put",
                "StackId": "arn:aws:cloudformation:us-west-2:EXAMPLE/stack-name/guid",
                "RequestId": request_id,
                "ResourceType": "Custom::GlobalAcceleratorEndpointGroup",
                "LogicalResourceId": f"MyCustomAcceleratorEndpointGroup",
                "ResourceProperties": endpoint_group,
            }
        )

        if physical_resource_id:
            self["PhysicalResourceId"] = physical_resource_id
