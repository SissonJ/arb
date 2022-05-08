import base64
#import fcntl
from math import sqrt
import time
import csv
import json
import traceback
from typing import Dict, Optional
import requests
from datetime import datetime

from BotInfo import BotInfo
from config import sscrtAdresses

from secret_sdk.client.lcd import LCDClient
from secret_sdk.core.auth.data.tx import StdSignMsg

SSCRT_ADDRESS = sscrtAdresses["SSCRT_ADDRESS"]
SSCRT_KEY = sscrtAdresses["SSCRT_KEY"]

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

def generateTxEncryptionKeys(client: LCDClient):
  nonceDict = {"first":client.utils.generate_new_seed(), "second":client.utils.generate_new_seed()}
  txEncryptionKeyDict = {
    "first": client.utils.get_tx_encryption_key(nonceDict["first"]), 
    "second": client.utils.get_tx_encryption_key(nonceDict["second"])
  }
  return nonceDict, txEncryptionKeyDict

def buyScrt(botInfo: BotInfo, scrtBal, logLocation):
  global SSCRT_ADDRESS, SSCRT_KEY
  sscrtBalRes = botInfo.client.wasm.contract_query(SSCRT_ADDRESS, { "balance": { "address": botInfo.accAddr, "key": SSCRT_KEY }})
  redeemAmount = int(sscrtBalRes['balance']['amount']) - scrtBal * 10 ** 6
  if( redeemAmount > 50 ):
    redeemAmount = 50
  handleMsg = {"redeem":{"amount":str(redeemAmount)}}
  res = botInfo.wallet.execute_tx(SSCRT_ADDRESS, handleMsg)

  res = requests.get("https://api.coingecko.com/api/v3/simple/price?ids=secret&vs_currencies=usd")
  data = res.json()

  with open(logLocation, mode="a", newline="") as csv_file:
    logWriter = csv.writer(csv_file, delimiter=',')
    logWriter.writerow([datetime.now(), data["secret"]["usd"], scrtBal, (int(sscrtBalRes['balance']['amount']) - scrtBal * 10 ** 6) - redeemAmount, "Bought scrt with sscrt for gas"])
  
  return

def checkScrtBal(botInfo: BotInfo, scrtBal, tradeAmount, logLocation):
  if (scrtBal < 1 ):
    print("NOT ENOUGH SCRT")
    buyScrt(botInfo, tradeAmount, logLocation)
    return 
  return

def getSSwapRatio(botInfo: BotInfo, nonce: Optional[int] = None, tx_encryption_key: Optional[str] = None):
  sswapInfo = botInfo.client.wasm.contract_query(
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
  return token1Amount/token2Amount, token1Amount, token2Amount

def getSiennaRatio(botInfo: BotInfo, nonce: Optional[int] = None, tx_encryption_key: Optional[str] = None):
  siennaInfo = botInfo.client.wasm.contract_query(
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
  return token1Amount/token2Amount, token1Amount, token2Amount

def constantProduct(poolBuy, poolSell, x):
  out = -(poolBuy * poolSell)/(poolSell + x) + poolBuy
  return out

def optimumProfit(poolBuy1, poolSell1, poolBuy2, poolSell2):
  optimized = (9.380602724198101*10**-6*(-1.06613651635*10**11 * poolBuy1 * poolSell1 * poolSell2-1.06934455*10**11 * poolSell1 * poolSell2**2+1.0660297422966704*10**8 *
    (994009 * poolBuy1**3 * poolSell1 * poolBuy2 * poolSell2 + 1.994*10**6 * poolBuy1**2 * poolSell1 * poolBuy2 *poolSell2**2 + 
    1*10**6 * poolBuy1 * poolSell1 * poolBuy2 * poolSell2**3)**.5))/(994009 * poolBuy1**2 + 1.994*10**6 *poolBuy1*poolSell2 + 1*10**6 * poolSell2**2)
  return optimized

def calculateProfitCP(s1t2, s1t1, s2t2, s2t1, amountSwapped, gasFeeScrt):
  firstSwap = constantProduct(s1t2, s1t1, amountSwapped*.996)
  secondSwap = constantProduct(s2t1, s2t2, firstSwap*.997) * .999

  profit = secondSwap - amountSwapped - gasFeeScrt
  return profit, firstSwap, secondSwap 

def calculateProfit(s1t2, s1t1, s2t2, s2t1, minimumAmountToSwap, gasFeeScrt):
  tempAmount = minimumAmountToSwap
  firstSwap = secondSwap = amountToSwap = 0
  maxProfit = -1000
  while tempAmount < 501:
    tempFirstSwap = constantProduct(s1t2, s1t1, tempAmount*.9969)
    tempSecondSwap = constantProduct(s2t1, s2t2, tempFirstSwap*.997) * .9999
    tempProfit = tempSecondSwap - tempAmount - gasFeeScrt
    if tempProfit > maxProfit:
      amountToSwap = tempAmount
      firstSwap = tempFirstSwap
      secondSwap = tempSecondSwap
      maxProfit = tempProfit
    if(tempAmount < 100):
      tempAmount = tempAmount + 10
    else:
      tempAmount = tempAmount + 50
  return amountToSwap, maxProfit, firstSwap, secondSwap

def calculateProfitOptimized(s1t2,s1t1,s2t2,s2t1, max, gasFeeScrt):
  amountToSwap = optimumProfit(s1t2, s1t1, s2t1, s2t2)
  profit = firstSwap = secondSwap = 0
  if (amountToSwap > max):
    amountToSwap = max
  if (amountToSwap < 1):
    amountToSwap = 1
  firstSwap = constantProduct(s1t2, s1t1, amountToSwap*.997) * .9999
  secondSwap = constantProduct(s2t1, s2t2, firstSwap*.997) * .9999
  profit = secondSwap - amountToSwap - gasFeeScrt
  return amountToSwap, profit, firstSwap, secondSwap

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
    #print(res)
    return res
  except Exception as e:
    with open( botInfo.logs["output"], mode="a", newline="") as csv_file:
      logWriter = csv.writer(csv_file, delimiter=',')
      logWriter.writerow([datetime.now().date(), datetime.now().time(),"BROADCAST TX ERROR", e])
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
    minExpected,
    firstSwap, 
    #secondSwap, 
    nonceDict, 
    txEncryptionKeyDict,
  ):

  sscrtBalStr = str(int(sscrtBal * 10 ** botInfo.tokenDecimals["token1"]))
  minExpectedStr = str(int(minExpected * 10 ** botInfo.tokenDecimals["token1"]))
  firstSwapStr = str(int(firstSwap * 10 ** botInfo.tokenDecimals["token2"]))
  #firstMinExpected = str(int(firstSwapStr)-1)
  #secondSwapStr = str(int(secondSwap * 10 ** botInfo.tokenDecimals["token1"]))

  msgExecuteSienna = createMsgExecuteSienna(
    botInfo, 
    "0", 
    sscrtBalStr,  
    botInfo.tokenContractAddresses["token1"],
    botInfo.tokenContractHashes["token1"],
    nonceDict['first'], 
    txEncryptionKeyDict['first'],
  )

  msgExecuteSswap = createMsgExecuteSswap(
    botInfo,
    minExpectedStr,
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
    minExpected,
    firstSwap, 
    #secondSwap, 
    nonceDict, 
    txEncryptionKeyDict,
  ):

  sscrtBalStr = str(int(sscrtBal * 10 ** botInfo.tokenDecimals["token1"]))
  minExpectedStr = str(int(minExpected * 10 ** botInfo.tokenDecimals["token1"]))
  firstSwapStr = str(int(firstSwap * 10 ** botInfo.tokenDecimals["token2"]))
  #firstMinExpected = str(int(int(firstSwapStr) * .999))
  #secondSwapStr = str(int(secondSwap * 10 ** botInfo.tokenDecimals["token1"]))

  msgExecuteSswap = createMsgExecuteSswap(
    botInfo, 
    "0",
    sscrtBalStr,
    botInfo.tokenContractAddresses["token1"],
    botInfo.tokenContractHashes["token1"],
    nonceDict["first"],
    txEncryptionKeyDict["first"],
  )

  msgExecuteSienna = createMsgExecuteSienna(
    botInfo,
    minExpectedStr,
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

def txHandle(logLocation, txResponse, profit, runningProfit, lastHeight, amountSwapped):
  if(not txResponse):
    print( "ERROR - txResponse returned false" )
    return False
  
  with open(logLocation, mode="a") as csv_file:
    logWriter = csv.writer(csv_file, delimiter=',')

    if(txResponse.is_tx_error()):
      #logWriter.writerow([txResponse.to_json()])
      logWriter.writerow([datetime.now(), "Error", txResponse.txhash, "height", lastHeight])
      print(txResponse.txhash)
      return False

    #logWriter.writerow([txResponse.to_json()])
    print("Success!")
    logWriter.writerow([datetime.now(), str(profit), str(runningProfit), txResponse.txhash, lastHeight, amountSwapped])

  return True

def calculate_gain_loss( controler: BotInfo, newScrtBal, newSscrtBal, scrtPrice, amount_swapped):
  gain = 0
  if( not newScrtBal == controler.total[1] ):
    gain = gain + newScrtBal * controler.total[2] - controler.total[1] * controler.total[2] 
    controler.total[1] = newScrtBal
  if( newSscrtBal > controler.total[0] ):
    temp_scrt_amount = 0
    cost_basis_gain = 0
    while temp_scrt_amount < amount_swapped:
      temp = [0,0]
      indexhldr = index = 0
      for things in controler.inv:
        if( things[0] > temp[0] ):
          temp = things
          index = indexhldr
        indexhldr = indexhldr + 1
      if( temp[1] > amount_swapped - temp_scrt_amount ):
        cost_basis_gain = cost_basis_gain + (amount_swapped - temp_scrt_amount) * temp[0]
        controler.inv[index][1] = controler.inv[index][1] - (amount_swapped - temp_scrt_amount)
        controler.inv.append([scrtPrice, amount_swapped + (newSscrtBal - controler.total[0])])
        temp_scrt_amount = amount_swapped
      else:
        temp_scrt_amount = temp_scrt_amount + temp[1]
        cost_basis_gain = cost_basis_gain + temp[1] * temp[0]
        controler.inv.pop(index)
        if( temp_scrt_amount == amount_swapped ):
          controler.inv.append([scrtPrice, amount_swapped + newSscrtBal - controler.total[0]])
    gain = gain + (amount_swapped * scrtPrice - cost_basis_gain) + (newSscrtBal - controler.total[0]) * scrtPrice
    controler.total[0] = newSscrtBal
  return gain

def recordTx(botInfo: BotInfo, pair, amountSwapped, ratio, wallet):
  scrtBal, t1Bal, t2Bal = getBalances(botInfo)
  res = requests.get("https://api.coingecko.com/api/v3/simple/price?ids=secret&vs_currencies=usd")
  data = res.json()
  botInfo.read_inventory(wallet)
  gain = calculate_gain_loss(botInfo, scrtBal, t1Bal, data["secret"]["usd"], amountSwapped)
  botInfo.write_inventory(wallet)

  with open( botInfo.logs["csv"], mode="a", newline="") as csv_file:
    logWriter = csv.writer(csv_file, delimiter=',')
    #date,time,scrt price,scrt bal,t1 bal,ratio,t2 bal,amount swapped,gain/loss
    logWriter.writerow([datetime.now(), data["secret"]["usd"], scrtBal, t1Bal, ratio, t2Bal, amountSwapped, gain])
  
  with open( botInfo.logs["central"], mode="a", newline="") as csv_file:
    botInfo.enter(csv_file)
    logWriter = csv.writer(csv_file, delimiter=',')
    #date, time, pair, sscrt/usd, scrt bal, sscrtBal, t2/sscrt, t2Bal, amount traded, gain/loss
    logWriter.writerow([datetime.now().date(), datetime.now().time(), pair,  data["secret"]["usd"], scrtBal, t1Bal, ratio, t2Bal, amountSwapped, gain])
    #fcntl.flock(csv_file, fcntl.LOCK_UN)

  return t1Bal


def getBalances(botInfo: BotInfo):
  scrtBalRes = botInfo.client.bank.balance(botInfo.accAddr)
  t1BalRes = botInfo.client.wasm.contract_query(
    botInfo.tokenContractAddresses["token1"], 
    { "balance": { "address": botInfo.accAddr, "key": botInfo.tokenKeys["token1"] }}
  )
  t2BalRes = botInfo.client.wasm.contract_query(
    botInfo.tokenContractAddresses["token2"], 
    { "balance": { "address": botInfo.accAddr, "key": botInfo.tokenKeys["token2"] }}
  )
  scrtBal = int(scrtBalRes.to_data()[0]["amount"]) * 10**-6
  t1Bal = float(t1BalRes['balance']['amount'])* 10**-botInfo.tokenDecimals["token1"]
  t2Bal = float(t2BalRes['balance']['amount'])* 10**-botInfo.tokenDecimals["token2"]
  return scrtBal, t1Bal, t2Bal

def log_traceback(ex, ex_traceback=None):
  if ex_traceback is None:
    ex_traceback = ex.__traceback__
  tb_lines = [ line.rstrip('\n') for line in
    traceback.format_exception(ex.__class__, ex, ex_traceback)]
  return tb_lines