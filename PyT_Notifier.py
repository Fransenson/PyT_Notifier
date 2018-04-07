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
            initialEndPos = f.tell()
            break
        else:
            lastLine = line

print("Done reading logfile till the end.")
print("Starting to watch for new transactions...DO NOT CLOSE THIS WINDOW")
aliveCounter = 2000
##Watchmode runtime
result = bot.send_message(chat_id, "I am up and watching your trades! See you soon.").wait()
if (result):
    print("Sent first message to Telegram!" + os.linesep)
else:
    print("Could not send message to Telegram!")

while True:
    time.sleep(5)
    aliveCounter -= 1
    if aliveCounter == 0:
        print("Don't worry, PyT_Notifier is still alive and watching! #hodltime")
        aliveCounter = 2000

    with open(log_path, 'r') as f:
        f.seek(initialEndPos)
        lines = f.readlines()
        if not lines:
            initialEndPos = f.tell()
            continue
        else:
            for line in lines:
                buysell = ("BUY", "SELL")
                filled = ("FILLED", "Get order information")
                if any(s in line for s in buysell) & all(f in line for f in filled):
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
                            amount = str(pyLogObject['sellLogData'][latestSaleCount - x]['soldAmount'])
                            profit = str(pyLogObject['sellLogData'][latestSaleCount - x]['profit']) + "%"
                            trigger = str(pyLogObject['sellLogData'][latestSaleCount - x]['triggerValue']) + "%"
                            dcaLevels = str(pyLogObject['sellLogData'][latestSaleCount - x]['boughtTimes'])
                            ##Compose message
                            message = "\U0001F911 *SOLD:*" + os.linesep + "`{0:<12}{1:>18}\n{2:<12}{3:>18}\n{4:<12}{5:>18}\n{6:<12}{7:>18}\n{8:<12}{9:>18}\n`".format("Coin:",market,"Amount:",amount,"DCA Levels:",dcaLevels,"Trigger:",trigger,"Profit:",profit)
                            result = bot.send_message(chat_id, message, parse_mode="Markdown").wait()
                            print("Sent SOLD message to Telegram!" + os.linesep)

                    if pairsCountDiff > 0:
                        for x in range(1, pairsCountDiff + 1):
                            market = str(pyLogObject['gainLogData'][latestPairsCount - x]['market'])
                            amount = str(pyLogObject['gainLogData'][latestPairsCount - x]['averageCalculator']['totalAmount'])
                            avgPrice = str(pyLogObject['gainLogData'][latestPairsCount - x]['averageCalculator']['avgPrice'])
                            totalCost = str(pyLogObject['gainLogData'][latestPairsCount - x]['averageCalculator']['totalCost'])
                            ##Compose message
                            message = "\U0001F4B8 *BOUGHT:*" + os.linesep + "`{0:<12}{1:>20}\n{2:<12}{3:>20}\n{4:<12}{5:>20}\n{6:<12}{7:>20}\n`".format("Coin:",market,"Amount:",amount,"Avg. Price:",str(format(float(avgPrice),'.8f')),"Total Cost:",str(format(float(totalCost),'.4f')))
                            ##Send Message to Telegram Bot
                            result = bot.send_message(chat_id, message, parse_mode="Markdown").wait()
                            print("Sent BOUGHT message to Telegram!" + os.linesep)

                    if dcaCountDiff > 0:
                        for x in range(1, dcaCountDiff + 1):
                                market = str(pyLogObject['dcaLogData'][latestDcaCount - x]['market'])
                                amount = str(pyLogObject['dcaLogData'][latestDcaCount - x]['averageCalculator']['totalAmount'])
                                curPrice = str(pyLogObject['dcaLogData'][latestDcaCount - x]['currentPrice'])
                                avgPrice = str(pyLogObject['dcaLogData'][latestDcaCount - x]['averageCalculator']['avgPrice'])
                                boughtTimes = str(pyLogObject['dcaLogData'][latestDcaCount - x]['boughtTimes'])
                                ##Compose message
                                message = "\U0001F4B8\U0000203C *BOUGHT DCA:*" + os.linesep + "`{0:<12}{1:>20}\n{2:<12}{3:>20}\n{4:<12}{5:>20}\n{6:<12}{7:>20}\n{8:<12}{9:>20}\n`".format("Coin:", market, "Total amount:", amount, "Avg Price:",str(format(float(avgPrice), '.8f')), "Current Price:",str(format(float(curPrice), '.8f')), "DCA Level:", boughtTimes)
                                ##Send Message to Telegram Bot
                                result = bot.send_message(chat_id, message, parse_mode="Markdown").wait()
                                print("Sent DCA-BOUGHT message to Telegram!" + os.linesep)

                    ##Set current LogDataCount from the .json as new base for comparison
                    firstSaleCount  = len(pyLogObject['sellLogData'])
                    firstPairsCount = len(pyLogObject['gainLogData'])
                    firstDcaCount   = len(pyLogObject['dcaLogData'])
                time.sleep(5)







