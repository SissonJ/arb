import csv

from BotInfo import BotInfo
from config import config
from utils import calculate_gain_loss, log_traceback, recordTx

def swap_simulations():
    botinfo = BotInfo(config["sscrt-shd-config"])
    botinfo.read_inventory("arb_v3")
    gain = calculate_gain_loss(botinfo, 56, 802, 3.6, 300)
    print(botinfo.total)
    print(botinfo.inv)
    botinfo.write_inventory("arb_v3")
    print(gain)
    #printout = recordTx(botinfo, "sscrt-test-test",200,12,"arb_v3")
    #print(printout)

swap_simulations()

def error_testing():
    try:
        1/0
    except Exception as e:
        with open( "../logs/TEST.csv", mode="a", newline="") as csv_file:
            logWriter = csv.writer(csv_file, delimiter=',')
            traceback = log_traceback(e)
            for rows in traceback:
                logWriter.writerow([rows])

#error_testing()

#"total",650,30,3.50
#"price","amount"
#3.05,650