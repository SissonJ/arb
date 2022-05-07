import csv
from utils import recordTx, generateTxEncryptionKeys, sync_next_block
from utils_stkd import calculateProfitStkd, swapStkd
from datetime import datetime
from BotInfo import BotInfo
from config import configStdk

def main():
  keeplooping = True
  botInfo = BotInfo(configStdk)

  maxAmount = 390

  nonceDictQuery, encryptionKeyDictQuery = generateTxEncryptionKeys(botInfo.client)
  nonceDictSwap, encryptionKeySwap = generateTxEncryptionKeys(botInfo.client)
  gasFeeScrt = (int(botInfo.fee.to_data()["gas"])/4000000)*3
  height = lastProfit = runningProfit = 0
  txResponse = ""
  profit = 0
  with open( botInfo.logs["output"], mode="a", newline="") as csv_file:
    logWriter = csv.writer(csv_file, delimiter=',')
    logWriter.writerow([datetime.now().date(), datetime.now().time(), "starting loop"])
  while keeplooping:
    try:
      height = sync_next_block(botInfo.client, height)
      txResponse = ""
      amountToSwap, profit, firstSwap, secondSwap, mintPrice = calculateProfitStkd(botInfo, maxAmount, gasFeeScrt, nonceDictQuery, encryptionKeyDictQuery)
    except Exception as e:
      with open( botInfo.logs["output"], mode="a", newline="") as csv_file:
        logWriter = csv.writer(csv_file, delimiter=',')
        logWriter.writerow([e.with_traceback()])
      continue
    if(profit > .05 ):
      txResponse = swapStkd(botInfo, amountToSwap, firstSwap, secondSwap, nonceDictSwap, encryptionKeySwap)
      with open( botInfo.logs["output"], mode="a", newline="") as csv_file:
        logWriter = csv.writer(csv_file, delimiter=',')
        logWriter.writerow([datetime.now().date(), datetime.now().time(), "attempted", nonceDictSwap["first"], nonceDictSwap["second"]])
    if(profit > lastProfit + .1 or profit < lastProfit - .1 or profit > 0):
      with open( botInfo.logs["output"], mode="a", newline="") as csv_file:
        logWriter = csv.writer(csv_file, delimiter=',')
        logWriter.writerow([datetime.now().date(), datetime.now().time(), "height:", height, "profit:", profit, "swapamount:", amountToSwap])
      lastProfit = profit
    if( txResponse != ""):
      maxAmount = recordTx(botInfo, "stkd-scrt-sscrt", amountToSwap, mintPrice) - 5
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