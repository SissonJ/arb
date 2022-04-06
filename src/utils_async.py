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

async def runAsyncQueries(botInfo: BotInfo, nonceDict, txEncryptionKeyDict):
  task1 = asyncio.create_task(getSSwapRatioAsync(botInfo))#, nonceDict["first"], txEncryptionKeyDict["first"]))
  task2 = asyncio.create_task(getSiennaRatioAsync(botInfo))#, nonceDict["second"], txEncryptionKeyDict["second"]))
  sswapRatio, sswapt1, sswapt2 = await task1
  siennaRatio, siennat1, siennat2 = await task2
  return sswapRatio, sswapt1, sswapt2, siennaRatio, siennat1, siennat2