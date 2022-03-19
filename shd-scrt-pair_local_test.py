import csv
import json
from datetime import datetime
import time

from secret_sdk.client.lcd import LCDClient
from secret_sdk.key.mnemonic import MnemonicKey
from secret_sdk.core.wasm import MsgExecuteContract
from secret_sdk.core.auth import StdFee
from secret_sdk.core.auth import StdSignMsg
from miscreant.aes.siv import SIV
import base64
from cryptography.hazmat.primitives import serialization
from tomlkit import boolean

mkSeed = "easy oxygen bone search trophy soccer video float tiny rack fragile cactus uphold acoustic carbon warm hand pilot topic session because seed magnet domain"
mk = MnemonicKey(mnemonic=mkSeed)
#client = LCDClient('https://api.scrt.network', 'secret-4')
client = LCDClient('https://lcd.secret.llc', 'secret-4')
wallet = client.wallet(mk)
fee = StdFee(200001, "050001uscrt")
accountNumber, sequence = wallet.account_number(), wallet.sequence()
nonceDict = {}
txEncryptionKeyDict = {}
seed = client.utils.generate_new_seed()
privkey, pubkey = client.utils.generate_new_key_pair_from_seed(seed)
#mk2 = MnemonicKey().from_hex(privkey.generate().)
#mk3 = MnemonicKey().from_hex(privkey.private_bytes())

SSWAP_SSCRT_SHD_PAIR = "secret1wwt7nh3zyzessk8c5d98lpfsw79vzpsnerj6d0"
SSWAP_QUERY = { 'pool': {} }
SIENNA_SSCRT_SHD_PAIR = "secret1drm0dwvewjyy0rhrrw485q4f5dnfm6j25zgfe5"
SIENNA_QUERY = 'pair_info'

SSCRT_ADDRESS = 'secret1k0jntykt7e4g3y88ltc60czgjuqdy4c9e8fzek'
SSCRT_CONTRACT_HASH = client.wasm.contract_hash(SSCRT_ADDRESS)
SSCRT_KEY = 'api_key_nE9AgouX7GVnT0+3LhAGoNmwUZ7HHRR4sUxNB+tbWW4='

SHD_ADDRESS = 'secret1qfql357amn448duf5gvp9gr48sxx9tsnhupu3d'
SHD_CONTRACT_HASH = client.wasm.contract_hash(SHD_ADDRESS)
SHD_KEY = 'api_key_xSmcfnyU8z5750bZSC9icFYUz6whMLIUeEloEqORQ7M='

def generateTxEncryptionKeys():
  global nonceDict, txEncryptionKeyDict
  nonceDict = {"first":client.utils.generate_new_seed(), "second":client.utils.generate_new_seed()}
  txEncryptionKeyDict = {"first":client.utils.get_tx_encryption_key(nonceDict["first"]), "second":client.utils.get_tx_encryption_key(nonceDict["second"])}
generateTxEncryptionKeys()

def getBalances(scrtBal, sscrtBal, shdBal):
  scrtBalRes = client.bank.balance(mk.acc_address)
  sscrtBalRes = client.wasm.contract_query(SSCRT_ADDRESS, { "balance": { "address": mk.acc_address, "key": SSCRT_KEY }})
  shdBalRes = client.wasm.contract_query(SHD_ADDRESS, { "balance": { "address": mk.acc_address, "key": SHD_KEY }})
  scrtBal, sscrtBal, shdBal = int(scrtBalRes.to_data()[0]["amount"]) * 10**-6, float(sscrtBalRes['balance']['amount'])* 10**-6, float(shdBalRes['balance']['amount'])* 10**-8
  return scrtBal, sscrtBal, shdBal

def constantProduct(poolBuy, poolSell, x):
  out = -(poolBuy * poolSell)/(poolSell + x) + poolBuy
  return out

def getSiennaRatio():
  siennaInfo = client.wasm.contract_query(SIENNA_SSCRT_SHD_PAIR, SIENNA_QUERY)
  shdAmount, sscrtAmount = float(siennaInfo['pair_info']['amount_0']) * 10**-8, float(siennaInfo['pair_info']['amount_1'])*10**-6
  return sscrtAmount/shdAmount, shdAmount, sscrtAmount

def getSSwapRatio():
  sswapInfo = client.wasm.contract_query(SSWAP_SSCRT_SHD_PAIR, SSWAP_QUERY)
  sscrtAmount, shdAmount = float(sswapInfo['assets'][0]['amount'])*10**-6, float(sswapInfo['assets'][1]['amount'])*10**-8
  return sscrtAmount/shdAmount, shdAmount, sscrtAmount

def encryptHandleMsg(contractBuyAddress, handleMsg, contractCodeHash, isFirst: bool):
  global nonceDict, txEncryptionKeyDict, pubkey
  nonce = None
  txEncryptionKey = None
  if(isFirst):
    nonce, txEncryptionKey = nonceDict["first"], txEncryptionKeyDict["first"]
  else:
    nonce, txEncryptionKey = nonceDict["second"], txEncryptionKeyDict["second"]

  siv = SIV(txEncryptionKey)
  plaintext = bytes(contractCodeHash, "utf-8") + bytes(handleMsg, "utf-8")
  ciphertext = siv.seal(plaintext, [bytes()])

  key_dump = pubkey.public_bytes(
    encoding=serialization.Encoding.Raw, format=serialization.PublicFormat.Raw
  )

  encryptedMsg = nonce + [x for x in key_dump] + [x for x in ciphertext]
  encryptedHandleMsg = base64.b64encode(bytes(encryptedMsg)).decode()
  return MsgExecuteContract( mk.acc_address, contractBuyAddress, encryptedHandleMsg, [])

def encryptAndBroadcastTx(msgExecuteFirst, msgExecuteSecond):
  global accountNumber, sequence, fee

  stdSignMsg = StdSignMsg.from_data({
    "chain_id": "secret-4",
    "account_number": accountNumber,
    "sequence": sequence,
    "fee": fee.to_data(),
    "msgs": [],
    "memo": "",
  })
  stdSignMsg.msgs = [msgExecuteFirst, msgExecuteSecond]

  sequence = str(int(sequence) + 1)

  tx = wallet.key.sign_tx(stdSignMsg)
  try:
    res = client.tx.broadcast(tx)
  except:
    print("BROADCAST TX ERROR")
    return False
  return res

def calculateProfitCP(s1Shd, s1Sscrt, s2Shd, s2Sscrt, amountSwapped, gasFeeScrt):
  firstSwap = constantProduct(s1Shd, s1Sscrt, amountSwapped*.996)
  secondSwap = constantProduct(s2Sscrt, s2Shd, firstSwap*.997) * .999

  profit = secondSwap - amountSwapped - gasFeeScrt
  return profit, firstSwap, secondSwap 

def swapSienna(sscrtBal, firstSwap, secondSwap):
  sscrtBalStr = str(int(sscrtBal * 10 ** 6))
  firstSwapStr = str(int(firstSwap * 10 ** 8))
  secondSwapStr = str(int(secondSwap * 10 ** 6))

  msgSienna = json.dumps({"swap":{"to":None,"expected_return":firstSwapStr}})
  encryptedMsgSienna = str( base64.b64encode(msgSienna.encode("utf-8")), "utf-8")
  handleMsgSienna = { "send": {"recipient": SIENNA_SSCRT_SHD_PAIR, "amount": sscrtBalStr, "msg": encryptedMsgSienna }}
  handleMsgSiennaStr = json.dumps(handleMsgSienna, separators=(",", ":"))
  msgExecuteSienna = encryptHandleMsg(SHD_ADDRESS, handleMsgSiennaStr, SHD_CONTRACT_HASH, True)
  
  msgSswap = json.dumps({"swap":{"expected_return":secondSwapStr}})
  encryptedMsgSswap = str( base64.b64encode(msgSswap.encode("utf-8")), "utf-8")
  handleMsgSswap = { "send": {"recipient": SSWAP_SSCRT_SHD_PAIR, "amount": firstSwapStr, "msg": encryptedMsgSswap }}
  handleMsgSswapStr = json.dumps(handleMsgSswap, separators=(",", ":"))
  msgExecuteSswap = encryptHandleMsg(SSCRT_ADDRESS, handleMsgSswapStr, SSCRT_CONTRACT_HASH, False)

  #wallet.execute_tx(SHD_ADDRESS, handleMsg) #OTHER METHOD
  #tx = wallet.create_and_sign_tx([msgExecuteSienna, msgExecuteSswap], fee)
  
  return encryptAndBroadcastTx(msgExecuteSienna, msgExecuteSswap)

def swapSswap(sscrtBal, firstSwap, secondSwap):
  sscrtBalStr = str(int(sscrtBal * 10 ** 6))
  firstSwapStr = str(int(firstSwap * 10 ** 8))
  secondSwapStr = str(int(secondSwap * 10 ** 6))

  msgSswap = json.dumps({"swap":{"expected_return":firstSwapStr}})
  encryptedMsgSswap = str( base64.b64encode(msgSswap.encode("utf-8")), "utf-8")
  handleMsgSswap = { "send": {"recipient": SSWAP_SSCRT_SHD_PAIR, "amount": sscrtBalStr, "msg": encryptedMsgSswap }}
  handleMsgSswapStr = json.dumps(handleMsgSswap, separators=(",", ":"))
  msgExecuteSswap = encryptHandleMsg(SHD_ADDRESS, handleMsgSswapStr, SHD_CONTRACT_HASH, False)

  msgSienna = json.dumps({"swap":{"to":None,"expected_return":secondSwapStr}})
  encryptedMsgSienna = str( base64.b64encode(msgSienna.encode("utf-8")), "utf-8")
  handleMsgSienna = { "send": {"recipient": SIENNA_SSCRT_SHD_PAIR, "amount": firstSwapStr, "msg": encryptedMsgSienna }}
  handleMsgSiennaStr = json.dumps(handleMsgSienna, separators=(",", ":"))
  msgExecuteSswap = encryptHandleMsg(SSCRT_ADDRESS, handleMsgSiennaStr, SSCRT_CONTRACT_HASH, True)

  #res = wallet.execute_tx(SSCRT_ADDRESS, handleMsgSswap) #OTHER METHOD

  #msgExecuteSienna = client.wasm.contract_execute_msg(mk.acc_address, SHD_ADDRESS, handleMsgSienna, [])
  #tx = wallet.create_and_sign_tx([msgExecuteSswap, msgExecuteSienna], fee) #OTHER METHOD

  return encryptAndBroadcastTx(msgExecuteSswap, msgExecuteSswap)

def buyScrt(scrtBal):
  sscrtBalRes = client.wasm.contract_query(SSCRT_ADDRESS, { "balance": { "address": mk.acc_address, "key": SSCRT_KEY }})
  redeemAmount = int(sscrtBalRes['balance']['amount']) - scrtBal * 10 ** 6
  handleMsg = {"redeem":{"amount":str(redeemAmount)}}
  res = wallet.execute_tx(SSCRT_ADDRESS, handleMsg)
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
    return True
  return True

def txHandle(txResponse, profit, logWriter, runningProfit):
  if(not txResponse):
    print( "ERROR" )
    return False
  
  if(txResponse.is_tx_error()):
    logWriter.writerow([txResponse.to_json()])
    print(txResponse.to_json())
    logWriter.writerow([datetime.now(), "Error", txResponse.txhash])
    print(txResponse.txhash)
    return False

  print(txResponse.txhash)
  logWriter.writerow([txResponse.to_json()])
  print(txResponse.to_json())
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
        print(datetime.now(), "  profit:", profit)
      if( difference < 0 ):
        profit, firstSwap, secondSwap = calculateProfitCP(siennaShd, siennaSscrt, sswapShd, sswapSscrt, amountSwapping, gasFeeScrt)
        print(datetime.now(), "  height:", lastHeight, "  profit:", profit)
      if( profit > 0 and difference > 0):
        print( "Height: ", lastHeight )
        #print(datetime.now())
        #print("profit: ", profit)
        txResponse = swapSswap(amountSwapping, firstSwap, secondSwap)
      if( profit > 0 and difference < 0):
        print( "Height: ", lastHeight )
        #print(datetime.now())
        #print("profit: ", profit)
        txResponse = swapSienna(amountSwapping, firstSwap, secondSwap)
      if( txResponse != ""):
        runningProfit += profit
        txHandle(txResponse, profit, logWriter, runningProfit)
        generateTxEncryptionKeys()
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
  gasFeeScrt = .050001 + .00027
  amountSwapping = 1
  siennaRatio, siennaShd, siennaSscrt = getSiennaRatio()
  sswapRatio, sswapShd, sswapSscrt = getSSwapRatio()
  difference = siennaRatio - sswapRatio 
  if( difference > 0 ):
    profit, firstSwap, secondSwap = calculateProfitCP(sswapShd, sswapSscrt, siennaShd, siennaSscrt, amountSwapping, gasFeeScrt)
    print("profit: ", profit, firstSwap, secondSwap)
  if( difference < 0 ):
    profit, firstSwap, secondSwap = calculateProfitCP(siennaShd, siennaSscrt, sswapShd, sswapSscrt, amountSwapping, gasFeeScrt)
    print("profit: ", profit, firstSwap, secondSwap)
  #res = swapSswap(amountSwapping, firstSwap, secondSwap)
  #res = buyScrt(amountSwapping)
  #print(res.to_json())


testFunction()



