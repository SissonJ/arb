import asyncio
from datetime import datetime
import sys
import traceback

from BotInfo import BotInfo
from config import config
from utils import calculateProfitOptimized, generateTxEncryptionKeys, runAsyncQueries, runSyncQueries, sync_next_block, checkScrtBal, getSiennaRatio, getSSwapRatio 
from utils import calculateProfit, swapSienna, swapSswap, recordTx

def main():

  botInfo = BotInfo(config["sscrt-shd-config"])#config[sys.argv[1]])

  nonceDictSwap, txEncryptionKeyDictSwap = generateTxEncryptionKeys(botInfo.client)
  nonceDictQuery, txEncryptionKeyDictQuery = generateTxEncryptionKeys(botInfo.client)

  scrtBal, sscrtBal, shdBal, lastSscrtBal = 0, 0, 0, 0
  keepLooping = True
  txResponse = ""
  runningProfit = 0
  minAmountSwapping = 40 #sscrt
  maxAmountSwapping = 500
  optimumAmountSwapping = 0
  height = 0
  lastHeight = 0
  lastProfit = 0
  gasFeeScrt = (int(botInfo.fee.to_data()["gas"])/4000000)*2.5
  #scrtBal = int(botInfo.client.bank.balance(botInfo.accAddr).to_data()[0]["amount"]) * 10**-6
  print("Starting loop")#, sys.argv[1])
  while keepLooping:
    try:
      height = sync_next_block(botInfo.client, lastHeight)
      txResponse = ""
      lastSscrtBal = sscrtBal
      #checkScrtBal(botInfo, scrtBal, maxAmountSwapping, config[sys.argv[1]]["logLocation"])
      sswapRatio, sswapt1, sswapt2,siennaRatio, siennat1, siennat2= runSyncQueries(botInfo, nonceDictQuery, txEncryptionKeyDictQuery)
      #sswapRatio, sswapt1, sswapt2 = getSSwapRatio(botInfo, nonceDictQuery["first"], txEncryptionKeyDictQuery["first"])
      #siennaRatio, siennat1, siennat2 = getSiennaRatio(botInfo, nonceDictQuery["second"], txEncryptionKeyDictQuery["second"])
      print(sswapRatio, sswapt1, sswapt2, siennaRatio, siennat1, siennat2)
    except Exception as e:
      print(traceback.format_exc())
      print( e )
      pass
    try:
      difference = siennaRatio - sswapRatio 
      profit= firstSwap = secondSwap = 0
      if( difference > 0 ):
        optimumAmountSwapping, profit, firstSwap, secondSwap = calculateProfitOptimized(
          sswapt2, sswapt1, siennat2, siennat1, maxAmountSwapping, gasFeeScrt)
      if( difference < 0 ):
        optimumAmountSwapping, profit, firstSwap, secondSwap = calculateProfitOptimized(
          siennat2, siennat1, sswapt2, sswapt1, maxAmountSwapping, gasFeeScrt)
      if(profit != lastProfit):
        print(datetime.now(), "  height:", height, "  profit:", profit, "swapAmount:", optimumAmountSwapping)
      lastProfit = profit
      if(height != lastHeight + 1 and lastHeight != 0):
        print(datetime.now(), "blocks skipped:", height - lastHeight)
      lastHeight = height
      if(profit > 0 and difference > 0):
        txResponse = swapSswap(
          botInfo,
          optimumAmountSwapping,
          optimumAmountSwapping + gasFeeScrt,
          firstSwap,
          nonceDictSwap,
          txEncryptionKeyDictSwap,
        )
      if(profit > 0 and difference < 0):
        txResponse = swapSienna(
          botInfo,
          optimumAmountSwapping,
          optimumAmountSwapping + gasFeeScrt,
          firstSwap,
          nonceDictSwap,
          txEncryptionKeyDictSwap,
        )
      if( txResponse != ""):
        if(not txResponse or txResponse.is_tx_error()):
          print(datetime.now(), "Failed")
        else:
          runningProfit += profit
          print(datetime.now(), "Success! Running profit:", runningProfit)
        recordTx(botInfo, config[sys.argv[1]]["logLocation"], optimumAmountSwapping, (siennaRatio + sswapRatio)/2)
        nonceDictSwap, txEncryptionKeyDictSwap = generateTxEncryptionKeys(botInfo.client)
        #scrtBal = int(botInfo.client.bank.balance(botInfo.accAddr).to_data()[0]["amount"]) * 10**-6
      botInfo.sequence = botInfo.wallet.sequence()
      nonceDictQuery, txEncryptionKeyDictQuery = generateTxEncryptionKeys(botInfo.client)
      keepLooping = False #set to false for only one run
    except Exception as e:
      print( "ERROR in tx\n" )
      print( e )
      #scrtBal = int(botInfo.client.bank.balance(botInfo.accAddr).to_data()[0]["amount"]) * 10**-6
      return

main()