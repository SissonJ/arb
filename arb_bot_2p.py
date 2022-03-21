import csv
from datetime import datetime
import sys

from BotInfo import BotInfo
from config import config
from utils import generateTxEncryptionKeys, sync_next_block, checkScrtBal, getSiennaRatio, getSSwapRatio, calculateProfitCP, swapSienna, swapSswap, txHandle

SSCRT_ADDRESS = 'secret1k0jntykt7e4g3y88ltc60czgjuqdy4c9e8fzek'
SSCRT_KEY = 'api_key_nE9AgouX7GVnT0+3LhAGoNmwUZ7HHRR4sUxNB+tbWW4='

def main():
  txLog = open(config[sys.argv[1]]["logLocation"], "a")
  logWriter = csv.writer(txLog, delimiter=' ')

  botInfo = BotInfo(config[sys.argv[1]])

  nonceDict, txEncryptionKeyDict = generateTxEncryptionKeys(botInfo.client)

  scrtBal, sscrtBal, shdBal, lastSscrtBal = 0, 0, 0, 0
  keepLooping = True
  txResponse = ""
  runningProfit = 0
  amountSwapping = 40 #sscrt
  height = 0
  lastHeight = 0
  lastProfit = 0
  gasFeeScrt = .050001 + .00027
  print("Starting loop", sys.argv[1])
  while keepLooping:
    try:
      height = sync_next_block(botInfo.client, lastHeight)
      txResponse = ""
      lastSscrtBal = sscrtBal
      #scrtBal, sscrtBal, shdBal = getBalances(scrtBal, sscrtBal, shdBal)
      scrtBal = int(botInfo.client.bank.balance(botInfo.accAddr).to_data()[0]["amount"]) * 10**-6
      checkScrtBal(botInfo, scrtBal, amountSwapping)
      siennaRatio, siennat1, siennat2 = getSiennaRatio(botInfo)
      sswapRatio, sswapt1, sswapt2 = getSSwapRatio(botInfo)
    except Exception as e:
      print( e )
    try:
      difference = siennaRatio - sswapRatio 
      profit= firstSwap = secondSwap = 0
      if( difference > 0 ):
        profit, firstSwap, secondSwap = calculateProfitCP(sswapt2, sswapt1, siennat2, siennat1, amountSwapping, gasFeeScrt)
      if( difference < 0 ):
        profit, firstSwap, secondSwap = calculateProfitCP(siennat2, siennat1, sswapt2, sswapt1, amountSwapping, gasFeeScrt)
      if(profit != lastProfit):
        print(datetime.now(), "  height:", height, "  profit:", profit)
      lastProfit = profit
      if(height != lastHeight + 1 and lastHeight != 0):
        print(datetime.now(), "blocks skipped:", height - lastHeight)
      lastHeight = height
      if(profit > 0 and difference > 0):
        txResponse = swapSswap(
          botInfo,
          amountSwapping,
          firstSwap,
          secondSwap,
          nonceDict,
          txEncryptionKeyDict,
        )
      if(profit > 0 and difference < 0):
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
        txHandle(txResponse, profit, logWriter, runningProfit, lastHeight)
        nonceDict, txEncryptionKeyDict = generateTxEncryptionKeys(botInfo.client)
        botInfo.sequence = botInfo.wallet.sequence()
    except Exception as e:
      print( "ERROR in tx\n" )
      print( e )
      return
  print( runningProfit )
  txLog.close()

main()