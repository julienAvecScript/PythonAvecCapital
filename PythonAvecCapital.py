import os
import json
from datetime import datetime

from coinbase.websocket import WSClient, WSClientConnectionClosedException, WSClientException
from coinbase.wallet.client import Client

CONF_FILE_PATH = "config.json"
PARA_FILE_PATH = "parameters.json"


def loadConfig():
    if not os.path.isfile(CONF_FILE_PATH):
        return {}

    with open(CONF_FILE_PATH) as conf_file:
        conf = json.load(conf_file)

        return {
            "apiPRO_key": conf["apiPRO_key"],
            "apiPRO_secret": conf["apiPRO_secret"],
            "api_key": conf["api_key"],
            "api_secret": conf["api_secret"]
        }

def loadParameters():
    if not os.path.isfile(PARA_FILE_PATH):
        return {}

    with open(PARA_FILE_PATH) as para_file:
        para = json.load(para_file)

        return para


if __name__ == "__main__":
    conf = loadConfig()
    para = loadParameters()
    state = 0
    symbol = input("What symbol are you trading? ")
    high = 0
    low = 9999999999999999
    entry = 0
    buyPrice = 0
    sellPrice = 0

    if not conf:
        print(
            "Error: Could not find the configuration file (config.json). Did you read the README?")
        exit()

    if not para:
        print(
            "Error: Could not find the parameters file (parameters.json). Did you read the README?")
        exit()

    client = Client(conf["api_key"], conf["api_secret"])
    dipAmplitude = float(para["dipAmplitude"])
    recoveryAmplitude = float(para["recoveryAmplitude"])
    pumpAmplitude = float(para["pumpAmplitude"])
    lossAmplitude = float(para["lossAmplitude"])

    try:
        user = client.get_current_user()
        print(user)

    except Exception as e:
        print(e)

    def compute(spot):
        global state
        global entry
        global dipAmplitude
        global recoveryAmplitude
        global pumpAmplitude
        global lossAmplitude
        global buyPrice
        global sellPrice
        now = datetime.now()

        match state:
            case 0:
                dip = entry * dipAmplitude
                print("-------------------- SPOT:" + str(spot) + ", WAITING FOR DROP TO " + str(entry - dip) + " @" + str(now))
                if spot < entry - dip:
                    print("******************** ENTERED @" + str(entry - dip))
                    state = 1
            case 1:
                recovery = low * recoveryAmplitude
                print("-------------------- SPOT:" + str(spot) + ", WAITING FOR RECOVERY TO " + str(low + recovery) + " @" + str(now))
                if spot > low + recovery:
                    buyPrice = spot
                    print("******************** BOUGHT @" + str(buyPrice))
                    state = 2
            case 2:
                pump = low * pumpAmplitude
                print("-------------------- SPOT:" + str(spot) + ", WAITING FOR PUMP TO " + str(low + pump) + " @" + str(now))
                if spot > low + pump:
                    print("******************** CONFIRMED @" + str(low + pump))
                    state = 3
            case 3:
                loss = high * lossAmplitude
                print("-------------------- SPOT:" + str(spot) + ", WAITING FOR DROP TO " + str(high - loss) + " @" + str(now))
                if low + (low * pumpAmplitude) < spot < high - loss:
                    sellPrice = spot
                    print("******************** SOLD @" + str(sellPrice) + " & BOUGHT @" + str(buyPrice) + " FOR " + str(
                        sellPrice / buyPrice) + "%! RE-ENTRYING..." + " @" + str(now))
                    entry = spot
                    state = 0

    def on_message(msg):
        global entry
        global high
        global low

        jsn = json.loads(msg)
        events = jsn["events"]
        try:
            for event in events:
                tickers = event["tickers"]
                for ticker in tickers:
                    spotRaw = ticker["price"]
                    spot = float(spotRaw)
                    if spot < low:
                        low = spot
                        print('******************** DISCOVERED NEW LOW @ ' + str(spot))
                    if spot > high:
                        high = spot
                        print('******************** DISCOVERED NEW HIGH @ ' + str(spot))
                        if state == 0:
                            entry = spot
                    compute(spot)
        except Exception as e:
            print(e)


    wsClient = WSClient(api_key=conf["apiPRO_key"], api_secret=conf["apiPRO_secret"], on_message=on_message)
    try:
        wsClient.open()
        wsClient.subscribe(product_ids=[symbol], channels=["ticker"])
        wsClient.run_forever_with_exception_check()
    except WSClientConnectionClosedException as e:
        print("Connection closed! Retry attempts exhausted.")
    except WSClientException as e:
        print("Error encountered!")