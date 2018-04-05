import json
import time
import os
from twx.botapi import TelegramBot
import settings

##Read Configuration File
bot_token   = settings.api_token
chat_id     = settings.chat_id
data_path   = settings.data_path
log_path    = settings.log_path

bot     = TelegramBot(bot_token)
bot.update_bot_info().wait()

##Greeting
print("Hello! This is PyT_Notifier by Fransenson#5625 (Discord)")
time.sleep(2)

##Initial File Read
print("Trying to open ProfitTrailerData.json...")
time.sleep(2)

with open(data_path, 'r') as myfile:
    jsonData = myfile.read().replace('\n', '')
    print("Success! Reading current state...")
    time.sleep(2)

firstPyLogObject    = json.loads(jsonData)

firstSaleCount      = len(firstPyLogObject['sellLogData'])
firstPairsCount     = len(firstPyLogObject['gainLogData'])
firstDcaCount       = len(firstPyLogObject['dcaLogData'])

print("Done! \nCurrent Sale Count: ", firstSaleCount)
print("Current Pairs: ", firstPairsCount)
print("Current DCA Entries: ", firstDcaCount)
time.sleep(2)


lastLine = None
with open(log_path, 'r') as f:
    while True:
        line = f.readline()
        if not line:
            break
        lastLine = line

print("Done reading logfile till the end.")
print("Starting to watch for new transactions...DO NOT CLOSE THIS WINDOW")
aliveCounter = 5000
##Watchmode runtime
result = bot.send_message(chat_id, "I am up and watching your trades! See you soon.").wait()

while True:
    aliveCounter -= 1
    if aliveCounter == 0:
        print("Don't worry, PyT_Notifier is still alive and watching! #hodltime")
        aliveCounter = 5000

    with open(log_path, 'r') as f:
        lines = f.readlines()
    if lines[-1] != lastLine:
        lastLine = lines[-1]
        buysell = ("BUY", "SELL")
        filled = ("FILLED", "Get order information")
        if any(s in lastLine for s in buysell) & all(f in lastLine for f in filled):
            with open(data_path, 'r') as myfile:
               jsonData     = myfile.read().replace('\n', '')
            pyLogObject     = json.loads(jsonData)
            latestSaleCount = len(pyLogObject['sellLogData'])
            latestPairsCount= len(pyLogObject['gainLogData'])
            latestDcaCount  = len(pyLogObject['dcaLogData'])

            saleCountDiff   = latestSaleCount - firstSaleCount
            pairsCountDiff  = latestPairsCount - firstPairsCount
            dcaCountDiff    = latestDcaCount - firstDcaCount

            if saleCountDiff > 0:
                for x in range(1, saleCountDiff + 1):
                    ##Get relevant data
                    market = str(pyLogObject['sellLogData'][latestSaleCount - x]['market'])
                    date = str(pyLogObject['sellLogData'][latestSaleCount - x]['soldDate']['date']['day']) + "." + str(
                        pyLogObject['sellLogData'][latestSaleCount - x]['soldDate']['date']['month']) + "." + str(
                        pyLogObject['sellLogData'][latestSaleCount - x]['soldDate']['date']['year']) + " - " + str(
                        pyLogObject['sellLogData'][latestSaleCount - x]['soldDate']['time']['hour']) + ":" + str(
                        pyLogObject['sellLogData'][latestSaleCount - x]['soldDate']['time']['minute'])
                    amount = str(pyLogObject['sellLogData'][latestSaleCount - x]['soldAmount'])
                    profit = str(pyLogObject['sellLogData'][latestSaleCount - x]['profit']) + "%"
                    trigger = str(pyLogObject['sellLogData'][latestSaleCount - x]['triggerValue']) + "%"
                    dcaLevels = str(pyLogObject['sellLogData'][latestSaleCount - x]['boughtTimes'])
                    ##Compose message
                    message = "\U0001F911 SOLD:\t" + os.linesep + "Coin:\t" + market + os.linesep + "Amount\t" + amount + os.linesep + "Date\t" + date + os.linesep + "DCA Levels\t" + dcaLevels + os.linesep + "Trigger\t" + trigger + os.linesep + "Profit\t" + profit
                    ##Send Message to Telegram Bot
                    result = bot.send_message(chat_id, message).wait()
                    print("Sent SOLD message to Telegram!" + os.linesep)

            if pairsCountDiff > 0:
                for x in range(1, pairsCountDiff + 1):
                    market = str(pyLogObject['gainLogData'][latestPairsCount - x]['market'])
                    date = str(pyLogObject['gainLogData'][latestPairsCount - x]['averageCalculator']['firstBoughtDate'][
                                   'date']['day']) + "." + str(
                        pyLogObject['gainLogData'][latestPairsCount - x]['averageCalculator']['firstBoughtDate'][
                            'date']['month']) + "." + str(
                        pyLogObject['gainLogData'][latestPairsCount - x]['averageCalculator']['firstBoughtDate'][
                            'date']['year']) + " - " + str(
                        pyLogObject['gainLogData'][latestPairsCount - x]['averageCalculator']['firstBoughtDate'][
                            'time']['hour']) + ":" + str(
                        pyLogObject['gainLogData'][latestPairsCount - x]['averageCalculator']['firstBoughtDate'][
                            'time']['minute'])
                    amount = str(pyLogObject['gainLogData'][latestPairsCount - x]['averageCalculator']['totalAmount'])
                    avgPrice = str(pyLogObject['gainLogData'][latestPairsCount - x]['averageCalculator']['avgPrice'])
                    totalCost = str(pyLogObject['gainLogData'][latestPairsCount - x]['averageCalculator']['totalCost'])
                    ##Compose message
                    message = "\U0001F4B8 BOUGHT\t" + os.linesep + "Coin\t" + market + os.linesep + "Amount\t" + amount + os.linesep + "Date\t" + date + os.linesep + "Average Price\t" + avgPrice + os.linesep + "Total Cost\t" + totalCost
                    ##Send Message to Telegram Bot
                    result = bot.send_message(chat_id, message).wait()
                    print("Sent BOUGHT message to Telegram!" + os.linesep)

            if dcaCountDiff > 0:
                for x in range(1, dcaCountDiff + 1):
                        market = str(pyLogObject['dcaLogData'][latestDcaCount - x]['market'])
                        date = str(
                            pyLogObject['dcaLogData'][latestDcaCount - x]['averageCalculator']['firstBoughtDate'][
                                'date']['day']) + "." + str(
                            pyLogObject['dcaLogData'][latestDcaCount - x]['averageCalculator']['firstBoughtDate'][
                                'date']['month']) + "." + str(
                            pyLogObject['dcaLogData'][latestDcaCount - x]['averageCalculator']['firstBoughtDate'][
                                'date']['year']) + " - " + str(
                            pyLogObject['dcaLogData'][latestDcaCount - x]['averageCalculator']['firstBoughtDate'][
                                'time']['hour']) + ":" + str(
                            pyLogObject['dcaLogData'][latestDcaCount - x]['averageCalculator']['firstBoughtDate'][
                                'time']['minute'])
                        amount = str(pyLogObject['dcaLogData'][latestDcaCount - x]['averageCalculator']['totalAmount'])
                        curPrice = str(pyLogObject['dcaLogData'][latestDcaCount - x]['currentPrice'])
                        avgPrice = str(pyLogObject['dcaLogData'][latestDcaCount - x]['averageCalculator']['avgPrice'])
                        boughtTimes = str(pyLogObject['dcaLogData'][latestDcaCount - x]['boughtTimes'])
                        ##Compose message
                        message = "\U0001F4B8\U0000203C BOUGHT\t" + os.linesep + "Coin\t" + market + os.linesep + "Total amount\t" + amount + os.linesep + "Date\t" + date + os.linesep + "Average Price\t" + avgPrice + os.linesep + "Current Price\t" + curPrice + os.linesep + "DCA Level\t" + boughtTimes
                        ##Send Message to Telegram Bot
                        result = bot.send_message(chat_id, message).wait()
                        print("Sent DCA-BOUGHT message to Telegram!" + os.linesep)

            ##Set current LogDataCount from the .json as new base for comparison
            firstSaleCount  = len(pyLogObject['sellLogData'])
            firstPairsCount = len(pyLogObject['gainLogData'])
            firstDcaCount   = len(pyLogObject['dcaLogData'])
        time.sleep(0.5)







