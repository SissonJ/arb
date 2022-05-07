import csv
import fcntl
import time
from typing import Any, Dict, List
from secret_sdk.client.lcd.lcdclient import AsyncLCDClient, LCDClient
from secret_sdk.client.lcd.wallet import Wallet
from secret_sdk.core.auth.data.tx import StdFee
from secret_sdk.key.mnemonic import MnemonicKey
#from utils_taxes import read_inventory
from config import inventory_locations


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
  logs: Dict[str, str]
  inventory_locations: Dict[str, str]
  inv: List
  total: List
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
    self.inventory_locations = inventory_locations
    self.total = [] #scrt bal, scrt price, 
    self.inv = self.read_inventory("arb_v3") #[price, amount]

  def read_inventory(self, wallet):
    with open( self.inventory_locations[wallet], newline='') as csv_file:
      #self.enter(csv_file)
      logReader = csv.reader(csv_file, delimiter=',')
      inv = []
      self.total = []
      for row in logReader:
        if(row[0] == "total"):
          self.total.append(float(row[1])) # total sscrt
          self.total.append(float(row[2])) # total scrt
          self.total.append(float(row[3])) # scrt price
          continue
        if(row[0] == "price"):
          continue
        inv.append([float(row[0]),float(row[1])])
    return inv

  def write_inventory(self, wallet):
    with open( self.inventory_locations[wallet], mode="w", newline="") as csv_file:
      logWriter = csv.writer(csv_file, delimiter=',')
      logWriter.writerow(["total", self.total[0], self.total[1], self.total[2]])
      logWriter.writerow(["price", "amount"])
      for prices in self.inv:
        logWriter.writerow([prices[0], prices[1]])
      fcntl.flock(csv_file, fcntl.LOCK_UN)

  def enter(self, file):
    while True:
      try:
        fcntl.flock(file, fcntl.LOCK_EX | fcntl.LOCK_NB)
        break
      except (OSError, IOError) as ex:
        pass
      time.sleep(.05)