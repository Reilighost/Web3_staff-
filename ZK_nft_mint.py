import random
import time
from web3 import Web3, HTTPProvider
import pandas as pd
import json
import datetime
from web3.middleware import geth_poa_middleware


with open("Json_staff/Config.JSON", 'r') as f:
    config = json.load(f)

min_delay = float(input("Enter minimum delay (in second) between transactions: "))
max_delay = float(input("Enter maximum delay (in second) between transactions: "))
max_trx = int(input("Enter the total number of transactions to perform per account: "))
address_delay = float(input("Enter delay (in hours) specific to each address: "))

# Load data file with wallet IDs, addresses, and private keys
file_path = "Data/Raw_data.xlsx"
transaction_count = "Data/TRX_count.xlsx"
df = pd.read_excel(file_path)
df2 = pd.read_excel(transaction_count)

# Extract ID, address, and private key from data file
ID = df['ID'].tolist()
addresses = df['Address'].tolist()
private_keys = df['Private_key'].tolist()
timestamp = df['Time_Stamp'].tolist()

def check_max_trx_reached(df2, max_trx):
    for value in df2['ZK_mint_total']:
        if value < max_trx:
            return False
    return True
def mint_greenfield(id, config, addresses, private_keys):
    w3 = Web3(HTTPProvider(config['networks']['BNB']['url']))
    w3.middleware_onion.inject(geth_poa_middleware, layer=0)
    address = addresses[id]
    address_checksum = w3.to_checksum_address(address)
    private_key = private_keys[id]
    account = w3.eth.account.from_key(private_key)
    contract_name = "Greenfield_nft"
    contract_details = config['contracts'][contract_name]
    contract_address = w3.to_checksum_address(contract_details['address'])
    contract = w3.eth.contract(address=contract_address, abi=contract_details['abi'])

    estimated_gas = contract.functions.mint().estimate_gas({
        'from': account.address,
    })

    gas_limit = int(estimated_gas * 1.05)
    gas_price_gwei = 3
    max_wei = gas_price_gwei * 1e9
    # Build transaction
    transaction = contract.functions.mint().build_transaction({
        'nonce': w3.eth.get_transaction_count(account.address),
        'gas': gas_limit,
        'gasPrice': int(max_wei),
    })
    # Sign transaction using private key
    signed_txn = w3.eth.account.sign_transaction(transaction, private_key)

    try:
        txn_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
        txn_receipt = w3.eth.wait_for_transaction_receipt(txn_hash)
    except ValueError:
        print("Insufficient funds for transaction.")
        return 0

    # Check the status field for success
    if txn_receipt['status'] == 1:
        print(f"Mint {contract_name} for ID:{id} was successful!")
        print(f"Transaction Hash: {txn_hash.hex()}")
        return 1
    elif txn_receipt['status'] == 0:
        print("Transaction was unsuccessful.")
        print(f"Transaction Hash: {txn_hash.hex()}")
        return 0
def mint_ZK_lite(id, config, addresses, private_keys):
    w3 = Web3(HTTPProvider(config['networks']['BNB']['url']))
    w3.middleware_onion.inject(geth_poa_middleware, layer=0)
    address = addresses[id]
    address_checksum = w3.to_checksum_address(address)
    private_key = private_keys[id]
    account = w3.eth.account.from_key(private_key)
    contract_name = "ZK_lite_nft"
    contract_details = config['contracts'][contract_name]
    contract_address = w3.to_checksum_address(contract_details['address'])
    contract = w3.eth.contract(address=contract_address, abi=contract_details['abi'])

    estimated_gas = contract.functions.mint().estimate_gas({
        'from': account.address,
    })

    gas_limit = int(estimated_gas * 1.05)
    gas_price_gwei = 3
    max_wei = gas_price_gwei * 1e9
    # Build transaction
    transaction = contract.functions.mint().build_transaction({
        'nonce': w3.eth.get_transaction_count(account.address),
        'gas': gas_limit,
        'gasPrice': int(max_wei),
    })
    # Sign transaction using private key
    signed_txn = w3.eth.account.sign_transaction(transaction, private_key)

    try:
        txn_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
        txn_receipt = w3.eth.wait_for_transaction_receipt(txn_hash)
    except ValueError:
        print("Insufficient funds for transaction.")
        return 0

    # Check the status field for success
    if txn_receipt['status'] == 1:
        print(f"Mint {contract_name} for ID:{id} was successful!")
        print(f"Transaction Hash: {txn_hash.hex()}")
        return 1
    elif txn_receipt['status'] == 0:
        print("Transaction was unsuccessful.")
        print(f"Transaction Hash: {txn_hash.hex()}")
        return 0
def mint_MainnetAlpha(id, config, addresses, private_keys):
    w3 = Web3(HTTPProvider(config['networks']['Polygon']['url']))
    w3.middleware_onion.inject(geth_poa_middleware, layer=0)
    address = addresses[id]
    address_checksum = w3.to_checksum_address(address)
    private_key = private_keys[id]
    account = w3.eth.account.from_key(private_key)
    contract_name = "MainnetAlpha_nft"
    contract_details = config['contracts'][contract_name]
    contract_address = w3.to_checksum_address(contract_details['address'])
    contract = w3.eth.contract(address=contract_address, abi=contract_details['abi'])

    estimated_gas = contract.functions.mint().estimate_gas({
        'from': account.address,
    })

    # Add 15% to the estimated gas
    gas_limit = int(estimated_gas * 1.05)
    max_gwei = random.uniform(260, 330)
    max_priority_gwei = random.uniform(33, 44)
    max_wei = max_gwei * 1e9
    max_priority_wei = max_priority_gwei * 1e9

    # Build transaction
    transaction = contract.functions.mint().build_transaction({
        'nonce': w3.eth.get_transaction_count(account.address),
        'gas': gas_limit,
        'maxFeePerGas': int(max_wei),
        'maxPriorityFeePerGas': int(max_priority_wei),
    })
    # Sign transaction using private key
    signed_txn = w3.eth.account.sign_transaction(transaction, private_key)

    try:
        txn_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
        txn_receipt = w3.eth.wait_for_transaction_receipt(txn_hash)
    except ValueError:
        print("Insufficient funds for transaction.")
        return 0

    # Check the status field for success
    if txn_receipt['status'] == 1:
        print(f"Mint {contract_name} for ID:{id} was successful!")
        print(f"Transaction Hash: {txn_hash.hex()}")
        return 1
    elif txn_receipt['status'] == 0:
        print("Transaction was unsuccessful.")
        print(f"Transaction Hash: {txn_hash.hex()}")
        return 0
def mint_BNBChainLubanUpgrade(id, config, addresses, private_keys):
    w3 = Web3(HTTPProvider(config['networks']['BNB']['url']))
    w3.middleware_onion.inject(geth_poa_middleware, layer=0)
    address = addresses[id]
    address_checksum = w3.to_checksum_address(address)
    private_key = private_keys[id]
    account = w3.eth.account.from_key(private_key)
    contract_name = "BNBChainLubanUpgrade_nft"
    contract_details = config['contracts'][contract_name]
    contract_address = w3.to_checksum_address(contract_details['address'])
    contract = w3.eth.contract(address=contract_address, abi=contract_details['abi'])

    estimated_gas = contract.functions.mint().estimate_gas({
        'from': account.address,
    })

    gas_limit = int(estimated_gas * 1.05)
    gas_price_gwei = 3
    max_wei = gas_price_gwei * 1e9
    # Build transaction
    transaction = contract.functions.mint().build_transaction({
        'nonce': w3.eth.get_transaction_count(account.address),
        'gas': gas_limit,
        'gasPrice': int(max_wei),
    })
    # Sign transaction using private key
    signed_txn = w3.eth.account.sign_transaction(transaction, private_key)

    try:
        txn_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
        txn_receipt = w3.eth.wait_for_transaction_receipt(txn_hash)
    except ValueError:
        print("Insufficient funds for transaction.")
        return 0

    # Check the status field for success
    if txn_receipt['status'] == 1:
        print(f"Mint {contract_name} for ID:{id} was successful!")
        print(f"Transaction Hash: {txn_hash.hex()}")
        return 1
    elif txn_receipt['status'] == 0:
        print("Transaction was unsuccessful.")
        print(f"Transaction Hash: {txn_hash.hex()}")
        return 0
def get_time_difference_in_hours(id, df):
    try:
        timestamp_str = str(df.at[id, 'Time_Stamp'])
        last_transaction_time = datetime.datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
        current_time = datetime.datetime.now()
        time_difference = current_time - last_transaction_time
        hours_passed = time_difference.total_seconds() / 3600
        print(f"Time difference in hours for ID {id}: {hours_passed}")
        return hours_passed
    except Exception as e:
        print(f"Error reading timestamp for ID {id}: {e}")
        return 99999
def update_excel_with_timestamp(id, transaction_count, df):
    try:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        df.at[id, 'Time_Stamp'] = timestamp
        df.to_excel(file_path, index=False)
        print(f"Updated timestamp for ID {id} to {timestamp}")
    except Exception as e:
        print(f"Error updating timestamp for ID {id}: {e}")

class BreakOuterLoop(Exception):
    pass
sleep_delay = 10
try:
    while True:
        # Randomize the order of IDs for each iteration of the loop
        random.shuffle(ID)
        eligible_id_found = False
        for id in ID:
            random.shuffle(ID)

            print(f"Processing ID {id}")
            total_trx = df2.at[id, 'ZK_mint_total']
            if total_trx >= max_trx:
                # print(f"Max transactions reached for ID: {id}. Skipping transaction.")
                continue
            if get_time_difference_in_hours(id, df) < address_delay:
                # print("Current delay have not passed for this account. Skipping transaction.")
                continue
            if check_max_trx_reached(df2, max_trx):
                print("Max transactions reached for all IDs. Stopping process...")
                raise BreakOuterLoop
            eligible_id_found = True
            sleep_delay = 10
            selected_func = random.choice([mint_greenfield, mint_ZK_lite, mint_MainnetAlpha, mint_BNBChainLubanUpgrade])
            try:
                result = selected_func(id, config, addresses, private_keys)
            except Exception as e:
                print(f"Error details: {str(e)}")
            if result > 0:
                df2.at[id, 'ZK_mint_total'] += 1
                update_excel_with_timestamp(id, transaction_count, df)
                slyp = random.uniform(min_delay, max_delay)
                print(f"Wait {slyp} second before next operation")
                df2.to_excel(transaction_count, index=False)
                time.sleep(slyp)
                sleep_delay = 10

        if not eligible_id_found:
            # If no eligible IDs were found in this iteration, increase the sleep delay
            sleep_delay *= 3.14
        print(f"No profile available for operation, Chill {sleep_delay} seconds before next check...")
        time.sleep(sleep_delay)

except BreakOuterLoop:
    print("Job is done, exit proces...")