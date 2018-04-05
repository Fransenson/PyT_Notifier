# PyT_Notifier
A Telegram notification bot for ProfitTrailer

## Features
* Telegram push notifications with detailed information on buys(normal and DCA) and sales
* NO EXCHANGE API REQUIRED - all information is being read from the PT log and database

## Installation
PyT_Notifier uses twx.botapi to send notifications. Therefore you need to install this package.

**If you've installed Python(3.X) already, you can probably skip to step 2**

### Step 1 - Install Python
Install Python 3: Follow the instructions on [the Python download page](https://www.python.org/downloads/)


### Step 2 - Install twx.botapi
Install the twx.botapi: `pip3 install twx.botapi`

If you are facing issues with pip, see the [official instructions to install pip](https://packaging.python.org/tutorials/installing-packages/) or [the pip installation guide](https://pip.pypa.io/en/stable/installing/)

or you just go: `sudo apt-get install python3-pip`


### Step 3 - Download PyT_Notifier
Download the current version of PyT_Notifier from the [release page here on github](https://github.com/Fransenson/PyT_Notifier/releases)


### Step 4 - Change settings as needed
Open `settings.py` with a text editor of your choice and fill in your relevant data. 

If you don't have a Telegram Bot API key already, go ask @BotFather on Telegram about it.

To get your chat id, open a chat with your bot, visit https://api.telegram.org/bot<YourBOTToken>/getUpdates in a browser, send the bot a message and refresh the page.

Please provide absolute paths to the needed files. 


### Step 5 - Run!
Run the script via `python3 PyT_Notifier.py` in your terminal.

If you are using pm2 just go with `pm2 start PyT_Notifier.py --interpreter python3`


## Feedback
Please report any issues here on GitHub. 

If you want to buy me a coffee (or a sports car):

BTC: 3BWgSr4TTc36ZAsihH46kfPDc2VxEyCvpu

ETH: 0x669Fc2167CEb36241C562e2207a646d1CFF16C6d

LTC: MNUoCapdRqsFsN98uAUivDf2MHK2m8uFoH

Those would be tips/donations only. The software is distributed free of charge and I don't offer paid support.

Thanks!
