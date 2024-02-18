WELCOME TO PYTHON AVEC CAPITAL !!!
**********************************
v1.0


INTRO
=====
In 2021 I coded a rudimentary trading robot in Java. This is the Python version of a similar simplified algorithm. My logic relies strictly on Coinbase tickers to catch dips and peaks in a given crypto's price, buying as low as possible and selling higher for a cash profit.


INSTALLATION
============
Step 1 - Create an API key on Coinbase Cloud and place the api_key and api_secret values in a config.json file like so:

{
  "api_key": "organizations/********/apiKeys/*****************",
  "api_secret": "-----BEGIN EC PRIVATE KEY-----\\n*****************\\***********************\\n************************************==\\n-----END EC PRIVATE KEY-----\\n"
}

IMPORTANT: you need to grant this key "trade" and "view" permissions.

Step 2 - Enter the robot parameters in a parameters.json file like so:

{
  "symbol": "DOGE-USDC",
  "entry": 0.08510
  "dipAmplitude": 0.0*,
  "recoveryAmplitude": 0.0*,
  "pumpAmplitude": 0.0*,
  "lossAmplitude": 0.0*,
  "positionSize": ***.**,
}

Step 3 - Install Python 3 and run the following in a Terminal located in the directory of the PythonAvecCapital.pyth script and 2 .json files:

python3 PythonAvecCapital.py

The robot should now be up and running and will inform you of its progress in the Terminal.


THEORY
======
Given crypto markets are volatile/manipulated, it is possible to grow a cash position by swing trading. The algorithm is as simple as possible: wait for a dip of w % down from the entry point/peak (maximum recorded price), then start looking for a recovery of x % up from the bottom (minimum recorded price), in which case buy and wait for a pump of y % up from the buy price, after which start looking for a loss of z % down from the peak, at which point sell for a profit. The sell point is the starting point of a new iteration, which means this process can be repeated ad infinitum. With the right parameters, the robot can take advantage of volatility no matter which direction price goes and grow a cash position by using the snowball effect of multiple successful iterations. Here is the algorithm broken down in pseudocode, involving the property "state" to determine at which step the algorithm is at.

STATE 0: the robot waits for the price to drop to a given level, once that level is found STATE = 1

STATE 1: having registered a dip, the robot follows the price as it drops and waits for the price to recover to a given level, once that level is found a buy order is triggered and STATE = 2 
            
STATE 2: having bought the dip, the robot waits for the price to increase to a given level, once that level is found STATE = 3

STATE 3: having registered a peak, the robot waits for the price to drop to a given level, once that level is found a sell order is triggered, STATE = 0 and the loop starts over again


OUTSIDE FACTORS
===============
At base value, crypto markets are pure offer and demand. The number of people who want to buy a certain crypto vs. how many are selling it determines the price. However, there are several factors outside of that basic mechanic that affect price movement. Here are 3 examples.

Example 1: the Bitcoin cycle. Every 4 years, there's a "halving event" where the emission rate of new bitcoins is cut in half. This "halving year" is generally bullish for crypto markets, as Bitcoin is the leading cryptocurrency and during such a year Bitcoin is generally spotlighted by the media and mainstream audiences. After the post-halving year, crypto markets have historically declined drastically from their all-time highs, followed by a year of slow recovery and the next halving year. This historical behaviour is important to keep in mind when dealing with anything crypto-related.

Example 2: the US election cycle. Ironically, the halving year typically occurs on the same year as the US Presidential Elections. During this time, markets are often bullish due to rumours of Quantitative Easing enacted by the incumbent-controlled Federal Reserve to please the population in hopes of re-election. However, such decisions to ease or tighten fiscal policy are swayed by inflation and unemployment data and so fiscal policies may differ from election year to election year. In times of Quantitative Easing, crypto markets historically soar thanks to the extra cheap liquidity injected into the US economy. The opposite goes for Quantitative Tightening, where crypto markets usually crash and burn, only to rev up back to life after the Federal Reserve goes back to easing, which reinjects liquidity and therefore volatiliy in crypto markets. This behaviour is also important, as the more volatility the better.

Example 3: liquidation cascades. Crypto markets are highly manipulated by "whales", account holders with astronomical quantities of crypto acquired at microscopic prices during a given crypto's infancy. Whales historically have pumped and dumped most crypto markets with impunity and will continue to do so as long as cryptocurrencies exist. This injects even more volatility in crypto markets as such pump or dump events have high chances of triggering liquidation cascades. Many traders are in crypto markets with high leverage and can be quickly margin called following a sudden price movement. This amplifies the whales' actions as the price increases or drops, because traders will either be liquidated with shorts as it goes up or liquidated with longs as it goes down, triggering more and more short or long liquidations as the price moves until a bottom or peak is formed and the given crypto goes into price consolidation. These sudden exagerated price movements can be highly profitable as much as they can be devastating and serve as a warning to overconfident traders who use too much leverage.

In summary, crypto markets are extremely wild and volatile and should be approached with caution. However, in times of high volatility, there are opportunities. Seizing such opportunities requires a cool head and good intuition. While the robot cannot intuitively detect outside factors' effects on price action, it can execute decisions based on hard data without any emotions involved, and given enough time and volatility, can potentially snowball a small account into a sizeable chunk of change.

DISCLAIMER: any given crypto could also go to 0 and you could lose all your money. You use this code at your own risk. If you don't know what crypto is, educate yourself before dabbling with it.
