import base64
import json
import time
from secret_sdk.client.lcd.lcdclient import LCDClient
from secret_sdk.core.auth.data.tx import StdFee, StdSignMsg
from secret_sdk.core.coin import Coin
from secret_sdk.key.mnemonic import MnemonicKey
from env import endpoint
from secret_sdk.key.raw import RawKey


def encryption_test():
  privkey_seed = [93, 148, 94, 235, 139, 187, 191, 197, 127, 54, 210, 113, 209, 160, 73, 132, 44, 26, 39, 166, 129, 226, 178, 176, 185, 182, 24, 89, 11, 244, 21, 130]
  client = LCDClient(endpoint, "secret-4", privkey_seed)
  key = RawKey(bytes(privkey_seed))
  tx = StdSignMsg.from_data({
    "chain_id": "secret_4",
    "account_number": 1,
    "fee": {"gas":"100", "amount":[{"amount":"1000","denom":"scrt"}]},
    "sequence": 1,
    "msgs": [],
    "memo": "",
  })
  tx = key.sign_tx(tx)
  client.tx.broadcast(tx)

#encryption_test()

def msg():
  privkey_seed = [93, 148, 94, 235, 139, 187, 191, 197, 127, 54, 210, 113, 209, 160, 73, 132, 44, 26, 39, 166, 129, 226, 178, 176, 185, 182, 24, 89, 11, 244, 21, 130]
  client = LCDClient(endpoint, "secret-4", privkey_seed)
  msgSienna = json.dumps({"swap":{"expected_return":"0"}})
  print(msgSienna)
  encryptedMsgSienna = str( base64.b64encode('{"swap":{"expected_return":"0"}}'.encode("utf-8")), "utf-8")
  handleMsgSienna = { "send": {"recipient": "secret1axw6cl0sg7htg8klpnnr88hvyhlw40tfrwsa98", "amount": "0", "msg": encryptedMsgSienna }}
  msgExecuteSienna = client.wasm.contract_execute_msg("secret1axw6cl0sg7htg8klpnnr88hvyhlw40tfrwsa98", "secret1axw6cl0sg7htg8klpnnr88hvyhlw40tfrwsa98", handleMsgSienna, [], contract_code_hash=None, nonce=privkey_seed)
  print(msgExecuteSienna.to_json())

#msg()

#def query_time():
#  task1 = asyncio.create_task(getSiennaRatioAsync(botInfo, nonceDict["first"], txEncryptionKeyDict["first"]))
#  task2 = asyncio.create_task(getSiennaRatioAsync(botInfo, nonceDict["second"], txEncryptionKeyDict["second"]))
#  sswapRatio, sswapt1, sswapt2 = await task1
#  siennaRatio, siennat1, siennat2 = await task2
#  return sswapRatio, sswapt1, sswapt2, siennaRatio, siennat1, siennat2

def query_test():
  privkey_seed = [93, 148, 94, 235, 139, 187, 191, 197, 127, 54, 210, 113, 209, 160, 73, 132, 44, 26, 39, 166, 129, 226, 178, 176, 185, 182, 24, 89, 11, 244, 21, 130]
  client = LCDClient(endpoint, "secret-4", privkey_seed)
  query, height = client.wasm.contract_query("secret1axw6cl0sg7htg8klpnnr88hvyhlw40tfrwsa98", {"get_config":{}})
  start_time = time.time()
  query, height = client.wasm.contract_query("secret1axw6cl0sg7htg8klpnnr88hvyhlw40tfrwsa98", {"get_config":{}}, height=int(height)+1)
  print("t1: ", time.time() - start_time)
  start_time = time.time()
  query, height = client.wasm.contract_query("secret1axw6cl0sg7htg8klpnnr88hvyhlw40tfrwsa98", {"get_config":{}}, height=int(height)+1)
  print("t2: ", time.time() - start_time)



#query_test()
