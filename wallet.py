# Import dependencies
import subprocess
import json
import os
import dotenv

from dotenv import load_dotenv
from web3 import Web3
from eth_account import Account
from pathlib import Path
from getpass import getpass
from constants import *
from web3 import Web3
from bip_utils import Bip32, Bip39SeedGenerator, Bip44, Bip44Coins, Bip44Changes

from bit import PrivateKeyTestnet
from bit.network import NetworkAPI
from web3.middleware import geth_poa_middleware
from web3.gas_strategies.time_based import medium_gas_price_strategy


# Load and set environment variables
load_dotenv()
mnemonic = os.getenv("mnemonic")
numderive = 3
w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:8545"))

# Create a function called `derive_wallets`
def derive_wallets(mnemoic,coin,numderive):
    command = f' ./derive -g --mnemonic="{mnemonic}" --numderive="{numderive}" --coin="{coin}" --format=json' 
    p = subprocess.Popen(command,stdout=subprocess.PIPE,shell=True)
    output, err = p.communicate()
    p_status = p.wait()
    keys = json.loads(output)
    return keys

# Create a dictionary object called coins to store the output from `derive_wallets`.

coins = {"eth", "btc-test", "btc"}

keys = {}
for coin in coins:
    keys[coin]= derive_wallets(os.getenv('mnemonic'), coin, numderive)
    
eth_PrivateKey = keys["eth"][0]['privkey']
btc_PrivateKey = keys['btc'][0]['privkey']
btc_test_PrivateKey = keys['btc-test'][0]['privkey']


# Create a function called `priv_key_to_account` that converts privkey strings to account objects.

def priv_key_to_account(coin,priv_key):   #priv_key
    if coin == ETH:
        return Account.privateKeyToAccount(priv_key)
    if coin == BTCTEST:
        return PrivateKeyTestnet(priv_key)  
    
    
# Create a function called `create_tx` that creates an unsigned transaction appropriate metadata.

def create_tx(coin,account,recipient,amount): #account
    
    if coin ==ETH:    
        gasEstimate = w3.eth.estimateGas({"from":account.address,"to":recipient,"value":amount})
        return {
            
            "from": account.address,
            "to": to,
            "value": amount,
            "gasPrice": w3.eth.gasPrice,
            "gas": gasEstimate,
            "chainId": 999,
            "nonce" : w3.eth.getTransactionCount(account.address)
        }
    elif coin == BTCTEST:
        return PrivateKeyTestnet.prepare_transaction(account.address, [(recipient, amount, BTC)])
       
        
# Create a function called `send_tx` that calls `create_tx`, signs and sends the transaction.

def send_tx(account,recipient,amount):
    tx = create_raw_tx(account,recipient,amount)
    if coin == ETH:
        signed_txn = account.sign_transaction(tx)
        result = w3.eth.sendRawTransaction(signed_tx.rawTransaction)
       # print(result.hex())
        return result.hex()
    
    elif coin == BTCTEST:
        tx_btctest = create_tx(coin, account, recipient, amount)
        signed_tx = account.sign_transaction(tx)
       # print(signed_tx)
        return NetworkAPI.broadcast_tx_testnet(signed_tx)
    return result.hex()