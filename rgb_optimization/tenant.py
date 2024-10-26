#!/usr/bin/env python3

import logging
from uuid import uuid4

from FINALES2.schemas import GeneralMetaData, Method, Quantity, ServerConfig
from FINALES2.server.schemas import Request, RequestInfo
from FINALES2.tenants.referenceTenant import Tenant
from FINALES2.user_management.classes_user_manager import User
from optimize import optimize_rgb

logger = logging.getLogger("RGBOptimizationTenant")


class RGBOptimizationTenant(Tenant):
    """A Tenant to manage RGB optimization."""


def run_optimization(input_request: RequestInfo):
    request_ID = input_request["uuid"]  # type: ignore
    request = Request(**input_request["request"])  # type: ignore
    method = request.methods[0]
    parameters = request.parameters[method]

    logger.info(
        (
            "Request information:",
            f"  request: {request_ID}",
            f"  method: {method}",
            f"  parameters: {parameters}",
        )
    )

    optimization_id = str(uuid4())

    logger.info(f"{request_ID}: {optimization_id}")

    result = optimize_rgb(
        id=optimization_id,
        **parameters,
    )

    id, minimum, cost = result

    logger.info(
        (
            "Optimization result:",
            f"  id: {id}",
            f"  minimum: {minimum}",
            f"  cost: {cost}",
        )
    )

    return result


def prepare_result(request: dict, data):
    logger.info(
        (
            "Preparing results for:",
            f"  request: {request['uuid']}",
            f"  measurement: {data['measurement_id']}",
        )
    )

    request_technical = Request(**request["request"])
    method = "rgb-measurement"

    result = {
        "data": {
            method: {
                "R": data["R"],
                "G": data["G"],
                "B": data["B"],
                "cost": data["cost"],
            }
        },
        "quantity": request_technical.quantity,
        "method": request_technical.methods,
        "parameters": {method: request_technical.parameters},
        "tenant_uuid": request_technical.tenant_uuid,
        "request_uuid": request["uuid"],
    }

    logger.info(
        (
            "Prepared result:",
            result,
        )
    )

    return result


rgb_optimization_method = Method(
    name="RGB-optimization",
    parameters=["R", "G", "B", "n_calls"],
    limitations={
        "R": [{"min": 0, "max": 255}],
        "G": [{"min": 0, "max": 255}],
        "B": [{"min": 0, "max": 255}],
        "n_calls": [{"min": 1, "max": 100}],
    },
    quantity="RGB-prediction",
)

dummy = User(username="dummy", password="password")


rgb_optimization_tenant = RGBOptimizationTenant(
    general_meta=GeneralMetaData(
        name="RGB-optimization",
        description="The RGB optimization tenant.",
    ),
    quantities={
        "RGB-prediction": Quantity(
            name="RGB-prediction",
            methods={
                "RGB-optimization": rgb_optimization_method,
            },
            is_active=True,
        )
    },
    FINALES_server_config=ServerConfig(
        host="localhost",
        port=13371,
    ),
    tenant_config="",
    run_method=run_optimization,
    prepare_results=prepare_result,
    operators=[dummy],
    tenant_user=dummy,
    tenant_uuid="9d6fa815-5f44-4c2b-9e7f-259232fa9375",
)

# rgb_optimization_tenant.tenant_object_to_json()
rgb_optimization_tenant.run()
