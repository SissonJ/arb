import csv
import json
from datetime import datetime
import time
from secret_sdk.client.lcd import LCDClient
from secret_sdk.key.mnemonic import MnemonicKey
from secret_sdk.core.wasm import MsgExecuteContract
from secret_sdk.core.auth import StdFee
import base64
from secret_sdk.core.bank import MsgSend

mk = MnemonicKey(mnemonic="easy oxygen bone search trophy soccer video float tiny rack fragile cactus uphold acoustic carbon warm hand pilot topic session because seed magnet domain")
#client = LCDClient('https://api.scrt.network', 'secret-4')
client = LCDClient('https://lcd.secret.llc', 'secret-4')

SSWAP_SSCRT_SHD_PAIR = "secret1wwt7nh3zyzessk8c5d98lpfsw79vzpsnerj6d0"
SSWAP_SSCRT_SIENNA_PAIR = "secret1rxrg8mp4qm5703ccz26lgh8hx7gpnkujrn6qcr"
SSWAP_QUERY = { 'pool': {} }

SIENNA_SSCRT_SHD_PAIR = "secret1drm0dwvewjyy0rhrrw485q4f5dnfm6j25zgfe5"
SIENNA_SSCRT_SIENNA_PAIR = "secret1guphvlle6wzjswda3ceuuu6m6ty36t6w5jn9rv"
SIENNA_SIENNA_SHD_PAIR = "secret1kp56t9dhd84453ph8sryjnly6gt7k8vur2ahzu"
SIENNA_QUERY = 'pair_info'

SSCRT_ADRESS = 'secret1k0jntykt7e4g3y88ltc60czgjuqdy4c9e8fzek'
SSCRT_KEY = 'api_key_nE9AgouX7GVnT0+3LhAGoNmwUZ7HHRR4sUxNB+tbWW4='

SHD_ADRESS = 'secret1qfql357amn448duf5gvp9gr48sxx9tsnhupu3d'
SHD_KEY = 'api_key_xSmcfnyU8z5750bZSC9icFYUz6whMLIUeEloEqORQ7M='

SIENNA_ADDRESS = "secret1rgm2m5t530tdzyd99775n6vzumxa5luxcllml4"

wallet = client.wallet(mk)
fee = StdFee(200001, "050001uscrt")

def getBalances(scrtBal, sscrtBal, shdBal):
  scrtBalRes = client.bank.balance(mk.acc_address)
  sscrtBalRes = client.wasm.contract_query(SSCRT_ADRESS, { "balance": { "address": mk.acc_address, "key": SSCRT_KEY }})
  shdBalRes = client.wasm.contract_query(SHD_ADRESS, { "balance": { "address": mk.acc_address, "key": SHD_KEY }})
  scrtBal, sscrtBal, shdBal = int(scrtBalRes.to_data()[0]["amount"]) * 10**-6, float(sscrtBalRes['balance']['amount'])* 10**-6, float(shdBalRes['balance']['amount'])* 10**-8
  return scrtBal, sscrtBal, shdBal

def constantProduct(poolBuy, poolSell, x):
  out = -(poolBuy * poolSell)/(poolSell + x) + poolBuy
  return out

def getSiennaShdSscrtRatio():
  siennaInfo = client.wasm.contract_query(SIENNA_SSCRT_SHD_PAIR, SIENNA_QUERY)
  uShdAmount, uSscrtAmount = float(siennaInfo['pair_info']['amount_0']) * 10**-2, int(siennaInfo['pair_info']['amount_1'])
  return uSscrtAmount/uShdAmount, uShdAmount, uSscrtAmount

def getSiennaSscrtSiennaRatio():
  siennaInfo = client.wasm.contract_query(SIENNA_SSCRT_SIENNA_PAIR, SIENNA_QUERY)
  uSiennaAmount, uSscrtAmount = int(siennaInfo['pair_info']['amount_0']), int(siennaInfo['pair_info']['amount_1'])
  return uSiennaAmount/uSscrtAmount, uSscrtAmount, uSiennaAmount

def getSiennaShdSiennaRatio():
  siennaInfo = client.wasm.contract_query(SIENNA_SIENNA_SHD_PAIR, SIENNA_QUERY)
  uSiennaAmount, uShdAmount = float(siennaInfo['pair_info']['amount_0'])* 10**-2, int(siennaInfo['pair_info']['amount_1'])
  return uSiennaAmount/uShdAmount, uShdAmount, uSiennaAmount

def getSSwapShdSscrtRatio():
  sswapInfo = client.wasm.contract_query(SSWAP_SSCRT_SHD_PAIR, SSWAP_QUERY)
  uSscrtAmount, uShdAmount = float(sswapInfo['assets'][0]['amount'])* 10**-2, int(sswapInfo['assets'][1]['amount'])
  return uSscrtAmount/uShdAmount, uShdAmount, uSscrtAmount

def getSSwapSscrtSiennaRatio():
  sswapInfo = client.wasm.contract_query(SSWAP_SSCRT_SIENNA_PAIR, SSWAP_QUERY)
  uSscrtAmount, uSiennaAmount = int(sswapInfo['assets'][0]['amount']), int(sswapInfo['assets'][1]['amount'])
  return uSiennaAmount/uSscrtAmount, uSscrtAmount, uSiennaAmount

def calculateProfitCP(s1Buy, s1Sell, s2Buy, s2Sell, s3Buy, s3Sell, amountSwapped, gasFeeScrt):
  firstSwap = constantProduct(s1Buy, s1Sell, amountSwapped*.996)
  secondSwap = constantProduct(s2Buy, s2Sell, firstSwap*.997) * .999
  thirdSwap = constantProduct(s3Buy, s3Sell, secondSwap * .997) * .999

  profit = thirdSwap - amountSwapped - gasFeeScrt
  return profit, firstSwap, secondSwap, thirdSwap 

def swapSienna(sscrtBal, firstSwap, secondSwap):
  sscrtBalStr = str(int(sscrtBal * 10 ** 6))
  firstSwapStr = str(int(firstSwap * 10 ** 8))
  secondSwapStr = str(int(secondSwap * 10 ** 6))

  msgSienna = json.dumps({"swap":{"to":None,"expected_return":firstSwapStr}})
  encryptedMsgSienna = str( base64.b64encode(msgSienna.encode("utf-8")), "utf-8")
  handleMsgSienna = { "send": {"recipient": SIENNA_SSCRT_SHD_PAIR, "amount": sscrtBalStr, "msg": encryptedMsgSienna }}
  msgExecuteSienna = client.wasm.contract_execute_msg(mk.acc_address, SSCRT_ADRESS, handleMsgSienna, [])
  
  msgSswap = json.dumps({"swap":{"expected_return":secondSwapStr}})
  encryptedMsgSswap = str( base64.b64encode(msgSswap.encode("utf-8")), "utf-8")
  handleMsgSswap = { "send": {"recipient": SSWAP_SSCRT_SHD_PAIR, "amount": firstSwapStr, "msg": encryptedMsgSswap }}
  msgExecuteSswap = client.wasm.contract_execute_msg(mk.acc_address, SHD_ADRESS, handleMsgSswap, [])

  #wallet.execute_tx(SHD_ADRESS, handleMsg) #OTHER METHOD
  
  tx = wallet.create_and_sign_tx([msgExecuteSienna, msgExecuteSswap], fee)
  try:
    res = client.tx.broadcast(tx)
  except:
    print("BROADCAST TX ERROR")
    return False
  return res

def swapSswap(sscrtBal, firstSwap, secondSwap):
  sscrtBalStr = str(int(sscrtBal * 10 ** 6))
  firstSwapStr = str(int(firstSwap * 10 ** 8))
  secondSwapStr = str(int(secondSwap * 10 ** 6))

  msgSswap = json.dumps({"swap":{"expected_return":firstSwapStr}})
  encryptedMsgSswap = str( base64.b64encode(msgSswap.encode("utf-8")), "utf-8")
  handleMsgSswap = { "send": {"recipient": SSWAP_SSCRT_SHD_PAIR, "amount": sscrtBalStr, "msg": encryptedMsgSswap }}
  msgExecuteSswap = client.wasm.contract_execute_msg(mk.acc_address, SSCRT_ADRESS, handleMsgSswap, [])

  msgSienna = json.dumps({"swap":{"to":None,"expected_return":secondSwapStr}})
  encryptedMsgSienna = str( base64.b64encode(msgSienna.encode("utf-8")), "utf-8")
  handleMsgSienna = { "send": {"recipient": SIENNA_SSCRT_SHD_PAIR, "amount": firstSwapStr, "msg": encryptedMsgSienna }}
  msgExecuteSienna = client.wasm.contract_execute_msg(mk.acc_address, SHD_ADRESS, handleMsgSienna, [])

  #res = wallet.execute_tx(SSCRT_ADRESS, handleMsgSswap) #OTHER METHOD

  tx = wallet.create_and_sign_tx([msgExecuteSswap, msgExecuteSienna], fee)
  try:
    res = client.tx.broadcast(tx)
  except:
    print("BROADCAST TX ERROR")
    return False
  return res

def swapSswapSswap(amountSwapping, firstSwap, secondSwap, thirdSwap):
  return

def swapSswapSienna(amountSwapping, firstSwap, secondSwap, thirdSwap):
  return

def swapSiennnaSswap(amountSwapping, firstSwap, secondSwap, thirdSwap):
  return

def swapSiennaSienna(amountSwapping, firstSwap, secondSwap, thirdSwap):
  return

def buyScrt(scrtBal):
  sscrtBalRes = client.wasm.contract_query(SSCRT_ADRESS, { "balance": { "address": mk.acc_address, "key": SSCRT_KEY }})
  redeemAmount = int(sscrtBalRes['balance']['amount']) - scrtBal * 10 ** 6
  handleMsg = {"redeem":{"amount":str(redeemAmount)}}
  res = wallet.execute_tx(SSCRT_ADRESS, handleMsg)
  return res

def checkScrtBal(scrtBal, tradeAmount):
  if (scrtBal < 1 ):
    print("NOT ENOUGH SCRT")
    buyScrt(tradeAmount)
    return True
  return True

def checkLastTradeProfitable(sscrtBal, lastSscrtBal):
  if( not (sscrtBal == lastSscrtBal) and (sscrtBal - lastSscrtBal < .0425 + .00027) ):
    print("NOT ENOUGH PROFIT")
    return False 
  return True

def txHandle(txResponse, profit, logWriter, runningProfit):
  logWriter.writerow([txResponse.to_json()])
  print(txResponse.to_json())
  if(txResponse.is_tx_error()):
    print( "ERROR" )
    logWriter.writerow([datetime.now(), "Error", txResponse.txhash])
    print(txResponse.txhash)
    return False

  print(txResponse.txhash)
  logWriter.writerow([datetime.now(), "profit", str(profit), "runningTotal", str(runningProfit)])

  return True

def block_height(secret):
  block_info = secret.tendermint.block_info()
  height = block_info['block']['header']['height']
  return int(height)

def sync_next_block(secret, height=0):
  while True:
    new_height = block_height(secret)
    if new_height > height:
      return new_height
    time.sleep(.5)
        

def main():
  txLog = open("shd-scrt-pair-log.csv", "a")
  logWriter = csv.writer(txLog, delimiter=' ')
  scrtBal, sscrtBal, shdBal, lastSscrtBal = 0, 0, 0, 0
  keepLooping = True
  txResponse = ""
  runningProfit = 0
  amountSwapping = 40 #sscrt
  lastHeight = 0
  gasFeeScrt = .050001 + .00027
  print("Starting main loop")
  while keepLooping:
    try:
      lastHeight = sync_next_block(client, lastHeight)
      #print( "Height: ", lastHeight )
      #print(datetime.now())
      txResponse = ""
      lastSscrtBal = sscrtBal
      #scrtBal, sscrtBal, shdBal = getBalances(scrtBal, sscrtBal, shdBal)
      scrtBal = int(client.bank.balance(mk.acc_address).to_data()[0]["amount"]) * 10**-6
      keepLooping = checkScrtBal(scrtBal, amountSwapping) and checkLastTradeProfitable(sscrtBal, lastSscrtBal)
      siennaRatio, siennaShd, siennaSscrt = getSiennaRatio()
      sswapRatio, sswapShd, sswapSscrt = getSSwapRatio()
    except:
      print("ERROR in queries\n")
      continue
    try:
      difference = siennaRatio - sswapRatio 
      #print("Sienna: ", siennaRatio)
      #print(" SSwap: ", sswapRatio)
      #print("  Diff: ", difference)
      profit= firstSwap = secondSwap = 0
      if( difference > 0 ):
        profit, firstSwap, secondSwap = calculateProfitCP(sswapShd, sswapSscrt, siennaShd, siennaSscrt, amountSwapping, gasFeeScrt)
        #print("profit: ", profit)
      if( difference < 0 ):
        profit, firstSwap, secondSwap = calculateProfitCP(siennaShd, siennaSscrt, sswapShd, sswapSscrt, amountSwapping, gasFeeScrt)
        #print("profit: ", profit)
      if( profit > 0 and difference > 0):
        print( "Height: ", lastHeight )
        print(datetime.now())
        print("profit: ", profit)
        txResponse = swapSswap(amountSwapping, firstSwap, secondSwap)
      if( profit > 0 and difference < 0):
        print( "Height: ", lastHeight )
        print(datetime.now())
        print("profit: ", profit)
        txResponse = swapSienna(amountSwapping, firstSwap, secondSwap)
      if( txResponse != ""):
        runningProfit += profit
        txHandle(txResponse, profit, logWriter, runningProfit)
    except:
      print( "ERROR in tx\n" )
      continue
  print( runningProfit )
  txLog.close()

#main()

def testFunction():
  #txLog = open("tx_log.csv", "a")
  #logWriter = csv.writer(txLog, delimiter=' ')
  #logWriter.writerow([datetime.now(), "Hello2", "this2"])
  #txLog.close()
  #amountSwapping = 40
  #siennaRatio, siennaShd, siennaSscrt = getSiennaRatio()
  #sswapRatio, sswapShd, sswapSscrt = getSSwapRatio()
  #difference = siennaRatio - sswapRatio 
  #if( difference > 0 ):
  #  profit, firstSwap, secondSwap = calculateProfitCP(sswapShd, sswapSscrt, siennaShd, siennaSscrt, amountSwapping)
  #  print("profit: ", profit, firstSwap, secondSwap)
  #if( difference < 0 ):
  #  profit, firstSwap, secondSwap = calculateProfitCP(siennaShd, siennaSscrt, sswapShd, sswapSscrt, amountSwapping)
  #  print("profit: ", profit, firstSwap, secondSwap)
  #res = swapSswap(40, firstSwap, secondSwap)
  #res = buyScrt(amountSwapping)
  #print(res.to_json())
  sssRatio, siennaUShd, siennaUSienna = getSiennaShdSiennaRatio()
  ssRatio, siennaUSscrt, siennaUSinna2 = getSiennaSscrtSiennaRatio()
  sRatio, sswapUshd, sswapUsscrt = getSSwapShdSscrtRatio()
  profit, firstSwap, secondSwap, thirdSwap = calculateProfitCP(siennaUSinna2, siennaUSscrt, siennaUShd, siennaUSienna, sswapUsscrt, sswapUshd, 40, 0)
  print(sssRatio, ssRatio, sRatio)
  print(profit)

testFunction()

#wallet = client.wallet(mk)

#tx = wallet.create_and_sign_tx(
#    msgs=[MsgSend(
#        wallet.key.acc_address,
#        "secret1kq56y5s8tfawa0k6gv9np86r4wtm8q86zl3n5v",
#        "1000000uscrt" # send 1 scrt
#    )],
#    memo="test transaction!",
#    fee=StdFee(200000, "120000uscrt")
#)




