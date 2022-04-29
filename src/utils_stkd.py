from cmath import sqrt
from datetime import datetime
import time
from BotInfo import BotInfo
from secret_sdk.core.auth.data.tx import StdSignMsg
from secret_sdk.core.coins import Coins
from utils import constantProduct, createMsgExecuteSienna, getSiennaRatio
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
  optimized = -(1/sqrt(mintPrice)) * 0.00020062192797672785 * (-4987.249241816575 * sqrt(poolBuy) * sqrt(poolSell) + 5000 * sqrt(mintPrice) * poolSell)
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
    firstSwap = constantProduct(s1t1, s1t2, swapAmount*.9969)
    secondSwap = ( firstSwap * .998 ) /  stkdPrice
    profit = secondSwap - swapAmount - gasFeeScrt
  else:
    return -1, -1, 0, 0, 0
  return swapAmount, profit, firstSwap, secondSwap, stkdPrice

def arbTrackerStkd(botInfo: BotInfo, nonceDict, encryptionKeyDict): 
    ratio, s1t1, s1t2 = getSiennaRatio(botInfo, nonceDict["first"], encryptionKeyDict["first"])
    stkdPrice = getStkdPrice(botInfo, nonceDict["second"], encryptionKeyDict["second"])
    print(s1t1, s1t2 )
    print("sienna:", s1t1/s1t2, "mint:", stkdPrice)
    swapAmount = optimumSwapAmountStkd(s1t1,s1t2,stkdPrice).real
    print(swapAmount)
    if( swapAmount < 40.0 ):
        swapAmount = 40
    firstSwap = constantProduct(s1t1, s1t2, swapAmount*.9969)
    secondSwap = ( firstSwap * .998 ) /  stkdPrice
    profit = secondSwap - swapAmount - float(botInfo.fee.amount.to_data()[0]["amount"])*10**-6
    return profit

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
    print(datetime.now(),"BROADCAST TX ERROR")
    print(datetime.now(), e )
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