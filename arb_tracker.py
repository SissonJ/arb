from datetime import datetime
from BotInfo import BotInfo
from secret_sdk.client.lcd.lcdclient import LCDClient
from config import config
from env import endpoint
from utils import getSSwapRatio, getSiennaRatio, calculateProfit, sync_next_block

def main():
  client = LCDClient(endpoint, 'secret-4')
  lastHeight = 0
  amountSwapping = 40
  gasFeeScrt = 0
  lastProfit = {}
  for cfg in config:
    lastProfit.update( {cfg: 0} )
  print("Starting loop")
  while True:
    lastHeight = sync_next_block(client, lastHeight)
    for cfg in config:
      botInfo = BotInfo(config[cfg])
      gasFeeScrt = int(botInfo.fee.to_data()["gas"])/4000000 + .00027
      s1ratio, sswapt1, sswapt2 = getSSwapRatio(botInfo)
      s2ratio, siennat1, siennat2 = getSiennaRatio(botInfo)
      difference = s2ratio - s1ratio
      profit= firstSwap = secondSwap = amountToSwap = 0
      if( difference > 0 ):
        amountToSwap, profit, firstSwap, secondSwap = calculateProfit(sswapt2, sswapt1, siennat2, siennat1, amountSwapping, gasFeeScrt)
      if( difference < 0 ):
        amountToSwap, profit, firstSwap, secondSwap = calculateProfit(siennat2, siennat1, sswapt2, sswapt1, amountSwapping, gasFeeScrt)
      if( profit != lastProfit[cfg]):
        print(datetime.now(), "height", lastHeight)
        print( cfg , "profit:", profit, "amount to swap", amountToSwap, sep="\t")
        print()
        lastProfit[cfg] = profit

main()