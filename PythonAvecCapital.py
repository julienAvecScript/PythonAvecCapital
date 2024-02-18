import os
import json
from datetime import datetime
from coinbase.websocket import WSClient, WSClientConnectionClosedException, WSClientException
from coinbase.rest import RESTClient
import uuid

CONF_FILE_PATH = "config.json"
PARA_FILE_PATH = "parameters.json"

def loadConfig():
    if not os.path.isfile(CONF_FILE_PATH):
        return {}

    with open(CONF_FILE_PATH) as conf_file:
        conf = json.load(conf_file)

        return {
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
    high = 0
    low = 9999999999999999
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

    client = RESTClient(conf["api_key"], conf["api_secret"])
    symbol = para["symbol"]
    entry = float(para["entry"])
    dipAmplitude = float(para["dipAmplitude"])
    recoveryAmplitude = float(para["recoveryAmplitude"])
    pumpAmplitude = float(para["pumpAmplitude"])
    lossAmplitude = float(para["lossAmplitude"])
    positionSize = float(para["positionSize"])

    try:
        accounts = client.get_accounts()

    except Exception as e:
        print(e)
        accountId = 0
        exit()

    def log(text):
        file = open("logs.txt", "a")
        file.write(text + "\n")
        file.close()

    def buy(quoteSize):
        try:
            clientOrderId = uuid.uuid4()
            order = client.market_order_buy(client_order_id=str(clientOrderId), product_id=symbol, quote_size=str(quoteSize))
            orderId = order["order_id"]
            return orderId
        except Exception as e:
            print(e)
            return 0

    def sell(baseSize):
        try:
            clientOrderId = uuid.uuid4()
            order = client.market_order_sell(client_order_id=str(clientOrderId), product_id=symbol, base_size=str(baseSize))
            orderId = order["order_id"]
            return orderId
        except Exception as e:
            print(e)
            return 0

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
                print("-------------------- SPOT:" + str(spot) + " | STATE: 0, WAITING FOR DROP TO " + str(entry - dip) + " @" + str(now))
                if spot < entry - dip:
                    log("******************** ENTERED @" + str(entry - dip) + " @" + str(now))
                    state = 1
            case 1:
                recovery = low * recoveryAmplitude
                print("-------------------- SPOT:" + str(spot) + " | STATE: 1, WAITING FOR RECOVERY TO " + str(low + recovery) + " @" + str(now))
                if spot > low + recovery:
                    buyPrice = spot
                    buy(positionSize)
                    log("******************** BOUGHT @" + str(buyPrice) + " @" + str(now))
                    state = 2
            case 2:
                pump = buyPrice * pumpAmplitude
                print("-------------------- SPOT:" + str(spot) + " | STATE: 2, WAITING FOR PUMP TO " + str(buyPrice + pump) + " @" + str(now))
                if spot > buyPrice + pump:
                    log("******************** CONFIRMED @" + str(buyPrice + pump) + " @" + str(now))
                    state = 3
            case 3:
                loss = high * lossAmplitude
                print("-------------------- SPOT:" + str(spot) + " | STATE: 3, WAITING FOR DROP TO " + str(high - loss) + " @" + str(now))
                if buyPrice + (buyPrice * pumpAmplitude) < spot < high - loss:
                    sellPrice = spot
                    log("******************** SOLD @" + str(sellPrice) + " & BOUGHT @" + str(buyPrice) + " FOR " + str(sellPrice / buyPrice) + "%! RE-ENTRYING..." + " @" + str(now))
                    log("DEBUG: positionSize/spot=" + str(positionSize/spot))
                    sell(positionSize/spot)
                    entry = spot
                    state = 0

    def onMessage(msg):
        global entry
        global high
        global low

        now = datetime.now()
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
                        log('******************** DISCOVERED NEW LOW @ ' + str(spot) + " @ " + str(now))
                    if spot > high:
                        high = spot
                        log('******************** DISCOVERED NEW HIGH @ ' + str(spot) + " @ " + str(now))
                        if state == 0 and high > entry:
                            entry = high
                    compute(spot)
        except Exception as e:
            print(e)

    now = datetime.now()
    log("******************** START @" + str(now))
    wsClient = WSClient(api_key=conf["api_key"], api_secret=conf["api_secret"], on_message=onMessage)
    try:
        wsClient.open()
        wsClient.subscribe(product_ids=[symbol], channels=["ticker"])
        wsClient.run_forever_with_exception_check()
    except WSClientConnectionClosedException as e:
        print("Connection closed! Retry attempts exhausted.")
    except WSClientException as e:
        print("Error encountered!")
