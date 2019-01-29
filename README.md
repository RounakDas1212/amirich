# Am I rich?

no.

## Installation

* Clone this git repository
* Create a virtualenv
* Install this module
```bash
cd amirich
pip install -IU .
```

### Usage
* Get an AlphaVantage API Key (It's free!) [here](https://www.alphavantage.co/support/#api-key) 

* Set the API key in the environment
```bash
export ALPHAVANTAGE_API_KEY=MySecretKey
```

* Use the CLI
```bash
amirich --help
```

### Examples
* You want to sell 100 Microsoft stocks, how much money will that get you? (in USD)
```bash
amirich 100xMSFT
```

* You want to sell 50 Adobe stocks & 75 Microsoft stocks
```bash
amirich 50xADBE 75xMSFT
```

* How much is your 200 Adobe RSU worth today in INR?
```bash
amirich 200xADBE --in INR
```

### License
MIT