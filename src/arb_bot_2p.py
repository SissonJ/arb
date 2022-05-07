import asyncio
import csv
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

  keepLooping = True
  txResponse = ""
  maxAmountSwapping = botInfo.total[0] - 5
  optimumAmountSwapping = height = lastHeight = lastProfit = 0
  lastLoopIsError = False
  gasFeeScrt = (int(botInfo.fee.to_data()["gas"])/4000000)*2.5
  with open( botInfo.logs["output"], mode="a", newline="") as csv_file:
    logWriter = csv.writer(csv_file, delimiter=',')
    logWriter.writerow([datetime.now().date(), datetime.now().time(),"Starting loop"])
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
      with open( botInfo.logs["output"], mode="a", newline="") as csv_file:
        logWriter = csv.writer(csv_file, delimiter=',')
        logWriter.writerow([datetime.now().date(), datetime.now().time(),"Error in Queries"])
        logWriter.writerow([e.with_traceback()])
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
      if(profit > lastProfit + .1 or profit < lastProfit - .1 or profit > .05):
        with open( botInfo.logs["output"], mode="a", newline="") as csv_file:
          logWriter = csv.writer(csv_file, delimiter=',')
          logWriter.writerow([datetime.now().date(), datetime.now().time(), "height:", height, "profit:", profit, "swapAmount:", optimumAmountSwapping])
        lastProfit = profit
    except Exception as e:
      with open( botInfo.logs["output"], mode="a", newline="") as csv_file:
        logWriter = csv.writer(csv_file, delimiter=',')
        logWriter.writerow([datetime.now().date(), datetime.now().time(),"Error in TX"])
        logWriter.writerow([e.with_traceback()])
    try:
      if( txResponse != ""):
        with open( botInfo.logs["output"], mode="a", newline="") as csv_file:
          logWriter = csv.writer(csv_file, delimiter=',')
          logWriter.writerow([datetime.now().date(), datetime.now().time(),"Attempted", nonceDictSwap["first"], nonceDictSwap["second"]])
        maxAmountSwapping = recordTx(botInfo, sys.argv[1], optimumAmountSwapping, (siennaRatio + sswapRatio)/2)
        #scrtBal = int(botInfo.client.bank.balance(botInfo.accAddr).to_data()[0]["amount"]) * 10**-6
      botInfo.sequence = botInfo.wallet.sequence()
      nonceDictSwap, txEncryptionKeyDictSwap = generateTxEncryptionKeys(botInfo.client)
      nonceDictQuery, txEncryptionKeyDictQuery = await generateTxEncryptionKeysAsync(botInfo.asyncClient)
      keepLooping = True #set to false for only one run
    except Exception as e:
      with open( botInfo.logs["output"], mode="a", newline="") as csv_file:
        logWriter = csv.writer(csv_file, delimiter=',')
        logWriter.writerow([datetime.now().date(), datetime.now().time(),"Error in Queries"])
        logWriter.writerow([e.with_traceback()])
      lastLoopIsError = True
      continue

asyncio.run(main())
