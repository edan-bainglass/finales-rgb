from pydantic import BaseModel, Field


class RGBInput(BaseModel):
    R: float = Field(description="Red")
    G: float = Field(description="Green")
    B: float = Field(description="Blue")
    warmup_time: float = Field(
        description="Warmup time in seconds",
        default=1,
    )
