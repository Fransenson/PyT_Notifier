import json
import time
import os
import re
import sys
import datetime
from twx.botapi import TelegramBot
import settings

#Read Configuration File
bot_token   = settings.api_token
chat_id     = settings.chat_id
data_path   = settings.data_path
log_path    = settings.log_path

bot     = TelegramBot(bot_token)
bot.update_bot_info().wait()

#Greeting
print("Hello! This is PyT_Notifier by Fransenson#5625 (Discord)")
time.sleep(2)

#Initial File Read
print("Trying to open ProfitTrailerData.json...")
time.sleep(2)

crashTimer = 5
while True:
    try:
        with open(data_path, 'r') as myfile:
            jsonData = myfile.read().replace('\n', '')
            print("Success! Reading current state...")
            time.sleep(2)
            firstPyLogObject = json.loads(jsonData)
            break
    except:
        time.sleep(2)
        if crashTimer >= 0:
            crashTimer -= 1
            continue
        else:
            print("Could not read JSON File, even after 10 tries! Restart script to try again.")
            result = bot.send_message(chat_id,"I stopped working because of problems with the JSON file. Please restart me!")
            sys.exit()

print("Current Pairs: ", len(firstPyLogObject['sellLogData']))
print("Current Pairs: ", len(firstPyLogObject['gainLogData']))
print("Current DCA Entries: ", len(firstPyLogObject['dcaLogData']))
time.sleep(1)
try:
    with open(log_path, 'r') as f:
        while True:
            line = f.readline()
            if not line:
                initialEndPos = f.tell()
                break
except:
    print("Path to Logfile seems to be wrong. Please check the settings and restart me. Quitting...")
    time.sleep(3)
    sys.exit()

print("Done reading logfile till the end.")
print("Starting to watch for new transactions...DO NOT CLOSE THIS WINDOW")

aliveCounter = 20000

#Watchmode runtime
result = bot.send_message(chat_id, "I am up and watching your trades! See you soon.").wait()
if (result):
    stamp = str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    print(stamp,"- Sent first message to Telegram!" + os.linesep)
else:
    print("Could not send message to Telegram!")


while True:
    aliveCounter -= 1
    if aliveCounter == 0:
        print("Don't worry, PyT_Notifier is still alive and watching! #hodltime")
        aliveCounter = 20000

    with open(log_path, 'r') as f:
        f.seek(initialEndPos)
        lines = f.readlines()
        if not lines:
            initialEndPos = f.tell()
            continue
        else:
            for line in lines:
                buysell             = ("BUY", "SELL")
                filled              = ("FILLED", "Get order information")
                if any(s in line for s in buysell) & all(f in line for f in filled):
                    crashTimer = 10
                    while True:
                        try:
                            with open(data_path, 'r') as myfile:
                                jsonData = myfile.read().replace('\n', '')
                            pyLogObject = json.loads(jsonData)
                            break
                        except:
                            time.sleep(2)
                            if crashTimer >= 0:
                                crashTimer -= 1
                                continue
                            else:
                                print("Could not read JSON File, even after 10 tries! Restart script to try again.")
                                result = bot.send_message(chat_id,
                                                          "I stopped working because of problems with the JSON file. Please restart me!")
                                sys.exit()
                    time.sleep(1)
                    crashTimer = 10
                    latestSalesCount = len(pyLogObject['sellLogData'])
                    latestPairsCount = len(pyLogObject['gainLogData'])
                    latestDcaCount = len(pyLogObject['dcaLogData'])

                    pattern     = "(\"symbol\":\")([A-Z]{6,8})(\")"
                    compiled    = re.compile(pattern)
                    match       = compiled.search(line)
                    symbol      = match.group(2)


                    if (pyLogObject['sellLogData'][latestSalesCount-1]['market']==symbol) & ("SELL" in line):
                            #Get relevant data
                            market = str(pyLogObject['sellLogData'][latestSalesCount - 1]['market'])
                            amount = str(pyLogObject['sellLogData'][latestSalesCount - 1]['soldAmount'])
                            profit = str(pyLogObject['sellLogData'][latestSalesCount - 1]['profit']) + "%"
                            trigger = str(pyLogObject['sellLogData'][latestSalesCount - 1]['triggerValue']) + "%"
                            dcaLevels = str(pyLogObject['sellLogData'][latestSalesCount - 1]['boughtTimes'])
                            sellStrat = str(pyLogObject['sellLogData'][latestSalesCount - 1]['sellStrategy'])
                            #Compose message if market = symbol that triggered the search
                            message = "\U0001F911 *SOLD:*" + os.linesep + "`{0:<12}{1:>18}\n{2:<12}{3:>18}\n{4:<12}{5:>18}\n{6:<12}{7:>18}\n{8:<12}{9:>18}\n{10:<12}{11:>18}\n`".format("Coin:",market,"Strategy:",sellStrat,"Amount:",amount,"DCA Levels:",dcaLevels,"Trigger:",trigger,"Profit:",profit)
                            result = bot.send_message(chat_id, message, parse_mode="Markdown").wait()
                            stamp = str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
                            print(stamp,"- Sent SOLD message to Telegram!")
                            time.sleep(2)

                    if (pyLogObject['gainLogData'][latestPairsCount-1]['market']==symbol) & ("BUY" in line):
                            market = str(pyLogObject['gainLogData'][latestPairsCount - 1]['market'])
                            amount = str(pyLogObject['gainLogData'][latestPairsCount - 1]['averageCalculator']['totalAmount'])
                            avgPrice = str(pyLogObject['gainLogData'][latestPairsCount - 1]['averageCalculator']['avgPrice'])
                            totalCost = str(pyLogObject['gainLogData'][latestPairsCount - 1]['averageCalculator']['totalCost'])
                            #Compose message if market = symbol that triggered the search
                            message = "\U0001F4B8 *BOUGHT:*" + os.linesep + "`{0:<12}{1:>20}\n{2:<12}{3:>20}\n{4:<12}{5:>20}\n{6:<12}{7:>20}\n`".format("Coin:",market,"Amount:",amount,"Avg. Price:",str(format(float(avgPrice),'.8f')),"Total Cost:",str(format(float(totalCost),'.4f')))
                            result = bot.send_message(chat_id, message, parse_mode="Markdown").wait()
                            stamp = str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
                            print(stamp,"- Sent BOUGHT message to Telegram!")
                            time.sleep(2)

                    if (pyLogObject['dcaLogData'][latestDcaCount - 1]['market'] == symbol) & ("BUY" in line):
                                market = str(pyLogObject['dcaLogData'][latestDcaCount - 1]['market'])
                                amount = str(pyLogObject['dcaLogData'][latestDcaCount - 1]['averageCalculator']['totalAmount'])
                                curPrice = str(pyLogObject['dcaLogData'][latestDcaCount - 1]['currentPrice'])
                                avgPrice = str(pyLogObject['dcaLogData'][latestDcaCount - 1]['averageCalculator']['avgPrice'])
                                boughtTimes = str(pyLogObject['dcaLogData'][latestDcaCount - 1]['boughtTimes'])
                                # Compose message if market = symbol that triggered the search
                                message = "\U0001F4B8\U0000183C *BOUGHT DCA:*" + os.linesep + "`{0:<14}{1:>18}\n{2:<14}{3:>18}\n{4:<14}{5:>18}\n{6:<14}{7:>18}\n{8:<14}{9:>18}\n`".format("Coin:", market, "Total amount:", amount, "Avg Price:",str(format(float(avgPrice), '.8f')), "Current Price:",str(format(float(curPrice), '.8f')), "DCA Level:", boughtTimes)
                                #Send Message to Telegram Bot
                                result = bot.send_message(chat_id, message, parse_mode="Markdown").wait()
                                stamp = str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
                                print(stamp,"- Sent DCA-BOUGHT message to Telegram!")
                                time.sleep(2)
                time.sleep(0.5)
            initialEndPos = f.tell()






