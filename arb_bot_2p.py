import csv
import time
from datetime import datetime
import json
import base64

from BotInfo import BotInfo

from secret_sdk.client.lcd import LCDClient
from secret_sdk.core.auth.data.tx import StdFee, StdSignMsg
from secret_sdk.key.mnemonic import MnemonicKey
from secret_sdk.client.lcd.wallet import Wallet

botConfig = {
  "mkSeed": "MNEMONIC",
  "pairAddrs": {
    "pair1": "secret1wwt7nh3zyzessk8c5d98lpfsw79vzpsnerj6d0", #SSWAP_SSCRT_SHD_PAIR
    "pair2": "secret1drm0dwvewjyy0rhrrw485q4f5dnfm6j25zgfe5", #SIENNA_SSCRT_SHD_PAIR
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
    "token1": "secret1k0jntykt7e4g3y88ltc60czgjuqdy4c9e8fzek", #SSCRT_ADDRESS
    "token2": "secret1qfql357amn448duf5gvp9gr48sxx9tsnhupu3d", #SHD_ADDRESS
  },
  "tokenDecimals":{
    "token1": 6,
    "toekn2": 8,
  },
  "clientInfo": {
    "endpoint": "https://lcd.secret.llc",
    "chainID": "secret-4"
  },
  "logLocation": "shd-scrt-pair-log.csv",
  "fee": {
    "gas": 200001,
    "price": "050001uscrt",
  },
}

SSCRT_ADDRESS = 'secret1k0jntykt7e4g3y88ltc60czgjuqdy4c9e8fzek'
SSCRT_KEY = 'api_key_nE9AgouX7GVnT0+3LhAGoNmwUZ7HHRR4sUxNB+tbWW4='

def block_height(client:LCDClient):
  block_info = client.tendermint.block_info()
  height = block_info['block']['header']['height']
  return int(height)

def sync_next_block(client:LCDClient, height=0):
  while True:
    new_height = block_height(client)
    if new_height > height:
      return new_height
    time.sleep(.5)

def buyScrt(botInfo: BotInfo, scrtBal):
  global SSCRT_ADDRESS, SSCRT_KEY
  sscrtBalRes = botInfo.client.wasm.contract_query(SSCRT_ADDRESS, { "balance": { "address": botInfo.accAddr, "key": SSCRT_KEY }})
  redeemAmount = int(sscrtBalRes['balance']['amount']) - scrtBal * 10 ** 6
  handleMsg = {"redeem":{"amount":str(redeemAmount)}}
  res = botInfo.wallet.execute_tx(SSCRT_ADDRESS, handleMsg)
  return res

def checkScrtBal(botInfo: BotInfo, scrtBal, tradeAmount):
  if (scrtBal < 1 ):
    print("NOT ENOUGH SCRT")
    buyScrt(botInfo, tradeAmount)
    return 
  return

#THESE ARE GOING TO NEED WORK

def getSSwapRatio(botInfo: BotInfo):
  sswapInfo = botInfo.client.wasm.contract_query(botInfo.pairContractAddresses["pair1"], botInfo.pairContractQueries["pair1"])
  if( botInfo.pairToken1First["pair1"] ):
    token1Amount = float(sswapInfo['assets'][0]['amount']) * 10**-botInfo.tokenDecimals["token1"]
    token2Amount = float(sswapInfo['assets'][1]['amount']) * 10**-botInfo.tokenDecimals["token2"]
  else:
    token1Amount = float(sswapInfo['assets'][1]['amount']) * 10**-botInfo.tokenDecimals["token1"]
    token2Amount = float(sswapInfo['assets'][0]['amount']) * 10**-botInfo.tokenDecimals["token2"]
  return token1Amount/token2Amount, token1Amount, token2Amount

def getSiennaRatio(botInfo: BotInfo):
  siennaInfo = botInfo.client.wasm.contract_query(botInfo.pairContractAddresses["pair2"], botInfo.pairContractQueries["pair2"])
  if(botInfo.pairToken1First["pair1"] ):
    token1Amount = float(siennaInfo['pair_info']['amount_0']) * 10**-botInfo.tokenDecimals["token1"]
    token2Amount = float(siennaInfo['pair_info']['amount_1']) * 10**-botInfo.tokenDecimals["token2"]
  else:
    token1Amount = float(siennaInfo['pair_info']['amount_1']) * 10**-botInfo.tokenDecimals["token1"]
    token2Amount = float(siennaInfo['pair_info']['amount_0']) * 10**-botInfo.tokenDecimals["token2"]
  return token1Amount/token2Amount, token1Amount, token2Amount

def constantProduct(poolBuy, poolSell, x):
  out = -(poolBuy * poolSell)/(poolSell + x) + poolBuy
  return out

def calculateProfitCP(s1t2, s1t1, s2t2, s2t1, amountSwapped, gasFeeScrt):
  firstSwap = constantProduct(s1t2, s1t1, amountSwapped*.996)
  secondSwap = constantProduct(s2t1, s2t2, firstSwap*.997) * .999

  profit = secondSwap - amountSwapped - gasFeeScrt
  return profit, firstSwap, secondSwap 

def broadcastTx(botInfo: BotInfo, msgExecuteFirst, msgExecuteSecond):

  stdSignMsg = StdSignMsg.from_data({
    "chain_id": "secret-4",
    "account_number": botInfo.accountNum,
    "sequence": botInfo.sequence,
    "fee": botInfo.fee.to_data(),
    "msgs": [],
    "memo": "",
  })

  stdSignMsg.msgs = [msgExecuteFirst, msgExecuteSecond]

  tx = botInfo.wallet.key.sign_tx(stdSignMsg)
  try:
    res = botInfo.client.tx.broadcast(tx)
    return res
  except:
    print("BROADCAST TX ERROR")
    return False

def createMsgExecuteSswap(botInfo: BotInfo, expectedReturn, amountToSwap, contractAddr, contractHash, nonce, txEncryptionKey):
  msgSswap = json.dumps({"swap":{"expected_return":expectedReturn}})
  encryptedMsgSswap = str( base64.b64encode(msgSswap.encode("utf-8")), "utf-8")
  handleMsgSswap = { "send": {"recipient": botInfo.pairContractAddresses["pair1"], "amount": amountToSwap, "msg": encryptedMsgSswap }}
  msgExecuteSswap = botInfo.client.wasm.contract_execute_msg(botInfo.accAddr, contractAddr, handleMsgSswap, [], contractHash, nonce, txEncryptionKey)
  return msgExecuteSswap

def createMsgExecuteSienna(botInfo: BotInfo, expectedReturn, amountToSwap, contractAddr, contractHash, nonce, txEncryptionKey):
  msgSienna = json.dumps({"swap":{"to":None,"expected_return":expectedReturn}})
  encryptedMsgSienna = str( base64.b64encode(msgSienna.encode("utf-8")), "utf-8")
  handleMsgSienna = { "send": {"recipient": botInfo.pairContractAddresses["pair2"], "amount": amountToSwap, "msg": encryptedMsgSienna }}
  msgExecuteSienna = botInfo.client.wasm.contract_execute_msg(botInfo.accAddr, contractAddr, handleMsgSienna, [], contractHash, nonce, txEncryptionKey)
  return msgExecuteSienna


def swapSienna(
    botInfo: BotInfo,
    sscrtBal, 
    firstSwap, 
    secondSwap, 
    nonceDict, 
    txEncryptionKeyDict,
  ):

  sscrtBalStr = str(int(sscrtBal * 10 ** 6))
  firstSwapStr = str(int(firstSwap * 10 ** 8))
  secondSwapStr = str(int(secondSwap * 10 ** 6))

  msgExecuteSienna = createMsgExecuteSienna(
    botInfo, 
    firstSwapStr, 
    sscrtBalStr,  
    botInfo.tokenContractAddresses["token1"],
    botInfo.tokenContractHashes["token1"],
    nonceDict['first'], 
    txEncryptionKeyDict['first'],
  )

  msgExecuteSswap = createMsgExecuteSswap(
    botInfo,
    secondSwapStr,
    firstSwapStr,
    botInfo.tokenContractAddresses["token2"],
    botInfo.tokenContractHashes["token2"], 
    nonceDict["second"],
    txEncryptionKeyDict["second"],
  )
  
  return broadcastTx(botInfo, msgExecuteSienna, msgExecuteSswap)

def swapSswap(
    botInfo: BotInfo,
    sscrtBal, 
    firstSwap, 
    secondSwap, 
    nonceDict, 
    txEncryptionKeyDict,
  ):

  sscrtBalStr = str(int(sscrtBal * 10 ** 6))
  firstSwapStr = str(int(firstSwap * 10 ** 8))
  secondSwapStr = str(int(secondSwap * 10 ** 6))

  msgExecuteSswap = createMsgExecuteSswap(
    botInfo, 
    firstSwapStr,
    sscrtBalStr,
    botInfo.tokenContractAddresses["token1"],
    botInfo.tokenContractHashes["token1"],
    nonceDict["first"],
    txEncryptionKeyDict["first"],
  )

  msgExecuteSienna = createMsgExecuteSienna(
    botInfo,
    secondSwapStr,
    firstSwapStr,
    botInfo.tokenContractAddresses["token2"],
    botInfo.tokenContractHashes["token2"],
    nonceDict["second"],
    txEncryptionKeyDict["second"]
  )

  return broadcastTx(botInfo, msgExecuteSswap, msgExecuteSienna)

def generateTxEncryptionKeys(client: LCDClient):
  nonceDict = {"first":client.utils.generate_new_seed(), "second":client.utils.generate_new_seed()}
  txEncryptionKeyDict = {"first":client.utils.get_tx_encryption_key(nonceDict["first"]), "second":client.utils.get_tx_encryption_key(nonceDict["second"])}
  return nonceDict, txEncryptionKeyDict

def txHandle(txResponse, profit, logWriter, runningProfit, lastHeight):
  if(not txResponse):
    print( "ERROR" )
    return False
  
  if(txResponse.is_tx_error()):
    #logWriter.writerow([txResponse.to_json()])
    print(txResponse.to_json())
    logWriter.writerow([datetime.now(), "Error", txResponse.txhash, "height", lastHeight])
    print(txResponse.txhash)
    return False

  print(txResponse.txhash)
  #logWriter.writerow([txResponse.to_json()])
  print(txResponse.to_json())
  logWriter.writerow([datetime.now(), "profit", str(profit), "runningTotal", str(runningProfit), txResponse.txhash, "height", lastHeight])

  return True

def main():
  global SSCRT_CONTRACT_HASH, SHD_CONTRACT_HASH
  txLog = open("shd-scrt-pair-log.csv", "a")
  logWriter = csv.writer(txLog, delimiter=' ')

  mk = MnemonicKey(mnemonic=mkSeed)
  client = LCDClient('https://lcd.secret.llc', 'secret-4')
  wallet = client.wallet(mk)
  SSCRT_CONTRACT_HASH = client.wasm.contract_hash(SSCRT_ADDRESS)
  SHD_CONTRACT_HASH = client.wasm.contract_hash(SHD_ADDRESS)
  contractHashes = { "SHD": SHD_CONTRACT_HASH, "SSCRT": SSCRT_CONTRACT_HASH}
  nonceDict, txEncryptionKeyDict = generateTxEncryptionKeys(client)
  fee = StdFee(200001, "050001uscrt")
  accountNumber, sequence = wallet.account_number(), wallet.sequence()

  scrtBal, sscrtBal, shdBal, lastSscrtBal = 0, 0, 0, 0
  keepLooping = True
  txResponse = ""
  runningProfit = 0
  amountSwapping = 40 #sscrt
  lastHeight = 0
  gasFeeScrt = .050001 + .00027
  print("Starting main loop")
  while keepLooping:
    try:
      lastHeight = sync_next_block(client, lastHeight)
      txResponse = ""
      lastSscrtBal = sscrtBal
      scrtBal = int(client.bank.balance(mk.acc_address).to_data()[0]["amount"]) * 10**-6
      checkScrtBal(client, wallet, mk.acc_address, scrtBal, amountSwapping)
      siennaRatio, siennat2, siennat1 = getSiennaRatio(client)
      sswapRatio, sswapt2, sswapt1 = getSSwapRatio(client)
    except:
      print("ERROR in queries\n")
      continue
    try:
      difference = siennaRatio - sswapRatio 
      profit= firstSwap = secondSwap = 0
      if( difference > 0 ):
        profit, firstSwap, secondSwap = calculateProfitCP(sswapt2, sswapt1, siennat2, siennat1, amountSwapping, gasFeeScrt)
      if( difference < 0 ):
        profit, firstSwap, secondSwap = calculateProfitCP(siennat2, siennat1, sswapt2, sswapt1, amountSwapping, gasFeeScrt)
      print(datetime.now(), "  height:", lastHeight, "  profit:", profit)
      if( profit > 0 and difference > 0):
        txResponse = swapSswap(
          client,
          wallet,
          amountSwapping,
          firstSwap,
          secondSwap,
          nonceDict,
          txEncryptionKeyDict,
          contractHashes,
          accountNumber,
          sequence,
          fee,
        )
      if( profit > 0 and difference < 0):
        txResponse = swapSienna(
          client,
          wallet,
          amountSwapping,
          firstSwap,
          secondSwap,
          nonceDict,
          txEncryptionKeyDict,
          contractHashes,
          accountNumber,
          sequence,
          fee,
        )
      if( txResponse != ""):
        runningProfit += profit
        print( runningProfit )
        txHandle(txResponse, profit, logWriter, runningProfit, lastHeight)
        nonceDict, txEncryptionKeyDict = generateTxEncryptionKeys(client)
        sequence = str(int(sequence) + 1)
    except:
      print( "ERROR in tx\n" )
      continue
  print( runningProfit )
  txLog.close()

#main()

def testMain():
  global botConfig
  txLog = open(botConfig["logLocation"], "a")
  logWriter = csv.writer(txLog, delimiter=' ')

  botInfo = BotInfo(botConfig)

  nonceDict, txEncryptionKeyDict = generateTxEncryptionKeys(botInfo.client)

  scrtBal, sscrtBal, shdBal, lastSscrtBal = 0, 0, 0, 0
  keepLooping = True
  txResponse = ""
  runningProfit = 0
  amountSwapping = 40 #sscrt
  lastHeight = 0
  gasFeeScrt = .050001 + .00027
  print("Starting test")
  try:
    lastHeight = sync_next_block(botInfo.client, lastHeight)
    txResponse = ""
    lastSscrtBal = sscrtBal
    #scrtBal, sscrtBal, shdBal = getBalances(scrtBal, sscrtBal, shdBal)
    scrtBal = int(botInfo.client.bank.balance(botInfo.accAddr).to_data()[0]["amount"]) * 10**-6
    checkScrtBal(botInfo, scrtBal, amountSwapping)
    siennaRatio, siennat1, siennat2 = getSiennaRatio(botInfo.client)
    sswapRatio, sswapt1, sswapt2 = getSSwapRatio(botInfo.client)
  except:
    print("ERROR in queries\n")
    return
  try:
    difference = siennaRatio - sswapRatio 
    profit= firstSwap = secondSwap = 0
    if( difference > 0 ):
      profit, firstSwap, secondSwap = calculateProfitCP(sswapt2, sswapt1, siennat2, siennat1, amountSwapping, gasFeeScrt)
    if( difference < 0 ):
      profit, firstSwap, secondSwap = calculateProfitCP(siennat2, siennat1, sswapt2, sswapt1, amountSwapping, gasFeeScrt)
    print(datetime.now(), "  height:", lastHeight, "  profit:", profit)
    print(firstSwap, secondSwap, profit)
    if(difference > 0):
      txResponse = swapSswap(
        botInfo,
        amountSwapping,
        firstSwap,
        secondSwap,
        nonceDict,
        txEncryptionKeyDict,
      )
    if(difference < 0):
      txResponse = swapSienna(
        botInfo,
        amountSwapping,
        firstSwap,
        secondSwap,
        nonceDict,
        txEncryptionKeyDict,
      )
    if( txResponse != ""):
      runningProfit += profit
      txHandle(txResponse, profit, logWriter, runningProfit)
      print(nonceDict)
      nonceDict, txEncryptionKeyDict = generateTxEncryptionKeys(botInfo.client)
      botInfo.sequence = botInfo.sequence + 1
  except:
    print( "ERROR in tx\n" )
    return
  print( runningProfit )
  txLog.close()

#testMain()

def executeOneSwap():
  mk = MnemonicKey(mnemonic=mkSeed)
  client = LCDClient('https://lcd.secret.llc', 'secret-4')
  wallet = client.wallet(mk)
  SSCRT_CONTRACT_HASH = client.wasm.contract_hash(SSCRT_ADDRESS)
  SHD_CONTRACT_HASH = client.wasm.contract_hash(SHD_ADDRESS)
  contractHashes = { "SHD": SHD_CONTRACT_HASH, "SSCRT": SSCRT_CONTRACT_HASH}
  nonceDict, txEncryptionKeyDict = generateTxEncryptionKeys(client)
  fee = StdFee(100000, "025000uscrt")
  accountNumber, sequence = wallet.account_number(), wallet.sequence()
  
  msgExecute = createMsgExecuteSswap(client, "0", "07720436", mk.acc_address, SHD_ADDRESS, contractHashes["SHD"], nonceDict["first"], txEncryptionKeyDict["first"])
  
  stdSignMsg = StdSignMsg.from_data({
    "chain_id": "secret-4",
    "account_number": accountNumber,
    "sequence": sequence,
    "fee": fee.to_data(),
    "msgs": [],
    "memo": "",
  })

  stdSignMsg.msgs = [msgExecute]

  tx = wallet.key.sign_tx(stdSignMsg)
  res = client.tx.broadcast(tx)
  print(res.to_data())
  client.utils.decrypt()

#executeOneSwap()

def decryptErrorMessage():
  client = LCDClient('https://lcd.secret.llc', 'secret-4')
  nonces = {'first': [254, 38, 86, 62, 183, 120, 24, 160, 131, 209, 81, 150, 236, 180, 49, 171, 58, 241, 247, 14, 32, 202, 86, 124, 27, 25, 59, 58, 127, 108, 228, 226], 'second': [76, 0, 78, 169, 118, 81, 13, 205, 79, 215, 129, 151, 175, 59, 204, 113, 197, 146, 234, 234, 76, 124, 112, 34, 178, 51, 153, 78, 68, 74, 29, 81]}
  res = {"code":3,"codespace":"compute","gas_used":27808,"gas_wanted":200001,"height":2599045,"logs":None,"raw_log":"failed to execute message; message index: 0: encrypted: zMagT2Ecb0CWKOYBDKAJDvemF9/YOsuL8lnNPkqs6XrDQV1KNZos8i/5vXUt4vCr0/rJOqSNCKUpcJZKT4y7ERn9AVi4QIDV8T/UlAYPlT8WOUjoUOdZb7P+: execute contract failed","txhash":"2C8841921265CC99C4C144502A74C426E8ACE397BC3CCC961B0D6A9A8737F253"}
  rawLog = res["raw_log"]
  print(rawLog.split(" "))
  splitRawLog = ['failed', 'to', 'execute', 'message;', 'message', 'index:', '0:', 'encrypted:', 'oUeK8OezwJOEFFvIdMCdDjtfOrJCfc73GSETu9JVR5NK/Q4WESrmn9JRi4KW8eOUsrgPgZXQpLu3ZMD1p/S0ibro3e2OvvJlovvO9q38E7EjnKQvyEzb3RTZ:', 'execute', 'contract', 'failed']
  isNextEncrypted = False
  encrypted = ""
  for elements in splitRawLog:
    if(isNextEncrypted):
      encrypted = elements
      break
    if( elements == 'encrypted:'):
      isNextEncrypted = True
  print(encrypted)
  input = base64.b64decode(bytes(encrypted, "utf-8"))
  #res2 = asyncio.get_event_loop().run_until_complete(client.utils.decrypt(input, nonces["second"]))
  siv = SIV(tx_encryption_key)
  plaintext = siv.open(ciphertext, [bytes()])
  print(res2)
  
#decryptErrorMessage()