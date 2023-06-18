# Importing necessary libraries
import pandas as pd
import json
from web3 import Web3
from requests import HTTPError
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
import requests

# Load the ABI for the ERC20 token (USDC in this case)
with open('Json_staff\\USDC_ABI.JSON', 'r') as f:
    usdc_abi = json.load(f)

# Load configuration from JSON file
with open("Json_staff\Config.JSON", 'r') as f:
    config = json.load(f)

# Define path to the Excel file with addresses
data_path = "Data\Raw_data.xlsx"

# Load the addresses from the Excel file into a dataframe
df = pd.read_excel(data_path)
addresses = df['Address'].tolist()

# Define network configurations for each network
networks  = {
    'BNB': {"url": "https://bsc-dataseed.binance.org/", "usdc_contract": "0x8ac76a51cc950d9822d68b83fe1ad97b32cd580d"},
    'Polygon': {"url": "https://polygon.llamarpc.com", "usdc_contract": "0x2791bca1f2de4661ed88a30c99a7a9449aa84174"},
    'Fantom': {"url": "https://rpc.fantom.network", "usdc_contract": "0x04068DA6C83AFCFA0e13ba15A6696662335D5B75"},
    'Avalanche': {"url": "https://rpc.ankr.com/avalanche", "usdc_contract": "0xB97EF9Ef8734C71904D8002F8b6Bc66Dd9c48a6E"},
    'Arbitrum': {"url": "https://arb-mainnet-public.unifra.io", "usdc_contract": "0xFF970A61A04b1cA14834A43f5dE4533eBDDB5CC8"},
    'Optimism': {"url": "https://opt-mainnet.g.alchemy.com/v2/demo", "usdc_contract": "0x7f5c764cbc14f9669b88837ca1490cca17c31607"},
    'Ethereum': {"url": "https://ethereum.publicnode.com", "usdc_contract": "0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48"},
}
# Function to get a Web3 instance. Retries if the RPC node rate-limits the requests (HTTP 429 status)
def get_web3_instance(rpc_url, retries=5, delay=15):
    for i in range(retries):
        try:
            web3 = Web3(Web3.HTTPProvider(rpc_url))
            return web3
        except HTTPError as e:
            if e.response.status_code == 429: # Too Many Requests
                print(f"Too many requests to {rpc_url}, retrying in {delay} seconds...")
                time.sleep(delay)
            else:
                raise
    raise Exception("Failed to connect after multiple retries.")

# Function to update prices of the tokens in each network from CoinGecko
def update_prices(config):
    for network in config['networks']:
        token_name = config['networks'][network]['token_name']
        url = f"https://api.coingecko.com/api/v3/simple/price?ids={token_name}&vs_currencies=usd"
        response = requests.get(url)
        data = response.json()
        token_price_usd = data[token_name]['usd']
        config['prices'][network]['usd'] = token_price_usd
        print(f"{data}")
    return config

# Update the prices in the configuration and save back to the JSON file
config = update_prices(config)
with open("Json_staff\Config.JSON", 'w') as json_file:
    json.dump(config, json_file, indent=4)

# Function to process an address. It gets the balance of the native token and USDC on all networks
def process_address(address, retries=5, delay=15):
    wallet_address = address
    checksum_address = Web3.to_checksum_address(wallet_address)
    for network_name in networks:
        for i in range(retries):
            try:
                rpc_url = networks[network_name]['url']
                web3 = get_web3_instance(rpc_url)

                balance_wei = web3.eth.get_balance(checksum_address)
                balance = Web3.from_wei(balance_wei, 'ether')

                # Fetch the token price from the JSON config
                token_price_usd = config['prices'][network_name]['usd']

                balance_usd = float(balance) * token_price_usd  # convert balance to float
                balance_formatted = str("{:.2f}".format(balance_usd)).replace('.', ',')
                print(f"{address} = {network_name} = {balance_formatted}")
                df.loc[df['Address'] == address, f"{network_name}"] = balance_formatted


                usdc_contract_address = networks[network_name]['usdc_contract']
                checksum_usdc_contract_address = Web3.to_checksum_address(usdc_contract_address)
                usdc_contract = web3.eth.contract(address=checksum_usdc_contract_address, abi=usdc_abi)
                balance_of_token = usdc_contract.functions.balanceOf(checksum_address).call()
                decimals = usdc_contract.functions.decimals().call()
                balance_usdc = balance_of_token / (10 ** decimals)
                if balance_usdc >= 0.01:
                    balance_formatted_usdc = str("{:.2f}".format(balance_usdc)).replace('.', ',')
                    print(f"{address} = {network_name} {balance_formatted_usdc} USDC")
                    df.loc[df['Address'] == address, f"{network_name}_USDC"] = balance_formatted_usdc
                else:
                    balance_formatted_usdc = 0
                df.loc[df['Address'] == address, f"{network_name}_USDC"] = balance_formatted_usdc
                break
            except requests.exceptions.HTTPError as e:
                if e.response.status_code == 429: # Too Many Requests
                    print(f"Too many requests to {rpc_url}, retrying in {delay} seconds...")
                    time.sleep(delay)
                else:
                    raise
    return df

# Start processing the addresses. The processing is done in multiple threads to speed up the process.
# The number of threads can be adjusted by changing the `max_workers` parameter.
futures = []
with ThreadPoolExecutor(max_workers=3) as executor:
    for address in addresses:
        futures.append(executor.submit(process_address, address, retries=5, delay=15))

# After all threads have finished, the results are collected and the dataframe is updated with the new balances
for future in as_completed(futures):
    df_result = future.result()
    df.update(df_result)
# Finally, save the updated dataframe back to the Excel file
df.to_excel(data_path, index=False)

#PERFORM BY @Palyanytsya & GPT4