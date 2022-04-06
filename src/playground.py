import asyncio
import base64
import json
from BotInfo import BotInfo
from env import testnet
from env import endpoint
from env import mkSeed
from env import mkSeed2
from secret_sdk.client.lcd.lcdclient import LCDClient
from secret_sdk.core.auth.data.tx import StdFee, StdSignMsg, StdTx
from secret_sdk.core.coins import Coins
from secret_sdk.key.key import Key
from secret_sdk.key.mnemonic import MnemonicKey
from utils import calculateProfitCP, constantProduct, getSiennaRatio, createMsgExecuteSienna
from miscreant.aes.siv import SIV
from datetime import datetime
import sys

from BotInfo import BotInfo
from config import config as cfg
from utils import generateTxEncryptionKeys, sync_next_block, checkScrtBal, getSiennaRatio, getSSwapRatio 
from utils import calculateProfit, swapSienna, swapSswap, recordTx

config = {
  "mkSeed": mkSeed,
  "pairAddrs": {
    "pair1": "secret1qnpz5n6uq8dhfkpmld2yxgaff4p27qps7maja5", #SSWAP_SSCRT_SIENNA_PAIR
    "pair2": "secret1qnpz5n6uq8dhfkpmld2yxgaff4p27qps7maja5", #SIENNA_SSCRT_SIENNA_PAIR
  },
  "pairQueries": {
    "pair1": { 'pool': {} }, #SSWAP_QUERY
    "pair2": 'pair_info', #SIENNA_QUERY
  },
  "token1First": {
    "pair1": True,
    "pair2": False,
  },
  "tokenAddrs": {
    "token1": "secret18vd8fpwxzck93qlwghaj6arh4p7c5n8978vsyg", #SSCRT_ADDRESS
    "token2": "secret12vy64457jysxf3x4hwr64425ztlauq98zchpgt", #SIENNA_ADDRESS
  },
  "tokenKeys":{
    "token1": "api_key_3wPSbtuDquKHhFw1zSFILDXnQnsGz2TuISVAnlmUgYU=", #SSCRT_API_KEY
    "token2": "api_key_IiGUpxiB9+hry8VNpAx+6C9x72Tz1KEkhvAWtpLQUUU=", #SIENNA_API_KEY
  },
  "tokenDecimals":{
    "token1": 6,
    "token2": 18,
  },
  "clientInfo": {
    "endpoint": testnet,
    "chainID": "pulsar-2"
  },
  "logLocation": "./../logs/sscrt-sienna-csv.csv",
  "fee": {
    "gas": 200001,
    "price": "050001uscrt",
  },
}


def decryptTxResponse():
  nonce = [232, 29, 21, 200, 12, 194, 1, 32, 153, 211, 211, 216, 90, 229, 205, 148, 122, 101, 224, 148, 179, 186, 47, 86, 16, 197, 94, 34, 103, 17, 227, 50]
  client = LCDClient(endpoint, 'secret-4')
  txKey = client.utils.get_tx_encryption_key(nonce)
  txResponse = {'height': 2694802, 'txhash': 'AC326DA80C96F834AC688B114A16DB521439204B65CB393CF1E3C745198D380D', 'raw_log': 'failed to execute message; message index: 0: encrypted: NhDWzAa0SwyBqYMTpiFPcOarHLFSkyZ4G7ZFgdRu/UjYi6wjXC3Qttzut8beioL3nFzzD11y6THgJ5kUA2AooZH56hUcrA5/hSU0t2W7diloYXB2vlIQgj0=: execute contract failed', 'gas_wanted': 200000, 'gas_used': 23852, 'logs': None, 'code': 3, 'codespace': 'compute'}
  raw_log = txResponse["raw_log"][txResponse["raw_log"].find("encrypted"):txResponse["raw_log"].find("contract")][11:-9]
  #print(raw_log == "NhDWzAa0SwyBqYMTpiFPcOarHLFSkyZ4G7ZFgdRu/UjYi6wjXC3Qttzut8beioL3nFzzD11y6THgJ5kUA2AooZH56hUcrA5/hSU0t2W7diloYXB2vlIQgj0=:")
  encoded_result = base64.b64decode(bytes("ECHs8TkQv7RqpAHGSZ/7Dq2aA1k4zxp6EwQWUZRsl82ywchWLESNk5RXDloMu8Tf96S5gnIYGQ/9jeVagrxc0eTJrAgMsq99jBgBEfk4ewzIC4gEH/G9dgE=:", "utf-8"))
  siv = SIV(txKey)
  decrypted = siv.open(encoded_result, [bytes()])
  #decrypted = asyncio.get_event_loop().run_until_complete(client.utils.decrypt_data_field(hex(int(raw_log,16)), nonce) )
  print(json.loads(base64.b64decode(decrypted)))
  #print(encryptedBytes)

#decryptTxResponse()

def main():
  controller = BotInfo(config)
  ratio, sscrtAmount, shdAmount = getSiennaRatio(controller)
  print(sscrtAmount, shdAmount)
  print(round(constantProduct(shdAmount, sscrtAmount, 1*.997)*10**18))
  expectedAmount = str(round(constantProduct(shdAmount, sscrtAmount, 1*.997)*10**18))
  print(expectedAmount)
  msgSienna = json.dumps({"swap":{"to":None,"expected_return":"0"}})
  encryptedMsgSienna = str( base64.b64encode(msgSienna.encode("utf-8")), "utf-8")
  handleMsgSienna = { "send": {"recipient": controller.pairContractAddresses["pair2"], "amount": "1000000", "msg": encryptedMsgSienna }}
  print("incoming")
  res = controller.wallet.execute_tx(
    controller.tokenContractAddresses["token1"],
    handleMsgSienna,
    "",
    [],
  )
  print(res.to_data())
  msgSienna = json.dumps({"swap":{"to":None,"expected_return":"0"}})
  encryptedMsgSienna = str( base64.b64encode(msgSienna.encode("utf-8")), "utf-8")
  handleMsgSienna = { "send": {"recipient": controller.pairContractAddresses["pair2"], "amount": str(expectedAmount), "msg": encryptedMsgSienna }}
  print("incoming")
  res = controller.wallet.execute_tx(
    controller.tokenContractAddresses["token2"],
    handleMsgSienna,
    "",
    [],
  )
  print(res.to_data())
  #decryptTxResponse(res)

#main()

def factoryQuery():
  client = LCDClient(endpoint, 'secret-4')
  codeHash = client.wasm.contract_hash("secret1zvk7pvhtme6j8yw3ryv0jdtgg937w0g0ggu8yy")
  res = client.wasm.contract_info("secret1zvk7pvhtme6j8yw3ryv0jdtgg937w0g0ggu8yy")
  print(res)
  res = client.wasm.contract_query(
    "secret1zvk7pvhtme6j8yw3ryv0jdtgg937w0g0ggu8yy",
    {"list_exchanges":{"pagination":{"start":1,"limit":10}}},
    codeHash
  )
  print(res)
#factoryQuery()

def swapSimulation():
  client = LCDClient(endpoint, 'secret-4')
  res = client.wasm.contract_query(
    "secret1drm0dwvewjyy0rhrrw485q4f5dnfm6j25zgfe5",
    {"swap_simulation":{"offer":{"custom_token":{"contract_addr":"secret1k0jntykt7e4g3y88ltc60czgjuqdy4c9e8fzek", "token_contract_hash":client.wasm.contract_hash("secret1k0jntykt7e4g3y88ltc60czgjuqdy4c9e8fzek")},"amount":1000000}}}
  )
  print(res)
#swapSimulation()

def oneRun():
  cfg[sys.argv[1]]["mkSeed"] = mkSeed2

  botInfo = BotInfo(cfg[sys.argv[1]])

  nonceDict, txEncryptionKeyDict = generateTxEncryptionKeys(botInfo.client)
  nonceDictPair, txEncryptionKeyDictPair = generateTxEncryptionKeys(botInfo.client)

  scrtBal, sscrtBal, shdBal, lastSscrtBal = 0, 0, 0, 0
  keepLooping = True
  txResponse = ""
  runningProfit = 0
  minAmountSwapping = 1 #sscrt
  maxAmountSwapping = 500
  optimumAmountSwapping = 0
  height = 0
  lastHeight = 0
  lastProfit = 0
  gasFeeScrt = (int(botInfo.fee.to_data()["gas"])/4000000)*2.5
  scrtBal = int(botInfo.client.bank.balance(botInfo.accAddr).to_data()[0]["amount"]) * 10**-6
  print("Starting loop", sys.argv[1])
  height = sync_next_block(botInfo.client, lastHeight)
  txResponse = ""
  lastSscrtBal = sscrtBal
  #checkScrtBal(botInfo, scrtBal, maxAmountSwapping, config[sys.argv[1]]["logLocation"])
  sswapRatio, sswapt1, sswapt2 = getSSwapRatio(botInfo, nonceDictPair["first"], txEncryptionKeyDictPair["first"])
  siennaRatio, siennat1, siennat2 = getSiennaRatio(botInfo, nonceDictPair["second"], txEncryptionKeyDictPair["second"])
  difference = siennaRatio - sswapRatio 
  profit= firstSwap = secondSwap = 0
  if( difference > 0 ):
    optimumAmountSwapping, profit, firstSwap, secondSwap = calculateProfit(
      sswapt2, sswapt1, siennat2, siennat1, minAmountSwapping, gasFeeScrt)
  if( difference < 0 ):
    optimumAmountSwapping, profit, firstSwap, secondSwap = calculateProfit(
      siennat2, siennat1, sswapt2, sswapt1, minAmountSwapping, gasFeeScrt)
  if(profit != lastProfit):
    print(datetime.now(), "  height:", height, "  profit:", profit)
  lastProfit = profit
  if(height != lastHeight + 1 and lastHeight != 0):
    print(datetime.now(), "blocks skipped:", height - lastHeight)
  lastHeight = height
  if(difference > 0):
    txResponse = swapSswap(
      botInfo,
      10,
      firstSwap,
      secondSwap,
      nonceDict,
      txEncryptionKeyDict,
    )
  if(difference < 0):
    txResponse = swapSienna(
      botInfo,
      10,
      firstSwap,
      secondSwap,
      nonceDict,
      txEncryptionKeyDict,
    )
  if( txResponse != ""):
    if(not txResponse or txResponse.is_tx_error()):
      print(datetime.now(), "Failed")
    else:
      runningProfit += profit
      print(datetime.now(), "Success! Running profit:", runningProfit)
    recordTx(botInfo, config[sys.argv[1]]["logLocation"], optimumAmountSwapping, (siennaRatio + sswapRatio)/2)
    nonceDict, txEncryptionKeyDict = generateTxEncryptionKeys(botInfo.client)
    botInfo.sequence = botInfo.wallet.sequence()
    scrtBal = int(botInfo.client.bank.balance(botInfo.accAddr).to_data()[0]["amount"]) * 10**-6
  nonceDictPair, txEncryptionKeyDictPair = generateTxEncryptionKeys(botInfo.client)
  keepLooping = True #set to false for only one run

#oneRun()

def swapTest():
  res = ""
  client = LCDClient(endpoint, "secret-4")
  wallet = client.wallet(MnemonicKey(mkSeed))
  print(wallet.account_number_and_sequence())
  msgSienna = json.dumps({"swap":{"to":None,"expected_return":"0"}})
  encryptedMsgSienna = str( base64.b64encode(msgSienna.encode("utf-8")), "utf-8")
  handleMsgSienna = { "send": {"recipient": "secret155ycxc247tmhwwzlzalakwrerde8mplhluhjct", "amount": "100", "msg": encryptedMsgSienna }}
  #res = wallet.execute_tx("secret1k0jntykt7e4g3y88ltc60czgjuqdy4c9e8fzek", handleMsgSienna, "", [])
  print("stkdscrt to sscrt",res)
  #asyncio.sleep(6)
  #res = wallet.execute_tx("secret1k0jntykt7e4g3y88ltc60czgjuqdy4c9e8fzek", {"redeem":{"amount": "100"}}, "", [])
  print("sscrt to scrt", res)
  #asyncio.sleep(6)
  #res = wallet.execute_tx("secret1k6u0cy4feepm6pehnz804zmwakuwdapm69tuc4", {"stake": {}}, "",Coins.from_str("100"+"uscrt"),gas=300000)
  executeMsg = client.wasm.contract_execute_msg(wallet.key.acc_address, "secret1k6u0cy4feepm6pehnz804zmwakuwdapm69tuc4", {"stake": {}},Coins.from_str("10000"+"uscrt"))
  stdSignMsg = StdSignMsg.from_data({
    "chain_id": "secret-4",
    "account_number": wallet.account_number(),
    "sequence": wallet.sequence(),
    "fee": StdFee(500001,"125000uscrt").to_data(),
    "msgs": [],
    "memo": "",
  })

  stdSignMsg.msgs = [executeMsg]
  print(stdSignMsg)
  tx = wallet.key.sign_tx(stdSignMsg)
  res = client.tx.broadcast(tx)
  print("scrt to stkdscrt", res)

swapTest()


