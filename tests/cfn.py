import json
import logging
import uuid
from collections import OrderedDict
objects = OrderedDict()
cfn_deleted = OrderedDict()
log = logging.getLogger()


def cfn(handler, request, context):
    if request["RequestType"] == "Create":
        response = handler(request, context)
        if response["Status"] == "SUCCESS":
            physical_resource_id = response["PhysicalResourceId"]
            objects[physical_resource_id] = json.loads(json.dumps(request))

    if request["RequestType"] == "Delete":
        physical_resource_id = request["PhysicalResourceId"]
        response = handler(request, context)
        if physical_resource_id in objects:
            del objects[physical_resource_id]
        return response

    if request["RequestType"] == "Update":
        physical_resource_id = request["PhysicalResourceId"]
        exists = physical_resource_id in objects
        assert exists
        request["OldResourceProperties"] = json.loads(
            json.dumps(objects[physical_resource_id]["ResourceProperties"])
        )
        response = handler(request, context)
        if response["Status"] == "SUCCESS":
            if response["PhysicalResourceId"] != physical_resource_id:
                objects[response["PhysicalResourceId"]] = json.loads(
                    json.dumps(request)
                )
                # delete the old resource, if the physical resource id change
                delete_request = json.loads(json.dumps(objects[physical_resource_id]))
                delete_request["PhysicalResourceId"] = physical_resource_id
                delete_request["RequestType"] = "Delete"
                request["RequestId"] = str(uuid.uuid4())
                delete_response = handler(delete_request, context)
                assert delete_response["Status"] == "SUCCESS", delete_response["Reason"]
                cfn_deleted[physical_resource_id] = True

    return response


def delete_all_resources(handler):
    log.info("created objects\n%s\n", json.dumps(objects, indent=2))
    log.info("deleted objects\n%s\n", json.dumps(cfn_deleted, indent=2))
    to_delete = []
    for physical_resource_id in objects:
        if physical_resource_id not in cfn_deleted:
            to_delete.append(physical_resource_id)
    to_delete = list(reversed(to_delete))
    log.info("to delete\n%s\n", json.dumps(to_delete, indent=2))
    for physical_resource_id in to_delete:
        request = json.loads(json.dumps(objects[physical_resource_id]))
        request["PhysicalResourceId"] = physical_resource_id
        request["RequestType"] = "Delete"
        request["RequestId"] = str(uuid.uuid4())
        response = cfn(handler, request, {})
        assert response["Status"] == "SUCCESS", response["Reason"]
