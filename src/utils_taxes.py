import csv

from BotInfo import BotInfo
from config import config
from utils import calculate_gain_loss

def swap_simulations():
    botinfo = BotInfo(config["sscrt-shd-config"])
    botinfo.read_inventory("arb_v2")
    gain = calculate_gain_loss(botinfo, 29, 655, 3.6, 300)
    print(botinfo.total)
    print(botinfo.inv)
    botinfo.write_inventory("arb_v2")
    print(gain)

swap_simulations()

#"total",650,30,3.50
#"price","amount"
#3.05,650