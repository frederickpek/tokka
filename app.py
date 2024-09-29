import uvicorn
from fastapi import FastAPI
from api.payload_model import BatchTransactionFeePayload
from api.response_model import GetTransactionFeeResponse, PostTransactionFeeResponse
from api.TxnFeeClient import TxnFeeClient

app = FastAPI()
txn_fee_client = TxnFeeClient()


@app.get("/transaction-fee/{hash}", response_model=GetTransactionFeeResponse)
async def get_transaction_fee(hash: str):
    txn_fee_client
    return {"hash": hash}


@app.post("/transaction-fee/", response_model=PostTransactionFeeResponse)
async def get_transaction_fees(payload: BatchTransactionFeePayload):
    txn_fee_client
    return {"hashes": payload.hashes}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
