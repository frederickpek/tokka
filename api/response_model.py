from pydantic import BaseModel


class GetTransactionFeeResponse(BaseModel):
    hash: str
    fee: str = ""
    msg: str = "ok"


class PostTransactionFeeResponse(BaseModel):
    fees: list[GetTransactionFeeResponse]
