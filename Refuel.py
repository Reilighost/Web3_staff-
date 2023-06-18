# Import necessary modules
import random
import time
from web3 import Web3, HTTPProvider
import pandas as pd
import json

# Load JSON config file
with open("Json_staff\\Config.JSON", 'r') as f:
    config = json.load(f)

# Ask user for minimum and maximum delay and amount
min_delay = float(input("Enter minimum delay between transaction: "))
max_delay = float(input("Enter maximum delay between transaction: "))
min_amount = float(input("Enter minimum amount (in AVAX token): "))
max_amount = float(input("Enter maximum amount (in AVAX token): "))
refuel_trigger = float(input("Threshold determining requires chain refuel or not (USD): "))

# Load data file with wallet IDs, addresses, and private keys
data_path = "Data\Raw_data.xlsx"
df = pd.read_excel(data_path)

# Extract ID, address, and private key from data file
ID = df['ID'].tolist()
addresses = df['Address'].tolist()
private_keys = df['Private_key'].tolist()


# Function to get a list of wallets that need refueling on each chain
def get_refuel_pool(df):
    # Initialize empty dictionary
    refuel_pool = {}

    # List of all chains excluding Ethereum
    chains = ["Arbitrum", "Optimism", "Fantom", "Avalanche", "BNB", "Polygon"]

    # Iterate over each wallet in data frame
    for i, row in df.iterrows():
        chains_to_refuel = []
        # Check each chain for low balance
        for chain in chains:
            # Convert balance to float
            balance_str = row[chain].replace(",", ".")
            try:
                balance = pd.to_numeric(balance_str, errors='coerce')
            except Exception as e:
                print(f"Error while parsing balance for chain {chain} ID {i}. Balance_str: {balance_str}. Error: {e}")
                continue
            # If balance is lower than refuel trigger, add to refuel list
            if balance < float(refuel_trigger):
                chains_to_refuel.append(chain)
        # If there are any chains to refuel, add to refuel pool
        if chains_to_refuel:
            refuel_pool[row['ID']] = chains_to_refuel
    return refuel_pool

# Function to transfer AVAX out of wallet
def out_of_AVAX(id, chain_name, config, addresses, private_keys):
    # Set up web3 connection to Avalanche blockchain (always use Avalanche for this)
    w3 = Web3(HTTPProvider(config['networks']['Avalanche']['url']))

    # Get wallet address and private key
    address = addresses[id]
    address_checksum = w3.to_checksum_address(address)
    private_key = private_keys[id]

    # Load account using private key
    account = w3.eth.account.from_key(private_key)

    # Load contract details from config
    contract_name = "contract_refuel_AVAX"
    contract_details = config['contracts'][contract_name]
    contract_address = w3.to_checksum_address(contract_details['address'])
    contract = w3.eth.contract(address=contract_address, abi=contract_details['abi'])

    # Calculate amount to transfer in Ether and convert to Wei
    payableAmount = random.uniform(min_amount, max_amount)
    payableAmountWei = Web3.to_wei(payableAmount, 'ether')

    # Get destination chain ID from config
    destinationChainId = config['networks'][chain_name]['id']

    estimated_gas = contract.functions.depositNativeToken(destinationChainId, address_checksum).estimate_gas({
        'from': account.address,
    })

    # Build transaction
    transaction = contract.functions.depositNativeToken(destinationChainId, address_checksum).build_transaction({
        'nonce': w3.eth.get_transaction_count(account.address),
        'gas': estimated_gas,
        'maxFeePerGas': w3.to_wei(35, 'nano'),
        'maxPriorityFeePerGas': w3.to_wei(1.5, 'nano'),
        'value': payableAmountWei
    })

    # Sign transaction using private key
    signed_txn = w3.eth.account.sign_transaction(transaction, private_key)

    # Send transaction and wait for receipt
    txn_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
    txn_receipt = w3.eth.wait_for_transaction_receipt(txn_hash)

    # Print success message and transaction hash
    if txn_receipt['status'] == 1:
        print(f"Successfully send {payableAmount} AVAX to chain {chain_name}")
        print(f"Transaction Hash: {txn_hash.hex()}")
    elif txn_receipt['status'] == 0:
        print("Transaction was unsuccessful. Up 'maxFeePerGas' or 'maxPriorityFeePerGas'")
        print(f"Transaction Hash: {txn_hash.hex()}")
    else:
        print("Unexpected status value.")

# Get refuel pool
refuel_pool = get_refuel_pool(df)

# Shuffle IDs to randomize order
id_list = list(refuel_pool.keys())
random.shuffle(id_list)

# Iterate over each wallet in refuel pool
for id in id_list:
    chains_to_refuel = refuel_pool[id]
    random.shuffle(chains_to_refuel)  # Shuffle the order of chains
    for chain_to_refuel in chains_to_refuel:
        print(f"Refueling chain {chain_to_refuel} for ID {id}")
        try:
            # Try to send transaction
            out_of_AVAX(id, chain_to_refuel, config, addresses, private_keys)
        except Exception as e:
            # If an error occurs, print error message
            print(f"Error while sending transaction for ID {id} on chain {chain_to_refuel}. Error: {e}")
        # Wait random time between transactions
        wait_time = random.uniform(min_delay, max_delay)
        print(f"Waiting {wait_time} second before next operation")
        time.sleep(wait_time)
#PERFORM BY @Palyanytsya & GPT4