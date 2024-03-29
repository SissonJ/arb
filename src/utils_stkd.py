from cmath import sqrt
import csv
from datetime import datetime
import fcntl
import time

import requests
from BotInfo import BotInfo
from secret_sdk.core.auth.data.tx import StdSignMsg
from secret_sdk.core.coins import Coins
from utils import calculate_gain_loss, constantProduct, createMsgExecuteSienna, getBalances, getSiennaRatio
from config import sscrtAdresses

SSCRT_ADDRESS = sscrtAdresses["SSCRT_ADDRESS"]
SSCRT_KEY = sscrtAdresses["SSCRT_KEY"]

def getStkdPrice(botInfo: BotInfo, nonce, txEncryptionKey):
  res = botInfo.client.wasm.contract_query(
    botInfo.tokenContractAddresses["token2"], 
    { "staking_info": { "time": round(time.time()) } },
    #botInfo.pairContractHash["pair2"],
    #nonce,
    #txEncryptionKey,
  )
  return float(res["staking_info"]["price"])*10**-6

def optimumSwapAmountStkd(poolBuy, poolSell, mintPrice):
  optimized = -(1/sqrt(mintPrice).real) * 0.00020062192797672785 * (-4987.249241816575 * sqrt(poolBuy).real * sqrt(poolSell).real + 5000 * sqrt(mintPrice).real * poolSell)
  return optimized

def calculateProfitStkd(botInfo: BotInfo, maxAmount, gasFeeScrt, nonceDict, encryptionKeyDict):
  ratio, s1t1, s1t2 = getSiennaRatio(botInfo, nonceDict["first"], encryptionKeyDict["first"])
  stkdPrice = getStkdPrice(botInfo, nonceDict["second"], encryptionKeyDict["second"])
  swapAmount = optimumSwapAmountStkd(s1t1,s1t2,stkdPrice)
  firstSwap = secondSwap = profit = 0
  if(swapAmount > maxAmount):
    swapAmount = maxAmount
  if( swapAmount < 2 ):
    swapAmount = 2
  if( swapAmount > 0 ):
    firstSwap = constantProduct(s1t1, s1t2, swapAmount*.997) * .9999
    secondSwap = ( firstSwap * .998 ) /  stkdPrice
    profit = secondSwap - swapAmount - gasFeeScrt
  else:
    return -1, -1, 0, 0, 0
  return swapAmount, profit, firstSwap, secondSwap, stkdPrice

def arbTrackerStkd(botInfo: BotInfo, nonceDict, encryptionKeyDict): 
    ratio, s1t1, s1t2 = getSiennaRatio(botInfo, nonceDict["first"], encryptionKeyDict["first"])
    stkdPrice = getStkdPrice(botInfo, nonceDict["second"], encryptionKeyDict["second"])
    optimum = optimumSwapAmountStkd(s1t1,s1t2,stkdPrice).real
    swapAmount = optimum
    if( swapAmount < 40.0 ):
        swapAmount = 40
    firstSwap = constantProduct(s1t1, s1t2, swapAmount*.9969)
    secondSwap = ( firstSwap * .9979 ) /  stkdPrice
    profit = secondSwap - swapAmount - float(botInfo.fee.amount.to_data()[0]["amount"])*10**-6
    return profit, s1t1, s1t2, s1t1/s1t2, stkdPrice, swapAmount, optimum

def broadcastTxStkd(botInfo: BotInfo, msgExecuteFirst, msgExecuteSecond, msgConvertSscrt):

  stdSignMsg = StdSignMsg.from_data({
    "chain_id": "secret-4",
    "account_number": botInfo.accountNum,
    "sequence": botInfo.sequence,
    "fee": botInfo.fee.to_data(),
    "msgs": [],
    "memo": "",
  })

  stdSignMsg.msgs = [msgExecuteFirst, msgConvertSscrt, msgExecuteSecond]

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

def swapStkd(
    botInfo: BotInfo,
    stkdBal, 
    firstSwap,
    minAmountRec, 
    #secondSwap, 
    nonceDict, 
    txEncryptionKeyDict,
  ):

  stkdBalStr = str(int(stkdBal * 10 ** botInfo.tokenDecimals["token1"]))
  firstSwapStr = str(int(firstSwap * 10 ** botInfo.tokenDecimals["token2"]))
  minAmountRecStr = str(int(stkdBal * 10 ** botInfo.tokenDecimals["token1"]))
  #secondSwapStr = str(int(secondSwap * 10 ** botInfo.tokenDecimals["token1"]))
  
  msgExecuteSienna = createMsgExecuteSienna(
    botInfo,
    firstSwapStr,
    stkdBalStr,
    botInfo.tokenContractAddresses["token2"],
    botInfo.tokenContractHashes["token2"],
    nonceDict["first"],
    txEncryptionKeyDict["first"]
  )

  msgSscrtToScrt = botInfo.client.wasm.contract_execute_msg(
    botInfo.accAddr,
    SSCRT_ADDRESS,
    {"redeem":{"amount": firstSwapStr}},
    [],
  )

  msgExecuteStkd = botInfo.client.wasm.contract_execute_msg(
    botInfo.accAddr, 
    botInfo.tokenContractAddresses["token2"], 
    {"stake": {}}, 
    Coins.from_str(firstSwapStr+"uscrt"),#{"denom": "uscrt", "amount": firstSwapStr}], 
    botInfo.tokenContractHashes["token2"],
  )

  return broadcastTxStkd(botInfo, msgExecuteSienna, msgExecuteStkd, msgSscrtToScrt)

def recordTxStkd(botInfo: BotInfo, pair, amountSwapped, ratio, wallet):
  scrtBal, t1Bal, t2Bal = getBalances(botInfo) #scrt, sscrt, stkd
  res = requests.get("https://api.coingecko.com/api/v3/simple/price?ids=stkd-scrt&vs_currencies=usd")
  data = res.json()
  botInfo.read_inventory(wallet)
  gain = calculate_gain_loss(botInfo, scrtBal, t2Bal, data["stkd-scrt"]["usd"], amountSwapped)
  botInfo.write_inventory(wallet)

  with open( botInfo.logs["csv"], mode="a", newline="") as csv_file:
    logWriter = csv.writer(csv_file, delimiter=',')
    #date,time,stkd-scrt price,scrt bal,t1 bal,ratio,t2 bal,amount swapped,gain/loss
    logWriter.writerow([datetime.now(), data["stkd-scrt"]["usd"], scrtBal, t1Bal, ratio, t2Bal, amountSwapped, gain])
  
  with open( botInfo.logs["central"], mode="a", newline="") as csv_file:
    botInfo.enter(csv_file)
    logWriter = csv.writer(csv_file, delimiter=',')
    #date, time, pair, stkd-sscrt/usd, scrt bal, sscrtBal, t2/sscrt, t2Bal, amount traded, gain/loss
    logWriter.writerow([datetime.now().date(), datetime.now().time(), pair,  data["stkd-scrt"]["usd"], scrtBal, t1Bal, ratio, t2Bal, amountSwapped, gain])
    fcntl.flock(csv_file, fcntl.LOCK_UN)

  return t2Bal, scrtBal