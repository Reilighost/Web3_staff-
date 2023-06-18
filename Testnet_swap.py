# Import necessary libraries
import random
import time
from web3 import Web3, HTTPProvider
import pandas as pd
import json

# Open configuration file
with open("Json_staff\\Config.JSON", 'r') as f:
    config = json.load(f)

# Accept user input for various parameters related to transactions
min_delay = float(input("Enter minimum delay between transaction: "))
max_delay = float(input("Enter maximum delay between transaction: "))
min_amount = float(input("Enter minimum amount (in ETH token): "))
max_amount = float(input("Enter maximum amount (in ETH token): "))
max_trx = int(input("Enter the maximum number of transactions: "))
max_iterations = int(input("Set a maximum number of loop iteration: "))

# Load data files containing wallet IDs, addresses, private keys, and transaction counts
file_path = "Data\\Raw_data.xlsx"
transaction_count = "Data\\TRX_count.xlsx"
df = pd.read_excel(file_path)
df2 = pd.read_excel(transaction_count)

# Extract wallet IDs, addresses, and private keys from the data file
ID = df['ID'].tolist()
addresses = df['Address'].tolist()
private_keys = df['Private_key'].tolist()


# Define a function to check if the maximum number of transactions has been reached for any wallet
def check_max_trx_reached(df2, max_trx):
    for value in df2['Testnet_Total']:
        if value < max_trx:
            return False
    return True


# Define a function to perform a swap and bridge transfer on the Optimism network
def out_of_OPT(id, config, addresses, private_keys):
    # Initialize a web3 instance for the Optimism network
    w3 = Web3(HTTPProvider(config['networks']['Optimism']['url']))

    # Get the wallet address, convert it to checksum format, and load the private key
    address = addresses[id]
    address_checksum = w3.to_checksum_address(address)
    private_key = private_keys[id]
    account = w3.eth.account.from_key(private_key)

    # Load contract details from the configuration file
    contract_name = "contract_testnet_OPT"
    contract_details = config['contracts'][contract_name]
    contract_address = w3.to_checksum_address(contract_details['address'])
    contract = w3.eth.contract(address=contract_address, abi=contract_details['abi'])

    # Calculate the amounts for the transaction
    payableAmount1 = random.uniform(min_amount, max_amount)
    payableAmountWei1 = Web3.to_wei(payableAmount1, 'ether')
    payableAmount2 = (payableAmount1 + 0.00018)
    payableAmountWei2 = Web3.to_wei(payableAmount2, 'ether')
    amountOutMin = random.uniform(2, 2.1)
    amountOutMin1 = Web3.to_wei(amountOutMin, 'ether')

    # Set up other parameters for the transaction
    dstChainId = 154
    to = address_checksum
    refundAddress = address_checksum
    zroPaymentAddress = "0x0000000000000000000000000000000000000000"
    adapterParams = b''

    # Build the transaction
    transaction = contract.functions.swapAndBridge(payableAmountWei1, amountOutMin1, dstChainId, to, refundAddress,
                                                   zroPaymentAddress, adapterParams).build_transaction({
        'nonce': w3.eth.get_transaction_count(account.address),
        'gas': 400000,
        'gasPrice': 1000000,
        'value': payableAmountWei2
    })

    # Sign the transaction using the wallet's private key
    signed_txn = w3.eth.account.sign_transaction(transaction, private_key)

    # Send the transaction and wait for it to be mined
    txn_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
    txn_receipt = w3.eth.wait_for_transaction_receipt(txn_hash)

    # Check if the transaction was successful
    if txn_receipt['status'] == 1:
        print(f"Transaction out of OPT was successful, value = {payableAmount2}")
        print(f"Transaction Hash: {txn_hash.hex()}")
        return 1
    elif txn_receipt['status'] == 0:
        print("Transaction was unsuccessful.")
        print(f"Transaction Hash: {txn_hash.hex()}")
        return 0

# Define a function to perform a swap and bridge transfer on the Arbitrum network
# This function is very similar to the previous one, but it interacts with the Arbitrum network instead
def out_of_ARB(id, config, addresses, private_keys):
    # Set up web3 connection to Arbitrum blockchain
    w3 = Web3(HTTPProvider(config['networks']['Arbitrum']['url']))

    # Get wallet address and private key
    address = addresses[id]
    address_checksum = w3.to_checksum_address(address)
    private_key = private_keys[id]

    # Load account using private key
    account = w3.eth.account.from_key(private_key)
    mim = 2
    notmim = 2.1
    # Load contract details from config
    contract_name = "contract_testnet_ARB"
    contract_details = config['contracts'][contract_name]
    contract_address = w3.to_checksum_address(contract_details['address'])
    contract = w3.eth.contract(address=contract_address, abi=contract_details['abi'])

    payableAmount1 = random.uniform(min_amount, max_amount)
    payableAmountWei1 = Web3.to_wei(payableAmount1, 'ether')
    payableAmount2 = (payableAmount1 + 0.00018)
    payableAmountWei2 = Web3.to_wei(payableAmount2, 'ether')
    amountOutMin = random.uniform(mim, notmim)
    amountOutMin1 = Web3.to_wei(amountOutMin, 'ether')
    dstChainId = 154
    to = address_checksum
    refundAddress = address_checksum
    zroPaymentAddress = "0x0000000000000000000000000000000000000000"
    adapterParams = b''
    max_fee_gwei = 0.135
    max_fee_wei = int(max_fee_gwei * (10 ** 9))


    # Build transaction
    transaction = contract.functions.swapAndBridge(payableAmountWei1, amountOutMin1, dstChainId, to, refundAddress, zroPaymentAddress, adapterParams).build_transaction({
        'nonce': w3.eth.get_transaction_count(account.address),
        'gas': 4000000,
        'maxFeePerGas': max_fee_wei,
        'value': payableAmountWei2
    })
    signed_txn = w3.eth.account.sign_transaction(transaction, private_key)

    txn_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
    txn_receipt = w3.eth.wait_for_transaction_receipt(txn_hash)

    if txn_receipt['status'] == 1:
        print(f"Transaction out ARB was successful, value = {payableAmount2}")
        print(f"Transaction Hash: {txn_hash.hex()}")
        return 1
    elif txn_receipt['status'] == 0:
        print("Transaction was unsuccessful.")
        print(f"Transaction Hash: {txn_hash.hex()}")
        return 0

random.shuffle(ID)
counter = 0
for id in ID:
    print(f"Processing ID {id}")
    total_trx = df2.at[id, 'Testnet_Total']
    if total_trx >= max_trx:
        print(f"Max transactions reached for ID: {id}. Skipping transaction.")
        continue
    if check_max_trx_reached(df2, max_trx):
        print("Max transactions reached for all IDs. Stopping process...")
        break
    selected_func = random.choice([out_of_OPT, out_of_ARB])
    if selected_func == out_of_OPT:
        result = out_of_OPT(id, config, addresses, private_keys)
        current_value = df2.at[id, 'Testnet_OPT']
        df2.at[id, 'Testnet_OPT'] = current_value + result
        if result > 0:
            df2.at[id, 'Testnet_Total'] += 1
    else:
        result = out_of_ARB(id, config, addresses, private_keys)
        current_value = df2.at[id, 'Testnet_ARB']
        df2.at[id, 'Testnet_ARB'] = current_value + result
        if result > 0:
            df2.at[id, 'Testnet_Total'] += 1
    df2.to_excel(transaction_count, index=False)
    counter += 1
    # Break the outer loop if we've reached the desired number of iterations
    if counter >= max_iterations:
        print(f"Desired number of iterations reached. Stopping process...")
        break
    sleep = (random.uniform(min_delay, max_delay))
    print(f"Wait {sleep} second before next operation")
    time.sleep(sleep)
#PERFORM BY @Palyanytsya & GPT4