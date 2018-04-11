import json
import time
import os
import sys
import datetime
from twx.botapi import TelegramBot
import settings

# Read Configuration File
bot_token = settings.api_token
chat_id = settings.chat_id
data_path = settings.data_path
log_path = settings.log_path

bot = TelegramBot(bot_token)
bot.update_bot_info().wait()

# Greeting
print("Hello! This is PyT_Notifier v1.0.8c by Fransenson#5625 (Discord)")
time.sleep(1)

# Initial File Read to check if path is set correctly
print("Trying to open ProfitTrailerData.json...")
time.sleep(1)

crashTimer = 5
while True:
    try:
        with open(data_path, 'r') as myfile:
            jsonData = myfile.read().replace('\n', '')
            print("Success! Reading current state...")
            firstPyLogObject = json.loads(jsonData)
            print("Current Sales: ", len(firstPyLogObject['sellLogData']))
            print("Current Pairs: ", len(firstPyLogObject['gainLogData']))
            print("Current DCA Entries: ", len(firstPyLogObject['dcaLogData']))
            time.sleep(1)
            break
    except:
        time.sleep(2)
        if crashTimer >= 0:
            crashTimer -= 1
            continue
        else:
            print("Could not read JSON File, even after 10 tries! Restart script to try again.")
            sent = bot.send_message(chat_id,
                                    "I stopped working because of problems with the JSON file. Please restart me!")
            sys.exit()

# Get current end of logfile
try:
    with open(log_path, 'r') as f:
        while True:
            line = f.readline()
            if not line:
                initialEndPos = f.tell()
                print("Done reading logfile till the end.")
                break
except:
    print("Path to Logfile seems to be wrong. Please check the settings and restart me. Quitting...")
    time.sleep(1)
    sys.exit()

# Finalizing startup
print("Starting to watch for new transactions...DO NOT CLOSE THIS WINDOW")
firstSent = bot.send_message(chat_id, "PyT_Notifier v1.0.8c - I am up and watching your trades! See you soon.").wait()
if (firstSent):
    stamp = str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    print(stamp, "- Sent first message to Telegram!")
else:
    stamp = str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    print(stamp, "Could not send message to Telegram!")

# Watchmode runtime
aliveCounter = 60
while True:
    time.sleep(2)
    aliveCounter -= 1
    firstModTime = os.path.getmtime(data_path)
    if aliveCounter == 0:
        stamp = str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        print(stamp, "Don't worry, PyT_Notifier is still alive and watching! #hodltime")
        aliveCounter = 60
    # Check new lines from last memorized position
    with open(log_path, 'r') as f:
        f.seek(initialEndPos)
        lines = f.readlines()
        if not lines:
            initialEndPos = f.tell()
            continue
        else:
            for line in lines:
                # If there is a transaction within the current line, go on with the message composer

                if any(side in line for side in ("BUY", "SELL")) & all(orderinf in line for orderinf in ("Get order information")) & any(fillex in line for fillex in("FILLED", "EXPIRED")):
                    splitLine = line.split('--')
                    jsonLine = json.loads(str(splitLine[1]))
                    if (float(format(float(jsonLine['executedQty']),'.4f')) > 0):

                        symbol = jsonLine['symbol']
                        stamp = str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
                        print(stamp, "FOUND A TRANSACTION! Waiting for JSON to update")
                        # Wait for json to change
                        while True:
                            secondModTime = os.path.getmtime(data_path)
                            if firstModTime == secondModTime:
                                time.sleep(1)
                                stamp = str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
                                print(stamp, "still waiting for JSON to update.")
                                continue
                            else:
                                stamp = str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
                                print(stamp, "Update found!")
                                break

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
                                    sent = bot.send_message(chat_id,
                                                            "I stopped working because of problems with the JSON file. Please restart me!")
                                    sys.exit()



                        stamp = str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
                        print(stamp, "Transaction found was for:", symbol)

                        # was it a sale?...Then get latest entry in Sales Log for the symbol!
                        if "SELL" in line:
                            stamp = str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
                            print(stamp, "It's a sale!")
                            saleFound = False
                            while saleFound == False:
                                for x in range(0, len(pyLogObject['sellLogData'])):
                                    if symbol in str(pyLogObject['sellLogData'][x]):
                                        sellResult = (pyLogObject['sellLogData'][x])
                                try:
                                    sellResult
                                except NameError:
                                    sellResult_exists = False
                                    stamp = str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
                                    print(stamp, "Found no sale with matching symbol:", symbol)
                                else:
                                    sellResult_exists = True
                                if (sellResult_exists):
                                    # Get relevant data
                                    market = str(sellResult['market'])
                                    # amount = str(sellResult['soldAmount'])
                                    profit = str(sellResult['profit']) + "%"
                                    trigger = str(sellResult['triggerValue']) + "%"
                                    dcaLevels = str(sellResult['boughtTimes'])
                                    avgCost = str(sellResult['averageCalculator']['avgCost'])
                                    sellStrat = str(sellResult['sellStrategy'])
                                    coinProfit = (sellResult['averageCalculator']['avgCost'] * (1 + (sellResult['profit'] / 100))) - sellResult['averageCalculator']['avgCost']
                                    # Compose message if market = symbol that triggered the search
                                    message = "\U0001F911 *SOLD:*" + os.linesep + "`{0:<12}{1:>18}\n{2:<12}{3:>18}\n{4:<12}{5:>18}\n{6:<12}{7:>18}\n{8:<12}{9:>18}\n{10:<12}{11:>18}\n`".format(
                                        "Coin:", market, "Strategy:", sellStrat, "DCA Levels:", dcaLevels,
                                        "Trigger:", trigger, "Profit:", profit, "Coin Profit:",
                                        str(format(float(coinProfit), '.8f')))
                                    sent = bot.send_message(chat_id, message, parse_mode="Markdown").wait()
                                    stamp = str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
                                    print(stamp, "- Found Sale! Sent SOLD message to Telegram!")
                                    saleFound = True
                        # ...or was it a buy? Then see if it was DCA or not!
                        if "BUY" in line:
                            stamp = str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
                            print(stamp, "It's a buy!")
                            buyFound = False
                            while not buyFound:
                                while True:
                                    crashTimer = 10
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
                                            stamp = str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
                                            print(stamp,"Could not read JSON File, even after 10 tries! Restart script to try again.")
                                            sent = bot.send_message(chat_id,
                                                                    "I stopped working because of problems with the JSON file. Please restart me!")
                                            sys.exit()
                                for x in range(0, len(pyLogObject['gainLogData'])):
                                    if symbol in str(pyLogObject['gainLogData'][x]):
                                        gainResult = pyLogObject['gainLogData'][x]
                                try:
                                    gainResult
                                except NameError:
                                    gainResult_exists = False
                                    stamp = str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
                                    print(stamp,"Found no entry in pairs log with matching symbol:", symbol,
                                          "Looking at DCA log now...")
                                    for x in range(0, len(pyLogObject['dcaLogData'])):
                                        if symbol in str(pyLogObject['dcaLogData'][x]):
                                            dcaResult = pyLogObject['dcaLogData'][x]
                                    try:
                                        dcaResult
                                    except NameError:
                                        stamp = str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
                                        print(stamp,"Found no entry in DCA log with matching symbol:", symbol, "No message sent. Trying again, until buy is in found in JSON")
                                        dcaResult_exists = False
                                    else:
                                        dcaResult_exists = True
                                        if dcaResult_exists:
                                            market = str(dcaResult['market'])
                                            amount = str(dcaResult['averageCalculator']['totalAmount'])
                                            curPrice = str(dcaResult['currentPrice'])
                                            avgPrice = str(dcaResult['averageCalculator']['avgPrice'])
                                            boughtTimes = str(dcaResult['boughtTimes'])
                                            # Compose message if market = symbol that triggered the search
                                            message = "\U0001F4B8\U0001F4B8 *BOUGHT DCA:*" + os.linesep + "`{0:<14}{1:>18}\n{2:<14}{3:>18}\n{4:<14}{5:>18}\n{6:<14}{7:>18}\n{8:<14}{9:>18}\n`".format(
                                                "Coin:", market, "Total amount:", amount, "Avg Price:",
                                                str(format(float(avgPrice), '.8f')), "Current Price:",
                                                str(format(float(curPrice), '.8f')), "DCA Level:", boughtTimes)
                                            # Send Message to Telegram Bot
                                            sent = bot.send_message(chat_id, message, parse_mode="Markdown").wait()
                                            stamp = str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
                                            print(stamp, "- Found Buy! Sent DCA-BOUGHT message to Telegram!")
                                            buyFound = True
                                else:
                                    gainResult_exisits = True
                                    if gainResult_exists:
                                        market = str(gainResult['market'])
                                        amount = str(gainResult['averageCalculator']['totalAmount'])
                                        avgPrice = str(gainResult['averageCalculator']['avgPrice'])
                                        totalCost = str(gainResult['averageCalculator']['totalCost'])
                                        # Compose message if market = symbol that triggered the search
                                        message = "\U0001F4B8 *BOUGHT:*" + os.linesep + "`{0:<12}{1:>20}\n{2:<12}{3:>20}\n{4:<12}{5:>20}\n{6:<12}{7:>20}\n`".format(
                                            "Coin:", market, "Amount:", amount, "Avg. Price:",
                                            str(format(float(avgPrice), '.8f')), "Total Cost:",
                                            str(format(float(totalCost), '.4f')))
                                        sent = bot.send_message(chat_id, message, parse_mode="Markdown").wait()
                                        stamp = str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
                                        print(stamp, "- Found Buy! Sent BOUGHT message to Telegram!")
                                        buyFound = True
                                time.sleep(1)
                time.sleep(0.5)
            # after each line, memorize current position in the logfile
            initialEndPos = f.tell()