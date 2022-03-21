from datetime import datetime
from BotInfo import BotInfo
from secret_sdk.client.lcd.lcdclient import LCDClient
from config import config
from env import endpoint
from utils import getSSwapRatio, getSiennaRatio, calculateProfitCP, sync_next_block

def main():
  client = LCDClient(endpoint, 'secret-4')
  lastHeight = 0
  amountSwapping = 40
  gasFeeScrt = .050001 + .00027
  lastProfit = {}
  for cfg in config:
    lastProfit.update( {cfg: 0} )
  print("Starting loop")
  while True:
    lastHeight = sync_next_block(client, lastHeight)
    for cfg in config:
      botInfo = BotInfo(config[cfg])
      s1ratio, sswapt1, sswapt2 = getSSwapRatio(botInfo)
      s2ratio, siennat1, siennat2 = getSiennaRatio(botInfo)
      difference = s2ratio - s1ratio
      profit= firstSwap = secondSwap = 0
      if( difference > 0 ):
        profit, firstSwap, secondSwap = calculateProfitCP(sswapt2, sswapt1, siennat2, siennat1, amountSwapping, gasFeeScrt)
      if( difference < 0 ):
        profit, firstSwap, secondSwap = calculateProfitCP(siennat2, siennat1, sswapt2, sswapt1, amountSwapping, gasFeeScrt)
      if( profit != lastProfit[cfg]):
        print(datetime.now(), cfg , "height:", lastHeight, "profit:", profit, sep="\t")
        lastProfit[cfg] = profit

main()