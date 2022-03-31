from secret_sdk.client.lcd.lcdclient import LCDClient
from utils import calculateProfitStdk, recordTx, swapStkd, optimumSwapAmountStdk,generateTxEncryptionKeys, sync_next_block
#from utils import getStkdPrice
from datetime import datetime
from time import time
from BotInfo import BotInfo
from config import configStdk
from env import testnet
import time

def getStkdPrice(client: LCDClient):
  res = client.wasm.contract_query(
    "secret1pz76z6dfekq2pcnymmz68dtwu7qtuh6s0ppf7z", 
    { "staking_info": { "time": round(time.time()) } }
  )
  return float(res["staking_info"]["price"])*10**-6

def main():
  keeplooping = True
  botInfo = BotInfo(configStdk)

  maxAmount = 200

  nonceDictQuery, encryptionKeyDictQuery = generateTxEncryptionKeys(botInfo.client)
  nonceDictSwap, encryptionKeyDictSwap = generateTxEncryptionKeys(botInfo.client)
  gasFeeScrt = (int(botInfo.fee.to_data()["gas"])/4000000)*2.5
  height = lastProfit = runningProfit = 0
  txResponse = ""
  #client = LCDClient(testnet, "pulsar-2")
  #print(getStkdPrice(client))
  while keeplooping:
    #add try catch after degugging
    height = sync_next_block(botInfo.client, height)
    txResponse = ""
    amountToSwap, profit, firstSwap, secondSwap, mintPrice = calculateProfitStdk(botInfo, maxAmount, gasFeeScrt, nonceDictQuery, encryptionKeyDictQuery)
    if(True or profit > 0 ): #remove after testing
      txResponse = swapStkd(
        botInfo, 
        amountToSwap, 
        amountToSwap + (gasFeeScrt/mintPrice), 
        firstSwap,
        nonceDictSwap, 
        encryptionKeyDictSwap
      )
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
      nonceDictSwap, encryptionKeyDictSwap = generateTxEncryptionKeys(botInfo.client)
      scrtBal = int(botInfo.client.bank.balance(botInfo.accAddr).to_data()[0]["amount"]) * 10**-6
      if(scrtBal < 1):
        break
    nonceDictQuery, encryptionKeyDictQuery = generateTxEncryptionKeys(botInfo.client)
    botInfo.sequence = botInfo.wallet.sequence()
    keeplooping = False
  return

main()