# Transaction Fee Tracker

This application retrieves and tracks transaction fees from the Ethereum UniswapV3 EthUsdc pool.

## Requirements

- Docker
- Docker Compose
- Python 3.10 (Packaged)
- Redis (Packaged)

## Running the Application

1. Clone the repository:

   ```bash
   git clone https://github.com/frederickpek/tokka.git
   cd tokka
   ```

2. Create a .env file in the root directory of the project with your Ethereum API key and RPC URL:

    ```.env
    ETHERSCAN_API_KEY=YOUR_ETHERSCAN_API_KEY
    RPC_URL=YOUR_RPC_URL
    ```

3. Build and run the application using Docker Compose:

   ```bash
   docker-compose up --build
   ```
   The application should spawn a redis instance and 2 other processes - A process to periodically load and batch load hash queries, and another api instance.

4. Access the application:

   - The application will be available at http://localhost:8000
   - The Swagger Doc is available as http://localhost:8000/docs

## API Endpoints

### Get Transaction Fee

**Endpoint:** /transaction-fee/{hash}

- **Method:** GET
- **Path Parameter:**
  - hash: The transaction hash to retrieve the USDT fee for.
- **Response Model:**

```python
class GetTransactionFeeResponse(BaseModel):
    hash: str
    fee: str = ""
    msg: str = "ok"
```

### Sample Curl

```bash
curl -X GET "http://localhost:8000/transaction-fee/0x7edc1beb3e592a7a078cddd8a3b7dd727a32f24780f632ca5ec89ccf1cc6982a"
```

### Example Response

```json
{
  "hash": "0x7edc1beb3e592a7a078cddd8a3b7dd727a32f24780f632ca5ec89ccf1cc6982a",
  "fee": "5.100978709474772", // in USDT
  "msg": "ok"
}
```

**Endpoint:** /transaction-fee

- **Method:** POST
- **Body Parameter:**
  - hashes: An array of hashes to retrieve the USDT fee for.
- **Response Model:**

```python
class PostTransactionFeeResponse(BaseModel):
    fees: list[GetTransactionFeeResponse]
```

### Sample Curl

```bash
curl -X POST "http://localhost:8000/transaction-fee/" \
-H "accept: application/json" \
-H "Content-Type: application/json" \
-d '{"hashes": ["0x7edc1beb3e592a7a078cddd8a3b7dd727a32f24780f632ca5ec89ccf1cc6982a", "0x646706f493c63c7c18285163808d43648e508129fd4d200a3dd4c24a6eac354c", "0x33600e9183dde58d8b787f63af70fc9a4d458c1f5ccb53e622c90658aa6f768a", "qwer"]}'
```

### Example Response

```json
{
    "fees" [
        {
          "hash": "0x7edc1beb3e592a7a078cddd8a3b7dd727a32f24780f632ca5ec89ccf1cc6982a",
          "fee": "5.100978709474772", // in USDT
          "msg": "ok"
        },
        {
          "hash": "0x646706f493c63c7c18285163808d43648e508129fd4d200a3dd4c24a6eac354c",
          "fee": "",
          "msg": "non uniswapv3 pool txn"
        },
        {
          "hash": "0x33600e9183dde58d8b787f63af70fc9a4d458c1f5ccb53e622c90658aa6f768a",
          "fee": "",
          "msg": "queued for processing, query again after some time"
        },
        {
          "hash": "qwer",
          "fee": "",
          "msg": "invalid hash"
        },
    ]
}
```
