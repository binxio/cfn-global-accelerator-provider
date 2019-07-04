import os
import logging
import global_accelerator_provider
import global_accelerator_listener_provider
import global_accelerator_endpoint_group_provider

logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))


def handler(request, context):
    request_type = request["ResourceType"]
    if request_type == "Custom::GlobalAccelerator":
        return global_accelerator_provider.handler(request, context)
    elif request_type == "Custom::GlobalAcceleratorListener":
        return global_accelerator_listener_provider.handler(request, context)
    elif request_type == "Custom::GlobalAcceleratorEndpointGroup":
        return global_accelerator_endpoint_group_provider.handler(request, context)
    else:
        return global_accelerator_provider.handler(request, context)
