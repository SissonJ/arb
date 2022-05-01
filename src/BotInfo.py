from typing import Any, Dict
from secret_sdk.client.lcd.lcdclient import AsyncLCDClient, LCDClient
from secret_sdk.client.lcd.wallet import Wallet
from secret_sdk.core.auth.data.tx import StdFee
from secret_sdk.key.mnemonic import MnemonicKey


class BotInfo:
  client: LCDClient
  asyncClient: AsyncLCDClient
  wallet: Wallet
  accAddr: str
  pairContractAddresses: Dict[str, str]
  pairContractQueries: Dict[Any, Any]
  pairContractHash: Dict[Any, Any]
  pairToken1First: Dict[bool, bool]
  tokenContractAddresses: Dict[str, str]
  tokenContractHashes: Dict[str, str] #client.wasm.contract_hash(botConfig["tokenAddrs"]["token1"])
  tokenKeys: Dict[str, str]
  tokenDecimals: Dict[int, int]
  fee: StdFee #(botConfig["fee"]["gas"], botConfig["fee"]["price"])
  accountNum: int #wallet.account_number(),
  sequence: int #wallet.sequence(),
  logs: Dict[str, str, str]
  #botConfig: Dict[str, Dict[str, str], Dict[str, str], Dict[str, str], Dict[str, str], str, Dict[int, str]]

  def __init__(self, botConfig):
    self.client = LCDClient(botConfig["clientInfo"]["endpoint"], botConfig["clientInfo"]["chainID"])
    self.asyncClient = AsyncLCDClient(botConfig["clientInfo"]["endpoint"], botConfig["clientInfo"]["chainID"])
    self.wallet = self.client.wallet(MnemonicKey(mnemonic=botConfig["mkSeed"]))
    self.accAddr = self.wallet.key.acc_address
    self.pairContractAddresses = botConfig["pairAddrs"]
    self.pairContractQueries = botConfig["pairQueries"]
    self.pairContractHash = {
      "pair1": self.client.wasm.contract_hash(self.pairContractAddresses["pair1"]),
      "pair2": self.client.wasm.contract_hash(self.pairContractAddresses["pair2"]),

    }
    self.pairToken1First = botConfig["token1First"]
    self.tokenContractAddresses = botConfig["tokenAddrs"]
    self.tokenContractHashes = {
      "token1": self.client.wasm.contract_hash(botConfig["tokenAddrs"]["token1"]),
      "token2": self.client.wasm.contract_hash(botConfig["tokenAddrs"]["token2"]),
    }
    self.tokenKeys = botConfig["tokenKeys"]
    self.tokenDecimals = botConfig["tokenDecimals"]
    self.fee = StdFee(botConfig["fee"]["gas"], botConfig["fee"]["price"])
    res = self.client.auth.account_info(self.wallet.key.acc_address)
    self.accountNum = res.account_number
    self.sequence = res.sequence
    self.logs = {
      "csv": botConfig["logLocation"],
      "central": botConfig["centralLogLoc"],
      "output": botConfig["outputLogLoc"],
    }
    