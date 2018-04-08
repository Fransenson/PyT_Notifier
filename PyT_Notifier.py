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
time.sleep(1)

#Initial File Read
print("Trying to open ProfitTrailerData.json...")
time.sleep(1)

crashTimer = 5
while True:
    try:
        with open(data_path, 'r') as myfile:
            jsonData = myfile.read().replace('\n', '')
            print("Success! Reading current state...")
            firstPyLogObject = json.loads(jsonData)
            print("Current Pairs: ", len(firstPyLogObject['sellLogData']))
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
            result = bot.send_message(chat_id,"I stopped working because of problems with the JSON file. Please restart me!")
            sys.exit()



#Get current end of logfile
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
    time.sleep(3)
    sys.exit()


#Finalizing startup
print("Starting to watch for new transactions...DO NOT CLOSE THIS WINDOW")
result = bot.send_message(chat_id, "I am up and watching your trades! See you soon.").wait()
if (result):
    stamp = str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    print(stamp,"- Sent first message to Telegram!")
else:
    print("Could not send message to Telegram!")


#Watchmode runtime
aliveCounter = 60
while True:
    time.sleep(2)
    aliveCounter -= 1
    if aliveCounter == 0:
        print("Don't worry, PyT_Notifier is still alive and watching! #hodltime")
        aliveCounter = 60
    #Check new lines from last memorized position
    with open(log_path, 'r') as f:
        f.seek(initialEndPos)
        lines = f.readlines()
        if not lines:
            initialEndPos = f.tell()
            continue
        else:
            for line in lines:
                #If there is a transaction within the current line, go on with the message composer
                if any(s in line for s in ("BUY", "SELL")) & all(f in line for f in ("FILLED", "Get order information")):
                    time.sleep(2)
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
                                result = bot.send_message(chat_id,"I stopped working because of problems with the JSON file. Please restart me!")
                                sys.exit()
                    time.sleep(1)
                    latestSalesCount = len(pyLogObject['sellLogData'])
                    pattern     = "(\"symbol\":\")([A-Z]{6,8})(\")"
                    compiled    = re.compile(pattern)
                    match       = compiled.search(line)
                    symbol      = match.group(2)

                    #was it a sale?...Then get latest entry in Sales Log for the symbol!
                    if "SELL" in line:
                        for x in range(0, len(pyLogObject['sellLogData'])):
                            if symbol in str(pyLogObject['sellLogData'][x]):
                                result = (pyLogObject['sellLogData'][x])
                        try:
                            result
                        except NameError:
                            result_exists = False
                        else:
                            result_exists = True
                        if (result_exists ):
                            #Get relevant data
                            market      = str(result['market'])
                            amount      = str(result['soldAmount'])
                            profit      = str(result['profit']) + "%"
                            trigger     = str(result['triggerValue']) + "%"
                            dcaLevels   = str(result['boughtTimes'])
                            sellStrat   = str(result['sellStrategy'])
                            #Compose message if market = symbol that triggered the search
                            message     = "\U0001F911 *SOLD:*" + os.linesep + "`{0:<12}{1:>18}\n{2:<12}{3:>18}\n{4:<12}{5:>18}\n{6:<12}{7:>18}\n{8:<12}{9:>18}\n{10:<12}{11:>18}\n`".format("Coin:",market,"Strategy:",sellStrat,"Amount:",amount,"DCA Levels:",dcaLevels,"Trigger:",trigger,"Profit:",profit)
                            result      = bot.send_message(chat_id, message, parse_mode="Markdown").wait()
                            stamp       = str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
                            print(stamp,"- Sent SOLD message to Telegram!")
                    #...or was it a buy? Then see if it was DCA or not!
                    if "BUY" in line:
                        for x in range(0, len(pyLogObject['gainLogData'])):
                            if symbol in str(pyLogObject['gainLogData'][x]):
                                result      = pyLogObject['gainLogData'][x]
                                market      = str(result['market'])
                                amount      = str(result['averageCalculator']['totalAmount'])
                                avgPrice    = str(result['averageCalculator']['avgPrice'])
                                totalCost   = str(result['averageCalculator']['totalCost'])
                                # Compose message if market = symbol that triggered the search
                                message     = "\U0001F4B8 *BOUGHT:*" + os.linesep + "`{0:<12}{1:>20}\n{2:<12}{3:>20}\n{4:<12}{5:>20}\n{6:<12}{7:>20}\n`".format(
                                    "Coin:", market, "Amount:", amount, "Avg. Price:",str(format(float(avgPrice), '.8f')), "Total Cost:",str(format(float(totalCost), '.4f')))
                                result      = bot.send_message(chat_id, message, parse_mode="Markdown").wait()
                                stamp       = str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
                                print(stamp, "- Sent BOUGHT message to Telegram!")
                                
                        for x in range(0, len(pyLogObject['dcaLogData'])):
                            if symbol in str(pyLogObject['dcaLogData'][x]):
                                result      = pyLogObject['dcaLogData'][x]
                                market      = str(result['market'])
                                amount      = str(result['averageCalculator']['totalAmount'])
                                curPrice    = str(result['currentPrice'])
                                avgPrice    = str(result['averageCalculator']['avgPrice'])
                                boughtTimes = str(result['boughtTimes'])
                                # Compose message if market = symbol that triggered the search
                                message     = "\U0001F4B8\U0000183C *BOUGHT DCA:*" + os.linesep + "`{0:<14}{1:>18}\n{2:<14}{3:>18}\n{4:<14}{5:>18}\n{6:<14}{7:>18}\n{8:<14}{9:>18}\n`".format("Coin:", market, "Total amount:", amount, "Avg Price:",str(format(float(avgPrice), '.8f')), "Current Price:",str(format(float(curPrice), '.8f')), "DCA Level:", boughtTimes)
                                #Send Message to Telegram Bot
                                result      = bot.send_message(chat_id, message, parse_mode="Markdown").wait()
                                stamp       = str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
                                print(stamp,"- Sent DCA-BOUGHT message to Telegram!")
                time.sleep(0.5)
            #after each line, memorize current position in the logfile
            initialEndPos = f.tell()






