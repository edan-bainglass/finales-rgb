#!/usr/bin/env python3

import datetime
import logging
from uuid import uuid4

from FINALES2.schemas import GeneralMetaData, Method, Quantity, ServerConfig
from FINALES2.server.schemas import Request, RequestInfo
from FINALES2.tenants.referenceTenant import Tenant
from FINALES2.user_management.classes_user_manager import User

from rgb_measurement import measure_rgb_from_snapshot, simulate_rgb_measurement

logger = logging.getLogger("RGBMeasurementTenant")


class RGBMeasurementTenant(Tenant):
    """A tenant to manage RGB measurements."""


def run_measurement(input_request: RequestInfo):
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

    measurement_id = str(uuid4())

    logger.info(f"{request_ID}: {measurement_id}")

    if method == "RGB-snapshot":
        result = measure_rgb_from_snapshot(
            id=measurement_id,
            **parameters,
        )
    elif method == "RGB-simulation":
        result = simulate_rgb_measurement(
            id=measurement_id,
            **parameters,
        )

    id, R, G, B = result

    logger.info(
        (
            "Measurement results:",
            f"  id: {id}",
            f"  RGB: [{R}, {G}, {B}]",
        )
    )

    return result


def prepare_result(request: dict, data):
    logger.info(
        (
            "Preparing results for:",
            f"  request: {request['uuid']}",
            f"  measurement: {data['id']}",
        )
    )

    request_technical = Request(**request["request"])
    method = request_technical.methods[0]

    result = {
        "data": {
            method: {
                "R": data["R"],
                "G": data["G"],
                "B": data["B"],
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


rgb_snapshot_method = Method(
    name="RGB-snapshot",
    parameters=["R", "G", "B", "warmup_time"],
    limitations={
        "R": [{"min": 0, "max": 255}],
        "G": [{"min": 0, "max": 255}],
        "B": [{"min": 0, "max": 255}],
        "warmup_time": [{"min": 0, "max": 10}],
    },
    quantity="RGB-measurement",
)


rgb_simulation_method = Method(
    name="RGB-simulation",
    parameters=["R", "G", "B", "warmup_time"],
    limitations={
        "R": [{"min": 0, "max": 255}],
        "G": [{"min": 0, "max": 255}],
        "B": [{"min": 0, "max": 255}],
        "warmup_time": [{"min": 0, "max": 10}],
    },
    quantity="RGB-measurement",
)

dummy = User(username="dummy", password="password")

rgb_measurement_tenant = RGBMeasurementTenant(
    general_meta=GeneralMetaData(
        name="RGB-measurement",
        description="The RGB measurement tenant.",
    ),
    quantities={
        "RGB-measurement": Quantity(
            name="RGB-measurement",
            methods={
                "RGB-snapshot": rgb_snapshot_method,
                "RGB-simulation": rgb_simulation_method,
            },
            is_active=True,
        )
    },
    FINALES_server_config=ServerConfig(
        host="localhost",
        port=13371,
    ),
    tenant_config="",
    run_method=run_measurement,
    prepare_results=prepare_result,
    operators=[dummy],
    tenant_user=dummy,
    tenant_uuid="f8ce68ea-c57e-474b-b2f2-815cea8f2cc7",
    end_run_time=datetime.datetime.now() + datetime.timedelta(hours=4),
)

# rgb_measurement_tenant.tenant_object_to_json()
rgb_measurement_tenant.run()
