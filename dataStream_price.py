import json
import random
import re
import string
from websocket import create_connection
from search_crypto import search

def generateSession():
    stringLength = 12
    letters = string.ascii_lowercase
    random_string = "".join(random.choice(letters) for i in range(stringLength))
    return "qs_" + random_string

def prependHeader(st):
    return "~m~" + str(len(st)) + "~m~" + st

def constructMessage(func, paramList):
    return json.dumps({"m": func, "p": paramList}, separators=(",", ":"))

def createMessage(func, paramList):
    return prependHeader(constructMessage(func, paramList))

def sendMessage(ws, func, args):
    ws.send(createMessage(func, args))

def sendPingPacket(ws, result):
    pingStr = re.findall(".......(.*)", result)
    if len(pingStr) != 0:
        pingStr = pingStr[0]
        ws.send("~m~" + str(len(pingStr)) + "~m~" + pingStr)

def socketJob(ws, symbol_id,tradingViewSocket,headers):
    try:
        result = ws.recv()
        price = 0
        if "session_id" in result:
            return socketJob(ws, symbol_id,tradingViewSocket,headers)
        if "quote_completed" in result :
            Res = re.findall("^.*?({.*)$", result)
            jsonStr = Res[0].split("~m~")[0]

            try:
                jsonRes = json.loads(jsonStr)
            except json.JSONDecodeError:
                # Handle non-JSON strings
                return socketJob(ws, symbol_id,tradingViewSocket,headers)

            if jsonRes["m"] == "qsd":
                price = jsonRes["p"][1]["v"]["lp"]
            return price


    
    except json.JSONDecodeError as e:
        # Log error message and problematic message for debugging purposes
        print(f"JSON decode error: {e}")
        print(f"Problematic message: {result}")
        return
    except KeyboardInterrupt:
        print("\nGoodbye!")
        exit(0)
    except Exception as e:
        print(f"ERROR: {e}\nTradingView message: {result}")
        # Reconnect WebSocket on error
        ws = create_connection(tradingViewSocket, headers=headers)
        session = generateSession()
        sendMessage(ws, "quote_create_session", [session])
        sendMessage(ws, "quote_set_fields", [session, "lp"])
        sendMessage(ws, "quote_add_symbols", [session, symbol_id])
        return
