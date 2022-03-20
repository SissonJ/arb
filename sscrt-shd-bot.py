import asyncio
import csv
import time
from datetime import datetime
import json
import base64

from secret_sdk.client.lcd import LCDClient
from secret_sdk.core.auth.data.tx import StdFee, StdSignMsg
from secret_sdk.key.mnemonic import MnemonicKey
from secret_sdk.client.lcd.wallet import Wallet

mkSeed = "easy oxygen bone search trophy soccer video float tiny rack fragile cactus uphold acoustic carbon warm hand pilot topic session because seed magnet domain"

SSWAP_SSCRT_SHD_PAIR = "secret1wwt7nh3zyzessk8c5d98lpfsw79vzpsnerj6d0"
SSWAP_QUERY = { 'pool': {} }
SIENNA_SSCRT_SHD_PAIR = "secret1drm0dwvewjyy0rhrrw485q4f5dnfm6j25zgfe5"
SIENNA_QUERY = 'pair_info'

SSCRT_ADDRESS = 'secret1k0jntykt7e4g3y88ltc60czgjuqdy4c9e8fzek'
SSCRT_CONTRACT_HASH = ''
SSCRT_KEY = 'api_key_nE9AgouX7GVnT0+3LhAGoNmwUZ7HHRR4sUxNB+tbWW4='

SHD_ADDRESS = 'secret1qfql357amn448duf5gvp9gr48sxx9tsnhupu3d'
SHD_CONTRACT_HASH = ''
SHD_KEY = 'api_key_xSmcfnyU8z5750bZSC9icFYUz6whMLIUeEloEqORQ7M='


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

def buyScrt(client:LCDClient, wallet:Wallet, acc_address, scrtBal):
  global SSCRT_ADDRESS, SSCRT_KEY
  sscrtBalRes = client.wasm.contract_query(SSCRT_ADDRESS, { "balance": { "address": acc_address, "key": SSCRT_KEY }})
  redeemAmount = int(sscrtBalRes['balance']['amount']) - scrtBal * 10 ** 6
  handleMsg = {"redeem":{"amount":str(redeemAmount)}}
  res = wallet.execute_tx(SSCRT_ADDRESS, handleMsg)
  return res

def checkScrtBal(client:LCDClient, wallet:Wallet, acc_address, scrtBal, tradeAmount):
  if (scrtBal < 1 ):
    print("NOT ENOUGH SCRT")
    buyScrt(client, wallet, acc_address, tradeAmount)
    return 
  return

def getSiennaRatio(client:LCDClient):
  siennaInfo = client.wasm.contract_query(SIENNA_SSCRT_SHD_PAIR, SIENNA_QUERY)
  shdAmount, sscrtAmount = float(siennaInfo['pair_info']['amount_0']) * 10**-8, float(siennaInfo['pair_info']['amount_1'])*10**-6
  return sscrtAmount/shdAmount, shdAmount, sscrtAmount

def getSSwapRatio(client:LCDClient):
  sswapInfo = client.wasm.contract_query(SSWAP_SSCRT_SHD_PAIR, SSWAP_QUERY)
  sscrtAmount, shdAmount = float(sswapInfo['assets'][0]['amount'])*10**-6, float(sswapInfo['assets'][1]['amount'])*10**-8
  return sscrtAmount/shdAmount, shdAmount, sscrtAmount

def constantProduct(poolBuy, poolSell, x):
  out = -(poolBuy * poolSell)/(poolSell + x) + poolBuy
  return out

def calculateProfitCP(s1Shd, s1Sscrt, s2Shd, s2Sscrt, amountSwapped, gasFeeScrt):
  firstSwap = constantProduct(s1Shd, s1Sscrt, amountSwapped*.996)
  secondSwap = constantProduct(s2Sscrt, s2Shd, firstSwap*.997) * .999

  profit = secondSwap - amountSwapped - gasFeeScrt
  return profit, firstSwap, secondSwap 

def broadcastTx(client: LCDClient, wallet: Wallet, msgExecuteFirst, msgExecuteSecond, accountNumber, sequence, fee: StdFee):

  stdSignMsg = StdSignMsg.from_data({
    "chain_id": "secret-4",
    "account_number": accountNumber,
    "sequence": sequence,
    "fee": fee.to_data(),
    "msgs": [],
    "memo": "",
  })

  stdSignMsg.msgs = [msgExecuteFirst, msgExecuteSecond]

  tx = wallet.key.sign_tx(stdSignMsg)
  try:
    res = client.tx.broadcast(tx)
    return res
  except:
    print("BROADCAST TX ERROR")
    return False

def createMsgExecuteSienna(client: LCDClient, expectedReturn, amountToSwap, senderAddr, contractAddr, contractHash, nonce, txEncryptionKey):
  msgSienna = json.dumps({"swap":{"to":None,"expected_return":expectedReturn}})
  encryptedMsgSienna = str( base64.b64encode(msgSienna.encode("utf-8")), "utf-8")
  handleMsgSienna = { "send": {"recipient": SIENNA_SSCRT_SHD_PAIR, "amount": amountToSwap, "msg": encryptedMsgSienna }}
  msgExecuteSienna = client.wasm.contract_execute_msg(senderAddr, contractAddr, handleMsgSienna, [], contractHash, nonce, txEncryptionKey)
  return msgExecuteSienna

def createMsgExecuteSswap(client: LCDClient, expectedReturn, amountToSwap, senderAddr, contractAddr, contractHash, nonce, txEncryptionKey):
  msgSswap = json.dumps({"swap":{"expected_return":expectedReturn}})
  encryptedMsgSswap = str( base64.b64encode(msgSswap.encode("utf-8")), "utf-8")
  handleMsgSswap = { "send": {"recipient": SSWAP_SSCRT_SHD_PAIR, "amount": amountToSwap, "msg": encryptedMsgSswap }}
  msgExecuteSswap = client.wasm.contract_execute_msg(senderAddr, contractAddr, handleMsgSswap, [], contractHash, nonce, txEncryptionKey)
  return msgExecuteSswap

def swapSienna(
    client: LCDClient, 
    wallet: Wallet,
    sscrtBal, 
    firstSwap, 
    secondSwap, 
    nonceDict, 
    txEncryptionKeyDict,
    contractHashes,
    accNum,
    sequence,
    fee,
  ):

  sscrtBalStr = str(int(sscrtBal * 10 ** 6))
  firstSwapStr = str(int(firstSwap * 10 ** 8))
  secondSwapStr = str(int(secondSwap * 10 ** 6))

  msgExecuteSienna = createMsgExecuteSienna(
    client, 
    firstSwapStr, 
    sscrtBalStr, 
    wallet.key.acc_address, 
    SSCRT_ADDRESS,
    contractHashes["SSCRT"],
    nonceDict['first'], 
    txEncryptionKeyDict['first'],
  )

  msgExecuteSswap = createMsgExecuteSswap(
    client,
    secondSwapStr,
    firstSwapStr,
    wallet.key.acc_address,
    SHD_ADDRESS,
    contractHashes["SHD"], 
    nonceDict["second"],
    txEncryptionKeyDict["second"],
  )
  
  return broadcastTx(client, wallet, msgExecuteSienna, msgExecuteSswap, accNum, sequence, fee)

def swapSswap(
    client: LCDClient, 
    wallet: Wallet,
    sscrtBal, 
    firstSwap, 
    secondSwap, 
    nonceDict, 
    txEncryptionKeyDict,
    contractHashes,
    accNum,
    sequence,
    fee,
  ):

  sscrtBalStr = str(int(sscrtBal * 10 ** 6))
  firstSwapStr = str(int(firstSwap * 10 ** 8))
  secondSwapStr = str(int(secondSwap * 10 ** 6))

  msgExecuteSswap = createMsgExecuteSswap(
    client, 
    firstSwapStr,
    sscrtBalStr,
    wallet.key.acc_address,
    SSCRT_ADDRESS,
    contractHashes["SSCRT"],
    nonceDict["first"],
    txEncryptionKeyDict["first"],
  )

  msgExecuteSienna = createMsgExecuteSienna(
    client,
    secondSwapStr,
    firstSwapStr,
    wallet.key.acc_address,
    SHD_ADDRESS,
    contractHashes["SHD"],
    nonceDict["second"],
    txEncryptionKeyDict["second"]
  )

  return broadcastTx(client, wallet, msgExecuteSswap, msgExecuteSienna, accNum, sequence, fee)

def generateTxEncryptionKeys(client: LCDClient):
  nonceDict = {"first":client.utils.generate_new_seed(), "second":client.utils.generate_new_seed()}
  txEncryptionKeyDict = {"first":client.utils.get_tx_encryption_key(nonceDict["first"]), "second":client.utils.get_tx_encryption_key(nonceDict["second"])}
  return nonceDict, txEncryptionKeyDict

def txHandle(txResponse, profit, logWriter, runningProfit):
  if(not txResponse):
    print( "ERROR" )
    return False
  
  if(txResponse.is_tx_error()):
    logWriter.writerow([txResponse.to_json()])
    print(txResponse.to_json())
    logWriter.writerow([datetime.now(), "Error", txResponse.txhash])
    print(txResponse.txhash)
    return False

  print(txResponse.txhash)
  logWriter.writerow([txResponse.to_json()])
  print(txResponse.to_json())
  logWriter.writerow([datetime.now(), "profit", str(profit), "runningTotal", str(runningProfit)])

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
      siennaRatio, siennaShd, siennaSscrt = getSiennaRatio(client)
      sswapRatio, sswapShd, sswapSscrt = getSSwapRatio(client)
    except:
      print("ERROR in queries\n")
      continue
    try:
      difference = siennaRatio - sswapRatio 
      profit= firstSwap = secondSwap = 0
      if( difference > 0 ):
        profit, firstSwap, secondSwap = calculateProfitCP(sswapShd, sswapSscrt, siennaShd, siennaSscrt, amountSwapping, gasFeeScrt)
      if( difference < 0 ):
        profit, firstSwap, secondSwap = calculateProfitCP(siennaShd, siennaSscrt, sswapShd, sswapSscrt, amountSwapping, gasFeeScrt)
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
        txHandle(txResponse, profit, logWriter, runningProfit)
        nonceDict, txEncryptionkeyDict = generateTxEncryptionKeys(client)
        sequence = str(int(sequence) + 1)
    except:
      print( "ERROR in tx\n" )
      continue
  print( runningProfit )
  txLog.close()

#main()

def testMain():
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
  print("Starting test")
  try:
    lastHeight = sync_next_block(client, lastHeight)
    txResponse = ""
    lastSscrtBal = sscrtBal
    #scrtBal, sscrtBal, shdBal = getBalances(scrtBal, sscrtBal, shdBal)
    scrtBal = int(client.bank.balance(mk.acc_address).to_data()[0]["amount"]) * 10**-6
    checkScrtBal(client, wallet, mk.acc_address, scrtBal, amountSwapping)
    siennaRatio, siennaShd, siennaSscrt = getSiennaRatio(client)
    sswapRatio, sswapShd, sswapSscrt = getSSwapRatio(client)
  except:
    print("ERROR in queries\n")
    return
  try:
    difference = siennaRatio - sswapRatio 
    profit= firstSwap = secondSwap = 0
    if( difference > 0 ):
      profit, firstSwap, secondSwap = calculateProfitCP(sswapShd, sswapSscrt, siennaShd, siennaSscrt, amountSwapping, gasFeeScrt)
    if( difference < 0 ):
      profit, firstSwap, secondSwap = calculateProfitCP(siennaShd, siennaSscrt, sswapShd, sswapSscrt, amountSwapping, gasFeeScrt)
    print(datetime.now(), "  height:", lastHeight, "  profit:", profit)
    print(firstSwap, secondSwap, profit)
    if(difference > 0):
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
    if(difference < 0):
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
      txHandle(txResponse, profit, logWriter, runningProfit)
      print(nonceDict)
      nonceDict, txEncryptionkeyDict = generateTxEncryptionKeys(client)
      sequence = str(int(sequence) + 1)
  except:
    print( "ERROR in tx\n" )
    return
  print( runningProfit )
  txLog.close()

testMain()

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