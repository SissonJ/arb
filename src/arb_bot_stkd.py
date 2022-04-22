from secret_sdk.client.lcd.lcdclient import LCDClient
from utils import calculateProfitStdk, recordTx, swapStkd, optimumSwapAmountStdk,generateTxEncryptionKeys, sync_next_block
#from utils import getStkdPrice
from datetime import datetime
from time import time
from BotInfo import BotInfo
from config import configStdk
from env import endpoint
import time

def getStkdPrice(client: LCDClient):
  res = client.wasm.contract_query(
    "secret1k6u0cy4feepm6pehnz804zmwakuwdapm69tuc4", 
    { "staking_info": { "time": round(time.time()) } }
  )
  return float(res["staking_info"]["price"])*10**-6

def main():
  keeplooping = True
  botInfo = BotInfo(configStdk)

  maxAmount = 200

  nonceDictQuery, encryptionKeyDictQuery = generateTxEncryptionKeys(botInfo.client)
  nonceDictSwap, encryptionKeySwap = generateTxEncryptionKeys(botInfo.client)
  gasFeeScrt = (int(botInfo.fee.to_data()["gas"])/4000000)*3
  height = lastProfit = runningProfit = 0
  txResponse = ""
  profit = 0
  #client = LCDClient(endpoint, "secret-4")
  #print(getStkdPrice(client))
  #print(client.wasm.contract_query(
  #  "secret155ycxc247tmhwwzlzalakwrerde8mplhluhjct",
  #  'pair_info',
  #))
  print("starting loop")
  while keeplooping:
    try:
      height = sync_next_block(botInfo.client, height)
      txResponse = ""
      amountToSwap, profit, firstSwap, secondSwap, mintPrice = calculateProfitStdk(botInfo, maxAmount, gasFeeScrt, nonceDictQuery, encryptionKeyDictQuery)
    except:
      pass
    if(profit > 0 ):
      txResponse = swapStkd(botInfo, amountToSwap, firstSwap, secondSwap, nonceDictSwap, encryptionKeySwap)
    if(profit != lastProfit):
       print(datetime.now(), "  height:", height, "  profit:", profit)
    lastProfit = profit
    if( txResponse != ""):
      if(not txResponse or txResponse.is_tx_error()):
        print(datetime.now(), "Failed" )
      else:
        runningProfit += profit
        print(datetime.now(), "Success! Running profit:", runningProfit)
      recordTx(botInfo, configStdk["logLocation"], amountToSwap, mintPrice)
      scrtBal = int(botInfo.client.bank.balance(botInfo.accAddr).to_data()[0]["amount"]) * 10**-6
      if(scrtBal < 1):
        break
    nonceDictSwap, encryptionKeySwap = generateTxEncryptionKeys(botInfo.client)
    botInfo.sequence = botInfo.wallet.sequence()
    nonceDictQuery, encryptionKeyDictQuery = generateTxEncryptionKeys(botInfo.client)
    botInfo.sequence = botInfo.wallet.sequence()
    keeplooping = True
  return

main()