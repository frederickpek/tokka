from pydantic import BaseModel


class BatchTransactionFeePayload(BaseModel):
    hashes: list[str]
