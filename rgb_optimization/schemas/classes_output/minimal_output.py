from pydantic import BaseModel, Field


class RGBOutput(BaseModel):
    R: float = Field(description="Red")
    G: float = Field(description="Green")
    B: float = Field(description="Blue")
    cost: float = Field(description="Cost")
