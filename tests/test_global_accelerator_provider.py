import uuid
import logging
from provider import handler
from cfn import cfn, delete_all_resources

logging.basicConfig(level=logging.INFO)


def test_crud():
    physical_resource_id = None
    try:
        name = f"test-{uuid.uuid4()}"
        request = Request("Create", name)
        response = cfn(handler, request, {})
        assert response["Status"] == "SUCCESS", response["Reason"]
        physical_resource_id = response.get("PhysicalResourceId")
        assert physical_resource_id

        request = Request("Update", f"{name}-new",physical_resource_id)
        response = cfn(handler, request, {})
        assert response["Status"] == "SUCCESS", response["Reason"]
        assert response.get("PhysicalResourceId")
        assert response.get("PhysicalResourceId") == physical_resource_id
    finally:
        if physical_resource_id:
            request = Request("Delete", name, physical_resource_id)
            response = cfn(handler, request, {})
            assert response["Status"] == "SUCCESS", response["Reason"]
        delete_all_resources(handler)

class Request(dict):
    def __init__(self, request_type, name, physical_resource_id=None):
        request_id = "request-%s" % uuid.uuid4()
        self.update(
            {
                "RequestType": request_type,
                "ResponseURL": "https://httpbin.org/put",
                "StackId": "arn:aws:cloudformation:us-west-2:EXAMPLE/stack-name/guid",
                "RequestId": request_id,
                "ResourceType": "Custom::GlobalAccelerator",
                "LogicalResourceId": f"MyCustomAccelerator",
                "ResourceProperties": {
                    "Name": name
                }
            }
        )

        if physical_resource_id:
            self["PhysicalResourceId"] = physical_resource_id
