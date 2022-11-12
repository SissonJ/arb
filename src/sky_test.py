import asyncio
import time
from secret_sdk.client.lcd.lcdclient import LCDClient
from env import endpoint, mkSeed2
from secret_sdk.client.lcd.wallet import Wallet
from secret_sdk.key.mnemonic import MnemonicKey

SWAP_AMOUNT = "5000000000"

SKY_ADDR = 'secret1axw6cl0sg7htg8klpnnr88hvyhlw40tfrwsa98'
SKY_HASH = '20a015a72cb7892680814a88308b76275c06fec7ecc7c0bcd55d0f87ee071591'
SKY_QUERY = {"is_cycle_profitable":{"amount":SWAP_AMOUNT, "index":"0"}}
SKY_HANDLE = {"arb_cycle":{"amount":SWAP_AMOUNT, "index":"0"}}

def main():
    client = LCDClient(endpoint, 'secret-4')
    nonce_q = client.utils.generate_new_seed()
    encryption_key_q = client.utils.get_tx_encryption_key(nonce_q)
    wallet = Wallet(client, MnemonicKey(mnemonic=mkSeed2))
    last_profit = 0

    while True:
        try:
            res = client.wasm.contract_query(SKY_ADDR, SKY_QUERY, SKY_HASH, nonce_q, encryption_key_q )
            profit = (int(res["is_cycle_profitable"]["swap_amounts"][2]) - int(SWAP_AMOUNT))*10**-8
            if not last_profit == profit:
                print(time.time(), "\t", profit)
                last_profit = profit
            if profit > 0:      
                res = wallet.execute_tx(SKY_ADDR, SKY_HANDLE)
                print(res)
        except Exception as e:
            print(e)

main()