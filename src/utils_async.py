import asyncio
from typing import Optional
from BotInfo import BotInfo
from secret_sdk.client.lcd.lcdclient import AsyncLCDClient


async def getSSwapRatioAsync(botInfo: BotInfo, nonce: Optional[int] = 0, tx_encryption_key: Optional[str] = ""):
  sswapInfo = await botInfo.asyncClient.wasm.contract_query(
    botInfo.pairContractAddresses["pair1"], 
    botInfo.pairContractQueries["pair1"], 
    botInfo.pairContractHash["pair1"], 
    nonce, 
    tx_encryption_key,
  )
  if( botInfo.pairToken1First["pair1"] ):
    token1Amount = float(sswapInfo['assets'][0]['amount']) * 10**-botInfo.tokenDecimals["token1"]
    token2Amount = float(sswapInfo['assets'][1]['amount']) * 10**-botInfo.tokenDecimals["token2"]
  else:
    token1Amount = float(sswapInfo['assets'][1]['amount']) * 10**-botInfo.tokenDecimals["token1"]
    token2Amount = float(sswapInfo['assets'][0]['amount']) * 10**-botInfo.tokenDecimals["token2"]
  return token1Amount/token2Amount, token1Amount, token2Amount

async def getSiennaRatioAsync(botInfo: BotInfo, nonce: Optional[int] = 0, tx_encryption_key: Optional[str] = ""):
  siennaInfo = await botInfo.asyncClient.wasm.contract_query(
    botInfo.pairContractAddresses["pair2"], 
    botInfo.pairContractQueries["pair2"], 
    botInfo.pairContractHash["pair2"], 
    nonce, 
    tx_encryption_key
  )
  if(botInfo.pairToken1First["pair2"] ):
    token1Amount = float(siennaInfo['pair_info']['amount_0']) * 10**-botInfo.tokenDecimals["token1"]
    token2Amount = float(siennaInfo['pair_info']['amount_1']) * 10**-botInfo.tokenDecimals["token2"]
  else:
    token1Amount = float(siennaInfo['pair_info']['amount_1']) * 10**-botInfo.tokenDecimals["token1"]
    token2Amount = float(siennaInfo['pair_info']['amount_0']) * 10**-botInfo.tokenDecimals["token2"]
  return token1Amount/token2Amount, token1Amount, token2Amount

async def runAsyncQueries(botInfo: BotInfo, nonce, txEncryptionKey):
  task1 = asyncio.create_task(getSSwapRatioAsync(botInfo, nonce, txEncryptionKey))
  task2 = asyncio.create_task(getSiennaRatioAsync(botInfo, nonce, txEncryptionKey))
  sswapRatio, sswapt1, sswapt2 = await task1
  siennaRatio, siennat1, siennat2 = await task2
  return sswapRatio, sswapt1, sswapt2, siennaRatio, siennat1, siennat2

async def generateTxEncryptionKeysAsync(client: AsyncLCDClient):
  nonceDict = {"first":client.utils.generate_new_seed(), "second":client.utils.generate_new_seed()}
  txEncryptionKeyDict = {"first": await client.utils.get_tx_encryption_key(nonceDict["first"]), "second": await client.utils.get_tx_encryption_key(nonceDict["second"])}
  return nonceDict, txEncryptionKeyDict

async def getBalancesAsync(botInfo: BotInfo):
  task1 = asyncio.create_task(botInfo.client.bank.balance(botInfo.accAddr))
  task2 = asyncio.create_task(botInfo.client.wasm.contract_query(
    botInfo.tokenContractAddresses["token1"], 
    { "balance": { "address": botInfo.accAddr, "key": botInfo.tokenKeys["token1"] }}
  ))
  task3 = asyncio.create_task(botInfo.client.wasm.contract_query(
    botInfo.tokenContractAddresses["token2"], 
    { "balance": { "address": botInfo.accAddr, "key": botInfo.tokenKeys["token2"] }}
  ))
  scrtBalRes = await task1
  t1BalRes = await task2
  t2BalRes = await task3
  scrtBal = int(scrtBalRes.to_data()[0]["amount"]) * 10**-6
  t1Bal = float(t1BalRes['balance']['amount'])* 10**-botInfo.tokenDecimals["token1"]
  t2Bal = float(t2BalRes['balance']['amount'])* 10**-botInfo.tokenDecimals["token2"]
  return scrtBal, t1Bal, t2Bal