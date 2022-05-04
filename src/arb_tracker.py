import asyncio
from datetime import datetime
import time
from secret_sdk.client.lcd.lcdclient import LCDClient

from config import config, configStdk

from BotInfo import BotInfo
from env import endpoint
from utils import getSSwapRatio, getSiennaRatio, calculateProfit, sync_next_block, optimumProfit
from utils_stkd import arbTrackerStkd

black_list = ["sscrt-swbtc-config", "sscrt-sxmr-config", "sscrt-sienna-config"]

async def main():
  client = LCDClient(endpoint, 'secret-4')
  lastHeight = 0
  amountSwapping = 40
  gasFeeScrt = 0
  lastProfit = {}
  lastProfitStkd = 0
  for cfg in config:
    lastProfit.update( {cfg: 0} )
  print("Starting loop")
  while True:
    time.sleep(5)
    lastHeight = sync_next_block(client, lastHeight)
    for cfg in config:
      if( cfg in black_list):
        continue
      botInfo = BotInfo(config[cfg])
      gasFeeScrt = (int(botInfo.fee.to_data()["gas"])/4000000)*2.5
      s1ratio, sswapt1, sswapt2 = getSSwapRatio(botInfo)
      s2ratio, siennat1, siennat2 = getSiennaRatio(botInfo)
      difference = s2ratio - s1ratio
      profit= firstSwap = secondSwap = amountToSwap = 0
      printval1, printval2, printval3, printval4 = 0, 0, 0, 0
      if( difference > 0 ):
        amountToSwap, profit, firstSwap, secondSwap = calculateProfit(sswapt2, sswapt1, siennat2, siennat1, amountSwapping, gasFeeScrt)
        printval1, printval2, printval3, printval4 = sswapt2, sswapt1, siennat2, siennat1
      if( difference < 0 ):
        amountToSwap, profit, firstSwap, secondSwap = calculateProfit(siennat2, siennat1, sswapt2, sswapt1, amountSwapping, gasFeeScrt)
        printval1, printval2, printval3, printval4 = siennat2, siennat1, sswapt2, sswapt1
      if( profit != lastProfit[cfg]):
        print(printval1, printval2, printval3, printval4, amountToSwap)
        print(optimumProfit(printval1, printval2, printval4, printval3))
        print(datetime.now(), "height", lastHeight, cfg , "profit:", profit, sep="\t")
        print("sswap:", s1ratio, "sienna", s2ratio )
        print()
        lastProfit[cfg] = profit
      await botInfo.asyncClient.session.close()
    if( "sscrt-stkd-config" in black_list ):
      continue
    botInfoStkd = BotInfo(configStdk)
    profitStkd, siesscrt, siestkd, sieprice, mint, swapamount, optimum = arbTrackerStkd(botInfoStkd, {"first":None, "second":None}, {"first":None, "second":None})
    if(profitStkd > lastProfitStkd + .01 or profitStkd < lastProfitStkd - .01 or profitStkd > 0):
      print( siesscrt, siestkd, swapamount )
      print( optimum )
      print(datetime.now(), "height", lastHeight, "sscrt-stkd-config" , "profit:", profitStkd, sep="\t")
      print("sienna:", sieprice, "mint:", mint)
      print()
      lastProfitStkd = profitStkd
    await botInfoStkd.asyncClient.session.close()

asyncio.run(main())