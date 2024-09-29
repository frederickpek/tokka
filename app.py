import uvicorn
from fastapi import FastAPI
from api.payload_model import BatchTransactionFeePayload
from api.response_model import GetTransactionFeeResponse, PostTransactionFeeResponse
from api.TxnFeeClient import TxnFeeClient

app = FastAPI()
txn_fee_client = TxnFeeClient()


@app.get("/")
async def home():
    return "app is live"


@app.get("/transaction-fee/{hash}", response_model=GetTransactionFeeResponse)
async def get_transaction_fee(hash: str):
    resp = await txn_fee_client.get_fee_response(hash=hash)
    return resp


@app.post("/transaction-fee/", response_model=PostTransactionFeeResponse)
async def get_transaction_fees(payload: BatchTransactionFeePayload):
    resp = await txn_fee_client.get_fee_responses(payload.hashes)
    return resp


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
