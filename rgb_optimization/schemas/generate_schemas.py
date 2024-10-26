#!/usr/bin/env python3

import json
import pathlib

from classes_input import RGBInput
from classes_output import RGBOutput

BASEPATH = pathlib.Path(__file__).parent.resolve()
BASEPATH_QUANTITIES = BASEPATH / "serialized_quantities"


# This function is not used at the moment, but it is kept here for easy reactivation in the future
def generate_schema(pydantic_class, filepath):
    """Generates the schema from a pydantic class and stores it in a file."""
    with open(filepath, "w") as fileobj:
        fileobj.write(pydantic_class.schema_json(indent=2))


def generate_quantity(
    quantity_name,
    method_name,
    input_schema,
    output_schema,
    filepath,
):
    """Generates the schema from a pydantic class and stores it in a file."""
    dictobj = {
        "quantity": quantity_name,
        "method": method_name,
        "json_schema_specifications": input_schema.model_json_schema(),
        "json_schema_result_output": output_schema.model_json_schema(),
        "is_active": True,
    }
    with open(filepath, "w") as fileobj:
        json.dump(dictobj, fileobj, indent=2)


if __name__ == "__main__":
    quantity = "RGB-prediction"
    method = "RGB-optimization"
    quantity_path = BASEPATH_QUANTITIES / quantity / f"{method}.json"
    generate_quantity(
        quantity,
        method,
        RGBInput,
        RGBOutput,
        quantity_path,
    )
