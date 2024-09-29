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

2. I have updated the the .env file in the root directory of the project with my free-tier Etherscan API key and Infura rpc url, feel free to substitute them with your own:

    ```bash
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

# Testing

Testing will be done locally with python's builtin unittest framework.
To run tests and generate a coverage report, follow these steps:

### 1. Set up a Python Virtual Environment
Ensure you have Python >= 3.9 installed. Then, create a virtual environment:

  ```bash
  python3 -m virtualenv venv
  ```

### 2. Activate the Virtual Environment
For Linux/macOS:
  ```bash
  source venv/bin/activate
  ```
For Windows:
  ```bash
  .\venv\Scripts\activate
  ```

### 3. Install the Required Dependencies
Install all dependencies from the `requirements.txt` file:
  ```bash
  pip install -r requirements.txt
  ```
### 4. Run the Tests with Coverage Reporting
To run all tests in the project and generate a coverage report, run the following command:

  ```bash
  python -m coverage run --omit="tests/*" -m unittest discover -p "test_*.py" && python -m coverage report
  ```

This command will run all test files starting with `test_` in the `tests/` directory, omitting the test files from the coverage report.

### Example Output
After running the command, you should see output similar to this:

  ```
  -------------------------------------------------------------------
  Ran 27 tests in 0.323s

  OK
  Name                                            Stmts   Miss  Cover
  -------------------------------------------------------------------
  api/TxnFeeClient.py                                33      0   100%
  api/response_model.py                               7      0   100%
  consts.py                                           7      0   100%
  loader/BaseLoader.py                               31      9    71%
  loader/BinancePriceApi.py                          17      5    71%
  loader/PeriodicLoader.py                           38      0   100%
  loader/Web3PubSubLoader.py                         43      0   100%
  loader/etherscan_loader/EtherscanApi.py            13      4    69%
  loader/etherscan_loader/EtherscanTxnLoader.py      11      0   100%
  loader/web3_loader/Web3TxnLoader.py                13      0   100%
  loader/web3_loader/Web3TxnVerifier.py              19      0   100%
  util/RedisClient.py                                13      4    69%
  util/__init__.py                                    4      0   100%
  -------------------------------------------------------------------
  TOTAL                                             249     22    91%
  ```
