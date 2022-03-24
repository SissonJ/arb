from secret_sdk.client.lcd.lcdclient import LCDClient
from utils import calculateProfitStdk, swapStkd, getStkdPrice
from datetime import datetime
from time import time
from BotInfo import BotInfo
from config import configStdk
from env import testnet
import time


def main():
  keeplooping = True
  botInfo = BotInfo(configStdk)
  client = LCDClient(testnet, "pulsar-2")
  res = client.wasm.contract_query(configStdk["tokenAddrs"]["token2"], { "staking_info": { "time": round(time.time()) } })
  print(float(res["staking_info"]["price"])*10**-6)
  while keeplooping:
    amountToSwap, profit, firstSwap, secondSwap = calculateProfitStdk(botInfo)
    if( profit > 0 ):
      swapStkd(botInfo, amountToSwap, firstSwap, secondSwap)
    keeplooping = False
  return

main()