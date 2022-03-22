import csv
from datetime import datetime
import sys

from BotInfo import BotInfo
from config import config
from utils import generateTxEncryptionKeys, sync_next_block, checkScrtBal, getSiennaRatio, getSSwapRatio, calculateProfit, swapSienna, swapSswap, txHandle

SSCRT_ADDRESS = 'secret1k0jntykt7e4g3y88ltc60czgjuqdy4c9e8fzek'
SSCRT_KEY = 'api_key_nE9AgouX7GVnT0+3LhAGoNmwUZ7HHRR4sUxNB+tbWW4='

def main():

  botInfo = BotInfo(config[sys.argv[1]])

  nonceDict, txEncryptionKeyDict = generateTxEncryptionKeys(botInfo.client)

  scrtBal, sscrtBal, shdBal, lastSscrtBal = 0, 0, 0, 0
  keepLooping = True
  txResponse = ""
  runningProfit = 0
  minAmountSwapping = 40 #sscrt
  maxAmountSwapping = 100
  optimumAmountSwapping = 0
  height = 0
  lastHeight = 0
  lastProfit = 0
  gasFeeScrt = int(botInfo.fee.to_data()["gas"])/4000000 + .00027
  print("Starting loop", sys.argv[1])
  while keepLooping:
    try:
      height = sync_next_block(botInfo.client, lastHeight)
      txResponse = ""
      lastSscrtBal = sscrtBal
      #scrtBal, sscrtBal, shdBal = getBalances(scrtBal, sscrtBal, shdBal)
      scrtBal = int(botInfo.client.bank.balance(botInfo.accAddr).to_data()[0]["amount"]) * 10**-6
      checkScrtBal(botInfo, scrtBal, maxAmountSwapping)
      siennaRatio, siennat1, siennat2 = getSiennaRatio(botInfo)
      sswapRatio, sswapt1, sswapt2 = getSSwapRatio(botInfo)
    except Exception as e:
      print( e )
    try:
      difference = siennaRatio - sswapRatio 
      profit= firstSwap = secondSwap = 0
      if( difference > 0 ):
        optimumAmountSwapping, profit, firstSwap, secondSwap = calculateProfit(
          sswapt2, sswapt1, siennat2, siennat1, minAmountSwapping, gasFeeScrt)
      if( difference < 0 ):
        optimumAmountSwapping, profit, firstSwap, secondSwap = calculateProfit(
          siennat2, siennat1, sswapt2, sswapt1, minAmountSwapping, gasFeeScrt)
      if(profit != lastProfit):
        print(datetime.now(), "  height:", height, "  profit:", profit)
      lastProfit = profit
      if(height != lastHeight + 1 and lastHeight != 0):
        print(datetime.now(), "blocks skipped:", height - lastHeight)
      lastHeight = height
      if(profit > 0 and difference > 0):
        txResponse = swapSswap(
          botInfo,
          optimumAmountSwapping,
          firstSwap,
          secondSwap,
          nonceDict,
          txEncryptionKeyDict,
        )
      if(profit > 0 and difference < 0):
        txResponse = swapSienna(
          botInfo,
          optimumAmountSwapping,
          firstSwap,
          secondSwap,
          nonceDict,
          txEncryptionKeyDict,
        )
      if( txResponse != ""):
        runningProfit += profit
        txHandle(config[sys.argv[1]]["logLocation"], txResponse, profit, runningProfit, lastHeight, optimumAmountSwapping)
        nonceDict, txEncryptionKeyDict = generateTxEncryptionKeys(botInfo.client)
        botInfo.sequence = botInfo.wallet.sequence()
      keepLooping = True #set to false for only one run
    except Exception as e:
      print( "ERROR in tx\n" )
      print( e )
      return

main()