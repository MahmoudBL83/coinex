import json

def getPrice(exchange_name,symbol):
    try:
        if symbol == 'USDT/USDT':
            price = 1
            return price

        if symbol.split('/')[1] == 'USDT':
            symbol_id = f"{str(exchange_name).upper().replace('OKEX','OKX')}{symbol.split('/')[0]+symbol.split('/')[1]}"
            with open("pricesData/"+f"{symbol_id}.json", "r") as f:
                price = json.load(f)[symbol][0]
        else:
            price1 = 0
            price2 = 0
            symbol_id1 = f"{str(exchange_name).upper().replace('OKEX','OKX')}{symbol.split('/')[1]+'USDT'}"
            with open("pricesData/"+f"{symbol_id1}.json", "r") as f:
                price1 = json.load(f)[symbol.split('/')[1]+"/"+'USDT'][0]
            symbol_id2 = f"{str(exchange_name).upper().replace('OKEX','OKX')}{symbol.split('/')[0]+'USDT'}"
            with open("pricesData/"+f"{symbol_id2}.json", "r") as f:
                price2 = json.load(f)[symbol.split('/')[0]+"/"+'USDT'][0]
            if not price1 or not price2:
                return 0
            if  price1 == 0:
                price = 0
            else:
                price = price2/price1
            
    except FileNotFoundError:
        price = 0

    return price

def getVolume(exchange_name,symbol):
    try:
        symbol_id = f"{str(exchange_name).upper().replace('OKEX','OKX')}{symbol.split('/')[0]+symbol.split('/')[1]}"
        with open("volumesData/"+f"{symbol_id}.json", "r") as f:
            volume = json.load(f)[symbol][0]
            
    except FileNotFoundError:
        volume = 0
        
    return volume