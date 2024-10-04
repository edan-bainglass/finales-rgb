from FINALES2.schemas import GeneralMetaData, Method, Quantity, ServerConfig
from FINALES2.tenants.referenceTenant import Tenant
from FINALES2.user_management.classes_user_manager import User

from run_both import process_request


class RGBTenant(Tenant):
    """This class represents the RGB tenant."""


rgb_snapshot_method = Method(
    name="RGB-snapshot",
    quantity="RGB",  # output
    parameters=["R", "G", "B"],  # inputs
    limitations={
        "R": [{"min": 0, "max": 255}],
        "G": [{"min": 0, "max": 255}],
        "B": [{"min": 0, "max": 255}],
    },
)


def prepare_results(results):
    # TODO map to schema
    return results


dummy = User(username="dummy", password="password")

rgb_tenant = RGBTenant(
    general_meta=GeneralMetaData(
        name="RGB-measurement",
        description="The RGB tenant.",
    ),
    quantities={
        "RGB": Quantity(
            name="RGB",
            methods={
                "RGB-snapshot": rgb_snapshot_method,
            },
            is_active=True,
        )
    },
    FINALES_server_config=ServerConfig(
        host="localhost",
        port=13371,
    ),
    tenant_config="",  # TODO ask Monika later
    run_method=process_request,
    prepare_results=prepare_results,  # TODO schema
    operators=[dummy],
    tenant_user=dummy,
    tenant_uuid="c2649110-614f-46f8-b7d1-a40fd9d0d95c",
)
