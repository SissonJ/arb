import asyncio
import base64
import json
import time
from typing import Optional
from BotInfo import BotInfo
#from BotInfo import BotInfo
from env import testnet
from env import endpoint
from env import mkSeed
from env import mkSeed2
from secret_sdk.client.lcd.lcdclient import LCDClient
from secret_sdk.core.auth.data.tx import StdFee, StdSignMsg, StdTx
from secret_sdk.core.coins import Coins
from secret_sdk.key.key import Key
from secret_sdk.key.mnemonic import MnemonicKey
from secret_sdk.client.lcd.lcdclient import AsyncLCDClient
from secret_sdk.core.auth.data.tx import StdTx
#from utils import calculateProfitCP, constantProduct, getSiennaRatio, createMsgExecuteSienna
from miscreant.aes.siv import SIV
from datetime import datetime
import sys

#from BotInfo import BotInfo
from config import config as cfg
from utils import calculateProfit, generateTxEncryptionKeys, getSSwapRatio, getSiennaRatio, swapSienna, swapSswap, sync_next_block
#from utils import generateTxEncryptionKeys, sync_next_block, checkScrtBal, getSiennaRatio, getSSwapRatio 
#from utils import calculateProfit, swapSienna, swapSswap, recordTx
#from utils_async import getSSwapRatioAsync

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
  nonce = [1, 113, 36, 99, 111, 48, 190, 132, 166, 75, 26, 115, 242, 88, 128, 38, 92, 170, 158, 110, 144, 84, 199, 231, 50, 56, 235, 218, 199, 141, 108, 101]
  client = LCDClient(endpoint, 'secret-4')
  txKey = client.utils.get_tx_encryption_key(nonce)
  txResponse = {'height': 2694802, 'txhash': 'AC326DA80C96F834AC688B114A16DB521439204B65CB393CF1E3C745198D380D', 'raw_log': 'failed to execute message; message index: 0: encrypted: NhDWzAa0SwyBqYMTpiFPcOarHLFSkyZ4G7ZFgdRu/UjYi6wjXC3Qttzut8beioL3nFzzD11y6THgJ5kUA2AooZH56hUcrA5/hSU0t2W7diloYXB2vlIQgj0=: execute contract failed', 'gas_wanted': 200000, 'gas_used': 23852, 'logs': None, 'code': 3, 'codespace': 'compute'}
  print(txKey)
  raw_log = txResponse["raw_log"][txResponse["raw_log"].find("encrypted"):txResponse["raw_log"].find("contract")][11:-9]
  #print(raw_log == "NhDWzAa0SwyBqYMTpiFPcOarHLFSkyZ4G7ZFgdRu/UjYi6wjXC3Qttzut8beioL3nFzzD11y6THgJ5kUA2AooZH56hUcrA5/hSU0t2W7diloYXB2vlIQgj0=:")
  decoded_result = base64.b64decode("eVfUwZf26iX6am/49tLT0LLmYdvj78lvVQ0wqqLJNTi9UUlOgi4XNny/0F/Mv0E+ednw6yZcY5WahBdzy+pqt3xEogdJ1m+mTEQjCtzx1zyuuncCkiAtDY3iuySQ3EMT5IvOOZQ=")
  print(decoded_result)
  #siv = SIV(txKey)
  #decrypted = siv.open(encoded_result, [bytes()])
  decrypted = client.utils.decrypt(decoded_result, nonce, txKey)
  print(decrypted)
  print(json.loads(base64.b64decode(decrypted)))
  #print(encryptedBytes)

#decryptTxResponse()

def encrypt_decrypt():
  nonce = [249, 202, 181, 154, 152, 224, 174, 20, 235, 146, 3, 10, 113, 76, 153, 251, 111, 233, 51, 52, 135, 11, 168, 205, 152, 192, 169, 215, 175, 73, 90, 83]
  client = LCDClient(endpoint, 'secret-4')
  txKey = client.utils.get_tx_encryption_key(nonce)
  plaintext = bytes("I will encrypt and decrypt this", "utf-8")
  siv = SIV(txKey)
  ciphertext = siv.seal(plaintext, [bytes()])
  print(ciphertext)
  decrypt = siv.open(ciphertext, [bytes()])
  print(decrypt)

#encrypt_decrypt()

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

async def XgetSSwapRatioAsync(botInfo: BotInfo, nonce: Optional[int] = 0, tx_encryption_key: Optional[str] = ""):
  print("SSwap",nonce, tx_encryption_key, botInfo.pairContractAddresses["pair1"])
  sswapInfo = await botInfo.client.wasm.contract_query(
    botInfo.pairContractAddresses["pair1"], 
    botInfo.pairContractQueries["pair1"], 
    botInfo.pairContractHash["pair1"], 
    nonce, 
    tx_encryption_key,
  )
  if( botInfo.pairToken1First["pair1"] ):
    token1Amount = float(sswapInfo['assets'][0]['amount']) * 10**-botInfo.tokenDecimals["token1"]
    token2Amount = float(sswapInfo['assets'][1]['amount']) * 10**-botInfo.tokenDecimals["token2"]
  else:
    token1Amount = float(sswapInfo['assets'][1]['amount']) * 10**-botInfo.tokenDecimals["token1"]
    token2Amount = float(sswapInfo['assets'][0]['amount']) * 10**-botInfo.tokenDecimals["token2"]
  print(token1Amount/token2Amount, token1Amount, token2Amount)
  return token1Amount/token2Amount, token1Amount, token2Amount

async def getSiennaRatioAsync(botInfo: BotInfo, nonce: Optional[int] = 0, tx_encryption_key: Optional[str] = ""):
  siennaInfo = await botInfo.client.wasm.contract_query(
    botInfo.pairContractAddresses["pair2"], 
    botInfo.pairContractQueries["pair2"], 
    botInfo.pairContractHash["pair2"], 
    nonce, 
    tx_encryption_key
  )
  if(botInfo.pairToken1First["pair2"] ):
    token1Amount = float(siennaInfo['pair_info']['amount_0']) * 10**-botInfo.tokenDecimals["token1"]
    token2Amount = float(siennaInfo['pair_info']['amount_1']) * 10**-botInfo.tokenDecimals["token2"]
  else:
    token1Amount = float(siennaInfo['pair_info']['amount_1']) * 10**-botInfo.tokenDecimals["token1"]
    token2Amount = float(siennaInfo['pair_info']['amount_0']) * 10**-botInfo.tokenDecimals["token2"]
  print(token1Amount/token2Amount, token1Amount, token2Amount)
  return token1Amount/token2Amount, token1Amount, token2Amount

async def runAsyncQueries(botInfo, nonceDict, txEncryptionKeyDict):
  print("runQ", nonceDict["first"], txEncryptionKeyDict["first"])
  task1 = asyncio.create_task(getSSwapRatioAsync(botInfo, 0, ""))#, nonceDictQuery["first"], txEncryptionKeyDictQuery["first"])
  task2 = asyncio.create_task(getSiennaRatioAsync(botInfo, 0, ""))#, nonceDictQuery["second"], txEncryptionKeyDictQuery["second"])
  SSratio, SStoken1Amount, SStoken2Amount = await task1
  SIratio, SItoken1Amount, SItoken2Amount = await task2
  await botInfo.client.session.close()
  return SSratio, SIratio, SStoken1Amount, SItoken1Amount, SStoken2Amount, SItoken1Amount

async def oneRun():
  cfg[sys.argv[1]]["mkSeed"] = mkSeed

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
  print(difference)
  if( difference > 0):
    txResponse = await swapSswap(
      botInfo,
      .0001,
      firstSwap,
      secondSwap,
      nonceDict,
      txEncryptionKeyDict,
    )
  if(difference < 0):
    txResponse = await swapSienna(
      botInfo,
      .0001,
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
    #recordTx(botInfo, config[sys.argv[1]]["logLocation"], optimumAmountSwapping, (siennaRatio + sswapRatio)/2)
    nonceDict, txEncryptionKeyDict = generateTxEncryptionKeys(botInfo.client)
    botInfo.sequence = botInfo.wallet.sequence()
    scrtBal = int(botInfo.client.bank.balance(botInfo.accAddr).to_data()[0]["amount"]) * 10**-6
  nonceDictPair, txEncryptionKeyDictPair = generateTxEncryptionKeys(botInfo.client)
  keepLooping = False #set to false for only one run

#asyncio.run(oneRun())

async def decryptTry2():
  client = LCDClient(endpoint, "secret-4")
  data = "0A9A030A2A2F7365637265742E636F6D707574652E763162657461312E4D736745786563757465436F6E747261637412EB020AE80269D4D3899EE7E1F6DBED0CB810FE1CA7D42761CC66DE9CC3E6111FFED245F42696DF18558BD8BD71EC355134B1A716A39BBACB8B08BA94545E2CF782EF424A8F3289D517D9F5632F94003FA977796C80161017D2B82689E5C7D6B0864D9F6E2C592A420E856422A2ABFB2F302B2906737D3DC267EDCFFE1D69D9F557D2C1007C2912A58421AACB7EBDF57AF066EF345E39C19249F70D4B1219CE7B84FCE097D9EA8E7318DAFC14C78C0BE8E44350F31500973350E78B61A2482F8461495265DC11DB3E6446E04F736DC700F58D28BD2D5154B4B621B79CE3DD0F4FDE7962717D5FC3C62161C8677564ECF7E63D9DDAC33A074635889CB4E8F01F8ADD54BC62A972BA2491670208D60968F39CCDE31FD8EA9E0191DBA523D625867F7E0D4878894E924BD50327F97BD288E36F1F9544D3EA6B483105FC2C6E5CAF257CDA2CACF20BC7118F7F01E7BF2A824549384EC58C7F8DBF38BF76EB1A73F014CC60661D98C53B77AF710D7B630A9A030A2A2F7365637265742E636F6D707574652E763162657461312E4D736745786563757465436F6E747261637412EB020AE8021F95D3C46E65122C37E1C0FA8313C1487EA3E38FF2C472F9C268297BA3E065892F2788F0591D194927BFCF12112FF7A3CB173410941C3D9D6C0C5FD8160A73647A99BEF6A8D71EF015F612E75FE39D8C29F03F5CED6F625B95D3145277DEE7732D0AD1A1D06285605E0F161DBEC133EF4CF90FE54ABF00BE228D82B17ECCC9F8A78269555FD4A63C908C8A8B5FE4D6CCEAF682C273AE060E08428AA14E7D4850A972CE4686F4F5A5D887E79E8745B632F150F5277912A411D9030B608903D61DCC6F405AD6F0EE23061BE152A872D1CDA72A97538F44813EE81925C343AB41921A051F166D77E7E27E63589BACBE9BFBFF1F144D4B6A5BEB558B7B5683E9643BA99264DA30848439EB5CD1935F8AF5122B215820A37B22D94D0960376EB49FF21EC1875AF5E2AEA3C3DF8A67129133C0CDC2C2C84A3368B955EB809A431559A63AF66A301317D35AF71DEFDFED81B0711D6C07B37E9167C6E75A66DB427D02CB83288A021A44A763"
  nonces = [[223, 112, 119, 87, 169, 64, 52, 71, 195, 191, 8, 170, 51, 226, 80, 35, 193, 242, 219, 34, 184, 167, 219, 237, 205, 54, 229, 106, 146, 59, 157, 210],[211, 33, 151, 192, 229, 64, 198, 197, 121, 220, 250, 55, 48, 0, 31, 98, 65, 16, 95, 14, 190, 5, 251, 83, 31, 136, 65, 30, 129, 129, 187, 231] ]
  key1 = client.utils.get_tx_encryption_key(nonces[0])
  key1 = client.utils.get_tx_encryption_key(nonces[1])
  encreyted_bytes = base64.encode()
  res = await client.utils.decrypt_data_field(data, nonces)

  print(res)

asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
asyncio.run(decryptTry2())

def swapTest():
  print(endpoint)
  client = LCDClient(endpoint, "secret-4")
  wallet = client.wallet(MnemonicKey(mkSeed))
  print(wallet.account_number_and_sequence())
  msgSienna = json.dumps({"swap":{"to":None,"expected_return":"0"}})
  encryptedMsgSienna = str( base64.b64encode(msgSienna.encode("utf-8")), "utf-8")
  handleMsgSienna = { "send": {"recipient": "secret155ycxc247tmhwwzlzalakwrerde8mplhluhjct", "amount": "100", "msg": encryptedMsgSienna }}
  res = wallet.execute_tx("secret1k0jntykt7e4g3y88ltc60czgjuqdy4c9e8fzek", handleMsgSienna, "", [])
  print("stkdscrt to sscrt",res)
  #asyncio.sleep(6)
  #res = wallet.execute_tx("secret1k0jntykt7e4g3y88ltc60czgjuqdy4c9e8fzek", {"redeem":{"amount": "100"}}, "", [])
  #print("sscrt to scrt", res)
  #asyncio.sleep(6)
  #res = wallet.execute_tx("secret1k6u0cy4feepm6pehnz804zmwakuwdapm69tuc4", {"stake": {}}, "",Coins.from_str("100"+"uscrt"),gas=300000)
  #executeMsg = client.wasm.contract_execute_msg(wallet.key.acc_address, "secret1k6u0cy4feepm6pehnz804zmwakuwdapm69tuc4", {"stake": {}},Coins.from_str("10000"+"uscrt"))
  #stdSignMsg = StdSignMsg.from_data({
  #  "chain_id": "secret-4",
  #  "account_number": wallet.account_number(),
  #  "sequence": wallet.sequence(),
  #  "fee": StdFee(500001,"125000uscrt").to_data(),
  #  "msgs": [],
  #  "memo": "",
  #})

  #stdSignMsg.msgs = [executeMsg]
  #print(stdSignMsg)
  #tx = wallet.key.sign_tx(stdSignMsg)
  #res = client.tx.broadcast(tx)
  #print("scrt to stkdscrt", res)

#swapTest()

def queryTest():
  botInfo = BotInfo(cfg[sys.argv[1]])
  nonceDictQuery, txEncryptionKeyDictQuery = generateTxEncryptionKeys(botInfo.client)
  start = time.time()
  getSSwapRatio(botInfo, 0, "")#, nonceDictQuery["first"], txEncryptionKeyDictQuery["first"])
  getSiennaRatio(botInfo, 0, "")#, nonceDictQuery["second"], txEncryptionKeyDictQuery["second"])
  end = time.time()
  print(end - start)
  botInfo.client = AsyncLCDClient(endpoint, "secret-4")
  start = time.time()
  #asyncio.gather(
  #  getSSwapRatioAsync(botInfo, 0, ""),
  #  getSiennaRatioAsync(botInfo, 0, "")
  #)
  ob1 = asyncio.get_event_loop().run_until_complete(runAsyncQueries(botInfo, nonceDictQuery, txEncryptionKeyDictQuery))
  #ob2 = asyncio.get_event_loop().run_until_complete(runAsyncQueries(botInfo))
  end = time.time() 
  print(end - start)
  print(ob1)


#queryTest()

async def generateTxEncryptionKeysAsync(client: AsyncLCDClient):
  nonceDict = {"first":client.utils.generate_new_seed(), "second":client.utils.generate_new_seed()}
  txEncryptionKeyDict = {"first": await client.utils.get_tx_encryption_key(nonceDict["first"]), "second": await client.utils.get_tx_encryption_key(nonceDict["second"])}
  return nonceDict, txEncryptionKeyDict

async def asyncQuery():
  botInfo = BotInfo(cfg[sys.argv[1]])
  nonceDictQuery, txEncryptionKeyDictQuery = await generateTxEncryptionKeysAsync(botInfo.asyncClient)
  print(await getSSwapRatioAsync(botInfo, nonceDictQuery["first"], txEncryptionKeyDictQuery["first"]))
  return

#asyncio.run(asyncQuery())

def regQuery():
  botInfo = BotInfo(cfg[sys.argv[1]])
  nonceDictQuery, txEncryptionKeyDictQuery = generateTxEncryptionKeys(botInfo.client)
  print(getSSwapRatio(botInfo, nonceDictQuery["first"], txEncryptionKeyDictQuery["first"]))
  return

#regQuery()
#print(optimumSwapAmountStdk(319600, 310835.328445, 1.02))

def swap_simulation_for_gain_loss():
  controller = BotInfo(cfg["sscrt-shd-config"])
  print(controller.inv)

#swap_simulation_for_gain_loss()

def encryption_test():
  client = LCDClient(endpoint, "secret-4")
  print(client.utils.encrypt("20a015a72cb7892680814a88308b76275c06fec7ecc7c0bcd55d0f87ee071591", {"get_config":{}}))

#encryption_test()