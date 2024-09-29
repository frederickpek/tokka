from pydantic import BaseModel, Field


class GetTransactionFeeResponse(BaseModel):
    hash: str = Field(..., description="The transaction hash")
    fee: str = Field("", description="The transaction fee in USDT amounts")
    msg: str = Field(
        "ok",
        description="A message indicating the result of the operation, typically 'ok'",
    )


class PostTransactionFeeResponse(BaseModel):
    fees: list[GetTransactionFeeResponse]
