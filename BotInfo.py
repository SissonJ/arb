from typing import Any, Dict
from secret_sdk.client.lcd.lcdclient import LCDClient
from secret_sdk.client.lcd.wallet import Wallet
from secret_sdk.core.auth.data.tx import StdFee
from secret_sdk.key.mnemonic import MnemonicKey


class BotInfo:
  client: LCDClient
  wallet: Wallet
  accAddr: str
  pairContractAddresses: Dict[str, str]
  pairContractQueries: Dict[Any, Any]
  pairToken1First: Dict[bool, bool]
  tokenContractAddresses: Dict[str, str]
  tokenContractHashes: Dict[str, str] #client.wasm.contract_hash(botConfig["tokenAddrs"]["token1"])
  tokenDecimals: Dict[int, int]
  fee: StdFee #(botConfig["fee"]["gas"], botConfig["fee"]["price"])
  accountNum: int #wallet.account_number(),
  sequence: int #wallet.sequence(),
  botConfig: Dict[str, Dict[str, str], Dict[str, str], Dict[str, str], Dict[str, str], str, Dict[int, str]]

  def __init__(self, botConfig):
    self.client = LCDClient(botConfig["clientInfo"]["endpoint"], botConfig["clientInfo"]["chainID"])
    self.wallet = self.client.wallet(MnemonicKey(mnemonic=botConfig["mkSeed"]))
    self.accAddr = self.wallet.key.acc_address
    self.pairContractAddresses = botConfig["pairAddrs"]
    self.pairContractQueries = botConfig["pairQueries"]
    self.pairToken1First = botConfig["token1First"]
    self.tokenContractAddresses = botConfig["tokenAddrs"]
    self.tokenContractHashes = {
      "token1": self.client.wasm.contract_hash(botConfig["tokenAddrs"]["token1"]),
      "token2": self.client.wasm.contract_hash(botConfig["tokenAddrs"]["token2"]),
    }
    self.tokenDecimals = botConfig["tokenDecimals"]
    self.fee = StdFee(botConfig["fee"]["gas"], botConfig["fee"]["price"])
    self.accountNum = self.wallet.account_number()
    self.sequence = self.wallet.sequence()
    