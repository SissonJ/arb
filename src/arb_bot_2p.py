import asyncio
import csv
from datetime import datetime
import sys
import time
import traceback
from secret_sdk.exceptions import LCDResponseError

from BotInfo import BotInfo
from config import config
from utils import calculateProfitOptimized, log_traceback, sync_next_block
from utils import swapSienna, swapSswap, recordTx, generateTxEncryptionKeys
from utils_async import runAsyncQueries, generateTxEncryptionKeysAsync

from env import nonce

async def main():

  botInfo = BotInfo(config[sys.argv[1]])

  txEncryptionKey = await botInfo.asyncClient.utils.get_tx_encryption_key(nonce)
  nonceDict, txEncryptionKeyDict = generateTxEncryptionKeys(botInfo.client)

  keepLooping = True
  txResponse = ""
  maxAmountSwapping = botInfo.total[0] - 5
  optimumAmountSwapping = height = lastHeight = lastProfit = 0
  lastLoopIsError = False
  gasFeeScrt = (int(botInfo.fee.to_data()["gas"])/40000000)*2
  with open( botInfo.logs["output"], mode="a", newline="") as csv_file:
    logWriter = csv.writer(csv_file, delimiter=',')
    logWriter.writerow([datetime.now().date(), datetime.now().time(),"Starting loop"])
  while keepLooping:
    if lastLoopIsError:
      botInfo.sequence = botInfo.wallet.sequence()
      nonceDict, txEncryptionKeyDict = generateTxEncryptionKeys(botInfo.client)
      lastLoopIsError = False
      continue
    try:
      height = sync_next_block(botInfo.client, lastHeight)
      start_time = time.time()
      lastHeight = height
      txResponse = ""
      sswapRatio, sswapt1, sswapt2,siennaRatio, siennat1, siennat2 = await runAsyncQueries(
        botInfo, 
        nonce,
        txEncryptionKey,
      )
    except Exception as e:
      with open( botInfo.logs["output"], mode="a", newline="") as csv_file:
        logWriter = csv.writer(csv_file, delimiter=',')
        logWriter.writerow([datetime.now().date(), datetime.now().time(),"Error in Queries", e])
        if( not isinstance(e, LCDResponseError)):
          traceback = log_traceback(e)
          for rows in traceback:
            logWriter.writerow([rows])
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
      if( profit > .01 and difference > 0):
        txResponse = await swapSswap(
          botInfo,
          optimumAmountSwapping,
          optimumAmountSwapping + gasFeeScrt,
          firstSwap,
          nonceDict,
          txEncryptionKeyDict,
        )
      if( profit > .01 and difference < 0):
        txResponse = await swapSienna(
          botInfo,
          optimumAmountSwapping,
          optimumAmountSwapping + gasFeeScrt,
          firstSwap,
          nonceDict,
          txEncryptionKeyDict,
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
        traceback = log_traceback(e)
        for rows in traceback:
          logWriter.writerow([rows])
    try:
      if( txResponse != ""):
        height = sync_next_block(botInfo.client, lastHeight)
        lastHeight = height
        with open( botInfo.logs["output"], mode="a", newline="") as csv_file:
          logWriter = csv.writer(csv_file, delimiter=',')
          logWriter.writerow([datetime.now().date(), datetime.now().time(),"Attempted", time.time()-start_time ])
        maxAmountSwapping = recordTx(botInfo, sys.argv[1], optimumAmountSwapping, (siennaRatio + sswapRatio)/2, "arb_v3")
        #scrtBal = int(botInfo.client.bank.balance(botInfo.accAddr).to_data()[0]["amount"]) * 10**-6
      botInfo.sequence = botInfo.wallet.sequence()
      nonceDict, txEncryptionKeyDict = generateTxEncryptionKeys(botInfo.client)
      keepLooping = True #set to false for only one run
    except Exception as e:
      with open( botInfo.logs["output"], mode="a", newline="") as csv_file:
        logWriter = csv.writer(csv_file, delimiter=',')
        logWriter.writerow([datetime.now().date(), datetime.now().time(),"Error in Queries"])
        if( not isinstance(e, LCDResponseError)):
          traceback = log_traceback(e)
          for rows in traceback:
            logWriter.writerow([rows])
      lastLoopIsError = True
      keepLooping = True
      continue

asyncio.run(main())
