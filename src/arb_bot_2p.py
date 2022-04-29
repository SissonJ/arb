import asyncio
from datetime import datetime
import sys
import traceback

from BotInfo import BotInfo
from config import config
from utils import calculateProfitOptimized, sync_next_block
from utils import swapSienna, swapSswap, recordTx, generateTxEncryptionKeys
from utils_async import runAsyncQueries, generateTxEncryptionKeysAsync

async def main():

  botInfo = BotInfo(config[sys.argv[1]])

  nonceDictSwap, txEncryptionKeyDictSwap = generateTxEncryptionKeys(botInfo.client)
  nonceDictQuery, txEncryptionKeyDictQuery = await generateTxEncryptionKeysAsync(botInfo.asyncClient)

  sscrtBal = 0
  keepLooping = True
  txResponse = ""
  runningProfit = 0
  maxAmountSwapping = 650
  optimumAmountSwapping = 0
  height = 0
  lastHeight = 0
  lastProfit = 0
  lastLoopIsError = False
  gasFeeScrt = (int(botInfo.fee.to_data()["gas"])/4000000)*2.5
  print("Starting loop")#, sys.argv[1])
  while keepLooping:
    if lastLoopIsError:
      botInfo.sequence = botInfo.wallet.sequence()
      nonceDictSwap, txEncryptionKeyDictSwap = generateTxEncryptionKeys(botInfo.client)
      nonceDictQuery, txEncryptionKeyDictQuery = await generateTxEncryptionKeysAsync(botInfo.asyncClient)
      lastLoopIsError = False
      continue
    try:
      height = sync_next_block(botInfo.client, lastHeight)
      txResponse = ""
      sswapRatio, sswapt1, sswapt2,siennaRatio, siennat1, siennat2 = await runAsyncQueries(
        botInfo, 
        nonceDictQuery, 
        txEncryptionKeyDictQuery
      )
    except Exception as e:
      print(datetime.now(), "Error in Queries")
      print(traceback.format_exc())
      print( e )
      lastLoopIsError = True
      continue
    try:
      difference = siennaRatio - sswapRatio 
      profit= firstSwap = secondSwap = 0
      if(difference > 0 ):
        optimumAmountSwapping, profit, firstSwap, secondSwap = calculateProfitOptimized(
          sswapt2, sswapt1, siennat2, siennat1, maxAmountSwapping, gasFeeScrt)
      if(difference < 0 ):
        optimumAmountSwapping, profit, firstSwap, secondSwap = calculateProfitOptimized(
          siennat2, siennat1, sswapt2, sswapt1, maxAmountSwapping, gasFeeScrt)
      if(profit > lastProfit + .1 or profit < lastProfit - .1 or profit > .05):
        print(datetime.now(), "  height:", height, "  profit:", profit, "swapAmount:", optimumAmountSwapping)
        lastProfit = profit
      lastHeight = height
      if(profit > .05 and difference > 0):
        txResponse = swapSswap(
          botInfo,
          optimumAmountSwapping,
          optimumAmountSwapping + gasFeeScrt,
          firstSwap,
          nonceDictSwap,
          txEncryptionKeyDictSwap,
        )
      if(profit > .05 and difference < 0):
        txResponse = swapSienna(
          botInfo,
          optimumAmountSwapping,
          optimumAmountSwapping + gasFeeScrt,
          firstSwap,
          nonceDictSwap,
          txEncryptionKeyDictSwap,
        )
    except Exception as e:
      print(datetime.now(), "Error in TX")
      print(traceback.format_exc())
      print( e )
    try:
      if( txResponse != ""):
        if(not txResponse or txResponse.is_tx_error()):
          print(datetime.now(), "Failed")
        else:
          runningProfit += profit
          print(datetime.now(), "Success! Running profit:", runningProfit)
        recordTx(botInfo, config[sys.argv[1]]["logLocation"], optimumAmountSwapping, (siennaRatio + sswapRatio)/2)
        #scrtBal = int(botInfo.client.bank.balance(botInfo.accAddr).to_data()[0]["amount"]) * 10**-6
      botInfo.sequence = botInfo.wallet.sequence()
      nonceDictSwap, txEncryptionKeyDictSwap = generateTxEncryptionKeys(botInfo.client)
      nonceDictQuery, txEncryptionKeyDictQuery = await generateTxEncryptionKeysAsync(botInfo.asyncClient)
      keepLooping = True #set to false for only one run
    except Exception as e:
      print(datetime.now(), "Error in Queries")
      print(traceback.format_exc())
      print( e )
      lastLoopIsError = True
      continue

asyncio.run(main())
