import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()


class BatchTransactionFeePayload(BaseModel):
    hashes: list[str]


class GetTransactionFeeResponse(BaseModel):
    hash: str


class PostTransactionFeeResponse(BaseModel):
    hashes: list[str]


@app.get("/transaction-fee/{hash}", response_model=GetTransactionFeeResponse)
async def get_transaction_fee(hash: str):
    return {"hash": hash}


@app.post("/transaction-fee/", response_model=PostTransactionFeeResponse)
async def get_transaction_fees(payload: BatchTransactionFeePayload):
    return {"hashes": payload.hashes}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
