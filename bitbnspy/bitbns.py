import base64
import hashlib
import hmac
import json
import time
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
import socketio

socket_IO = socketio.Client()    

class bitbns():
    apiKeys = dict()
    baseUrl = 'https://api.bitbns.com/api/trade/v1'
    baseUrl2 = 'https://api.bitbns.com/api/trade/v2'
    baseUrl3 = 'https://bitbns.com/'

    def __init__(self, apiKey, apiSecretKey, timeout = 30):
        self.__setTimeout(timeout)

        self.apiKeys['apiKey'] = apiKey
        self.apiKeys['apiSecretKey'] = apiSecretKey
        
        self.connectionsAdaptor = requests.Session()
        self.connectionsAdaptor.mount('https://', HTTPAdapter(max_retries = Retry(total = 3)))

        headers = {'X-BITBNS-APIKEY': apiKey}
        response = self.connectionsAdaptor.get('https://api.bitbns.com/api/trade/v1/getServerTime', headers=headers)
        response = response.json()
        serverTime = int(response['serverTime'])
        localTime = int(time.time() * 1000.0)
        self.timeOffset = localTime - serverTime

    @classmethod
    def publicEndpoints(cls, timeout = 30):
        obj = cls.__new__(cls)
        super(bitbns, obj).__init__()

        obj.__setTimeout(timeout)
        obj.apiKeys['apiKey'] = ''
        obj.apiKeys['apiSecretKey'] = ''
        
        obj.connectionsAdaptor = requests.Session()
        obj.connectionsAdaptor.mount('https://', HTTPAdapter(max_retries = Retry(total = 3)))

        return obj


    def __setTimeout(self, timeout):
        old_send = requests.Session.send

        def new_send(*args, **kwargs):
            if kwargs.get("timeout", None) is None:
                kwargs["timeout"] = timeout
            return old_send(*args, **kwargs)

        requests.Session.send = new_send

    def initHeaders(self):
        api_headers = dict()
        api_headers['X-BITBNS-APIKEY'] = ''
        api_headers['X-BITBNS-PAYLOAD'] = ''
        api_headers['X-BITBNS-SIGNATURE'] = ''
        api_headers['Accept'] = 'application/json'
        api_headers['Accept-Charset'] = 'utf-8'
        api_headers['content-type'] = 'application/x-www-form-urlencoded'
        return api_headers

    def getOrderBookSocket(self, coinName, marketName):
        try:
            socket_IO.connect(
                'https://ws' + marketName.lower() + 'mv2.bitbns.com/?coin=' + coinName.upper(), transports = 'websocket')
            return {'socket': socket_IO, 'error': None, 'status': 1}
        except Exception as e:
            if str(e.args[0]) == 'Already connected':
                return {'socket': socket_IO, 'error': None, 'status': 1}
            return self.genErrorMessage(None, 0, 'some error in get req')

    def getTickerSocket(self, marketName):
        try:
            socket_IO.connect(
                'https://ws' + marketName.lower() + 'mv2.bitbns.com/?withTicker=true&onlyTicker=true', transports = 'websocket')
            return {'socket': socket_IO, 'error': None, 'status': 1}
        except Exception as e:
            if str(e.args[0]) == 'Already connected':
                return {'socket': socket_IO, 'error': None, 'status': 1}
            return self.genErrorMessage(None, 0, 'some error in get req')

    def getExecutedOrders(self, token):
        try:
            socket_IO.connect(
                f'https://wsorderv2.bitbns.com/?token={token}')
            return {'socket': socket_IO, 'error': None, 'status': 1}
        except Exception as e:
            if str(e.args[0]) == 'Already connected':
                return {'socket': socket_IO, 'error': None, 'status': 1}
            return self.genErrorMessage(None, 0, 'some error in get req')

    def verifyApiKeys(self, data):
        if isinstance(data['apiKey'], str) and isinstance(data['apiSecretKey'], str) and len(
                data['apiKey']) >= 5 and len(data['apiSecretKey']) >= 5:
            return True
        else:
            return False

    def getPayload(self, symbol, body):
        timeStamp_nonce = int(int(time.time() * 1000.0)) - int(self.timeOffset)
        data = dict()
        data['symbol'] = symbol
        data['timeStamp_nonce'] = str(timeStamp_nonce)
        data['body'] = body
        data = json.dumps(data)
        data = data.replace(" ", "")
        encoded = base64.b64encode(data.encode())
        return encoded.decode()

    def getSignature(self, payload, apiSecretKey):
        m = hmac.new(apiSecretKey.encode('utf-8'), payload.encode('utf-8'), hashlib.sha512)
        return m.hexdigest()

    def populateHeadersForPost(self, symbol, methodName, body):
        headers = self.initHeaders()
        payload = self.getPayload('/' + methodName + '/' + symbol, body)
        signature = self.getSignature(payload, self.apiKeys['apiSecretKey'])
        headers['X-BITBNS-APIKEY'] = self.apiKeys['apiKey']
        headers['X-BITBNS-PAYLOAD'] = payload
        headers['X-BITBNS-SIGNATURE'] = signature
        return headers

    def genErrorMessage(self, data, status, error):
        ret = dict()
        ret['data'] = data
        ret['status'] = status
        ret['error'] = error
        return ret

    def platformStatus(self):
        try:
            req = self.connectionsAdaptor.get(self.baseUrl + '/platform/status', headers={"X-BITBNS-APIKEY": self.apiKeys['apiKey']})
            return req.json()
        except:
            return self.genErrorMessage(None, 0, 'some error in get req')

    def getTickerApi(self, symbols):
        allSymbol = symbols.split(',')
        try:
            req = self.connectionsAdaptor.get(self.baseUrl + '/tickers', headers={"X-BITBNS-APIKEY": self.apiKeys['apiKey']})
            req = req.json()
        except:
            return self.genErrorMessage(None, 0, 'some error in get req')
        for key, item in req.items():
            req[key].pop('yes_price', None)
            req[key].pop('volume', None)
        if len(allSymbol) == 1 and allSymbol[0] == '':
            return {'data': req, 'status': 1, 'error': None}
        finallist = {'data': dict(), 'status': 1, 'error': None}
        for item in allSymbol:
            if item not in req:
                return self.genErrorMessage(None, 0, 'provide proper symbol')
            finallist['data'][item] = req[item]
        return finallist

    def requestAuthenticate(self, symbol):
        if isinstance(symbol, str) or len(symbol) >= 1:
            return True
        else:
            return False

    def requestAuthenticate2(self, order_obj):
        if isinstance(order_obj['side'], str) or isinstance(order_obj['symbol'], str):
            return True
        else:
            return False

    def makePostRequest(self, symbol, methodName, body):
        options = dict()
        options['url'] = self.baseUrl + '/' + methodName + '/' + symbol
        options['body'] = json.dumps(body)
        options['body'] = options['body'].replace(" ", "")
        headers = self.populateHeadersForPost(symbol, methodName, json.dumps(body))
        options['headers'] = headers
        try:
            req = requests.post(options['url'], headers=options['headers'], data=options['body'])
            return req.json()
        except:
            return self.genErrorMessage(None, 0, 'error while making post request')

    def makePostRequest2(self, methodName, body):
        options = dict()
        options['url'] = self.baseUrl2 + '/' + methodName
        options['method'] = 'POST'
        options['body'] = json.dumps(body)
        options['body'] = options['body'].replace(" ", "")
        options['followAllRedirects'] = True
        headers = self.populateHeadersForPost(body['symbol'], methodName, json.dumps(body))
        options['headers'] = headers
        try:
            req = requests.post(options['url'], headers=options['headers'], data=options['body'])
            return req.json()
        except:
            return self.genErrorMessage(None, 0, 'error while making post request')

    def currentCoinBalance(self, symbol):
        body = dict()
        if self.requestAuthenticate(symbol) and self.verifyApiKeys(self.apiKeys):
            return self.makePostRequest(symbol, 'currentCoinBalance', body)
        else:
            return self.genErrorMessage(None, 0, 'please recheck the parameters')

    def depositHistory(self, symbol, page):
        body = dict()
        body['page'] = page
        if self.requestAuthenticate(symbol) and self.verifyApiKeys(self.apiKeys):
            return self.makePostRequest(symbol, 'depositHistory', body)
        else:
            return self.genErrorMessage(None, 0, 'please recheck the parameters')

    def withdrawHistory(self, symbol, page):
        body = dict()
        body['page'] = page
        if self.requestAuthenticate(symbol) and self.verifyApiKeys(self.apiKeys):
            return self.makePostRequest(symbol, 'withdrawHistory', body)
        else:
            return self.genErrorMessage(None, 0, 'please recheck the parameters')

    def listOpenOrders(self, symbol):
        body = dict()
        body['page'] = 0
        if self.requestAuthenticate(symbol) and self.verifyApiKeys(self.apiKeys):
            return self.makePostRequest(symbol, 'listOpenOrders', body)
        else:
            return self.genErrorMessage(None, 0, 'please recheck the parameters')

    def listOpenStopOrders(self, symbol):
        body = dict()
        body['page'] = 0
        if self.requestAuthenticate(symbol) and self.verifyApiKeys(self.apiKeys):
            return self.makePostRequest(symbol, 'listOpenStopOrders', body)
        else:
            return self.genErrorMessage(None, 0, 'please recheck the parameters')

    def getCoinAddress(self, symbol):
        body = dict()
        if self.requestAuthenticate(symbol) and self.verifyApiKeys(self.apiKeys):
            return self.makePostRequest(symbol, 'getCoinAddress', body)
        else:
            return self.genErrorMessage(None, 0, 'please recheck the parameters')

    def placeSellOrder(self, symbol, quantity, rate):
        body = dict()
        body['quantity'] = quantity
        body['rate'] = rate
        if self.requestAuthenticate(symbol) and self.verifyApiKeys(self.apiKeys):
            return self.makePostRequest(symbol, 'placeSellOrder', body)
        else:
            return self.genErrorMessage(None, 0, 'please recheck the parameters')

    def placeBuyOrder(self, symbol, quantity, rate):
        body = dict()
        body['rate'] = rate
        body['quantity'] = quantity
        if self.requestAuthenticate(symbol) and self.verifyApiKeys(self.apiKeys):
            return self.makePostRequest(symbol, 'placeBuyOrder', body)
        else:
            return self.genErrorMessage(None, 0, 'please recheck the parameters')

    def placeMarketOrder(self, symbol, marketName, side, amount):
        body = dict()
        body['market'] = marketName
        body['side'] = side
        body['amount'] = amount
        if self.requestAuthenticate(symbol) and self.verifyApiKeys(self.apiKeys):
            return self.makePostRequest(symbol, 'placeMarketOrder', body)
        else:
            return self.genErrorMessage(None, 0, 'please recheck the parameters')        

    def placeMarketOrderQuantity(self, symbol, marketName, side, quantity):
        body = dict()
        body['market'] = marketName
        body['side'] = side
        body['quantity'] = quantity
        if self.requestAuthenticate(symbol) and self.verifyApiKeys(self.apiKeys):
            return self.makePostRequest(symbol, 'placeMarketOrderQnty', body)
        else:
            return self.genErrorMessage(None, 0, 'please recheck the parameters')
            
    def buyStopLoss(self, symbol, quantity, rate, t_rate):
        body = dict()
        body['quantity'] = quantity
        body['rate'] = rate
        body['t_rate'] = t_rate
        if self.requestAuthenticate(symbol) and self.verifyApiKeys(self.apiKeys):
            return self.makePostRequest(symbol, 'buyStopLoss', body)
        else:
            return self.genErrorMessage(None, 0, 'please recheck the parameters')

    def sellStopLoss(self, symbol, quantity, rate, t_rate):
        body = dict()
        body['quantity'] = quantity
        body['rate'] = rate
        body['t_rate'] = t_rate
        if self.requestAuthenticate(symbol) and self.verifyApiKeys(self.apiKeys):
            return self.makePostRequest(symbol, 'sellStopLoss', body)
        else:
            return self.genErrorMessage(None, 0, 'please recheck the parameters')

    def cancelOrder(self, symbol, entry_id):
        body = dict()
        body['entry_id'] = entry_id
        if self.requestAuthenticate(symbol) and self.verifyApiKeys(self.apiKeys):
            return self.makePostRequest(symbol, 'cancelOrder', body)
        else:
            return self.genErrorMessage(None, 0, 'please recheck the parameters')

    def getBuyOrderBook(self, symbol):
        try:
            req = self.connectionsAdaptor.get(self.baseUrl + '/orderbook/buy/{}'.format(symbol),
                               headers={"X-BITBNS-APIKEY": self.apiKeys['apiKey']})
            return req.json()
        except:
            return self.genErrorMessage(None, 0, 'some error in get req')

    def getSellOrderBook(self, symbol):
        try:
            req = self.connectionsAdaptor.get(self.baseUrl + '/orderbook/sell/{}'.format(symbol),
                               headers={"X-BITBNS-APIKEY": self.apiKeys['apiKey']})
            return req.json()
        except:
            return self.genErrorMessage(None, 0, 'some error in get req')

    def getApiUsageStatus(self):
        body = dict()
        if self.verifyApiKeys(self.apiKeys):
            return self.makePostRequest('USAGE', 'getApiUsageStatus', body)
        else:
            return self.genErrorMessage(None, 0, 'please recheck the parameters')

    def orderStatus(self, symbol, entry_id):
        body = dict()
        body['entry_id'] = entry_id
        if self.requestAuthenticate(symbol) and self.verifyApiKeys(self.apiKeys):
            return self.makePostRequest(symbol, 'orderStatus', body)
        else:
            return self.genErrorMessage(None, 0, 'please recheck the parameters')

    def cancelStopLossOrder(self, symbol, entry_id):
        body = dict()
        body['entry_id'] = entry_id
        if self.requestAuthenticate(symbol) and self.verifyApiKeys(self.apiKeys):
            return self.makePostRequest(symbol, 'cancelStopLossOrder', body)
        else:
            return self.genErrorMessage(None, 0, 'please recheck the parameters')

    def listExecutedOrders(self, symbol, pageNo, since):
        body = dict()
        body['page'] = pageNo
        body['since'] = since
        if self.requestAuthenticate(symbol) and self.verifyApiKeys(self.apiKeys):
            return self.makePostRequest(symbol, "listExecutedOrders", body)
        else:
            return self.genErrorMessage(None, 0, 'apiKeys Not Found , Please intialize it first')

    def placeOrders(self, orders_obj):
        body = orders_obj.copy()
        if self.requestAuthenticate2(orders_obj) and self.verifyApiKeys(self.apiKeys):
            return self.makePostRequest2('orders', body)
        else:
            return self.genErrorMessage(None, 0, 'apiKeys Not Found , Please intialize it first')

    def getOrders(self, orders_obj):
        body = orders_obj
        if self.requestAuthenticate2(orders_obj) and self.verifyApiKeys(self.apiKeys):
            return self.makePostRequest2('getordersnew', body)
        else:
            return self.genErrorMessage(None, 0, 'apiKeys Not Found , Please intialize it first')

    def cancelOrders(self, orders_obj):
        body = orders_obj
        if self.requestAuthenticate(orders_obj) and self.verifyApiKeys(self.apiKeys):
            return self.makePostRequest2('cancel', body)
        else:
            return self.genErrorMessage(None, 0, 'apiKeys Not Found , Please intialize it first')

    def getTokenSocket(self):
        body = dict()
        if self.requestAuthenticate('USAGE') and self.verifyApiKeys(self.apiKeys):
            return self.makePostRequest('USAGE', "getOrderSocketToken", body)
        else:
            return self.genErrorMessage(None, 0, 'apiKeys Not Found , Please intialize it first')

    def placeMarginOrders(self, orders_obj):
        if self.requestAuthenticate2(orders_obj) and self.verifyApiKeys(self.apiKeys):
            body = orders_obj.copy()
            return self.makePostRequest2('marginOrders', body)
        else:
            return self.genErrorMessage(None, 0, 'apiKeys Not Found , Please intialize it first')

    def cancelMarginOrder(self, orders_obj):
        if self.requestAuthenticate2(orders_obj) and self.verifyApiKeys(self.apiKeys):
            body = orders_obj.copy()
            return self.makePostRequest2('marginOrders', body)
        else:
            return self.genErrorMessage(None, 0, 'apiKeys Not Found , Please intialize it first')

    def settleMarginPartial(self, orders_obj):
        if self.requestAuthenticate2(orders_obj) and self.verifyApiKeys(self.apiKeys):
            body = orders_obj.copy()
            return self.makePostRequest2('marginOrders', body)
        else:
            return self.genErrorMessage(None, 0, 'apiKeys Not Found , Please intialize it first')

    def settleMargin(self, orders_obj):
        if self.requestAuthenticate2(orders_obj) and self.verifyApiKeys(self.apiKeys):
            body = orders_obj.copy()
            return self.makePostRequest2('marginOrders', body)
        else:
            return self.genErrorMessage(None, 0, 'apiKeys Not Found , Please intialize it first')

    def listMarginExecuted(self, orders_obj):
        if self.requestAuthenticate2(orders_obj) and self.verifyApiKeys(self.apiKeys):
            body = orders_obj.copy()
            return self.makePostRequest2('marginOrders', body)
        else:
            return self.genErrorMessage(None, 0, 'apiKeys Not Found , Please intialize it first')

    def listMarginPending(self, orders_obj):
        if self.requestAuthenticate2(orders_obj) and self.verifyApiKeys(self.apiKeys):
            body = orders_obj.copy()
            return self.makePostRequest2('marginOrders', body)
        else:
            return self.genErrorMessage(None, 0, 'apiKeys Not Found , Please intialize it first')

    def listMarginMarketOrders(self, orders_obj):
        if self.requestAuthenticate2(orders_obj) and self.verifyApiKeys(self.apiKeys):
            body = orders_obj.copy()
            return self.makePostRequest2('marginOrders', body)
        else:
            return self.genErrorMessage(None, 0, 'apiKeys Not Found , Please intialize it first')

    def fetchTickers(self):
        try:
            req = self.connectionsAdaptor.get(self.baseUrl3 + 'order/getTickerWithVolume')
            return {'data': req.json(), 'error': None, 'status': 1}
        except Exception as e:
            return self.genErrorMessage(None, 0, f'some error in get req :{e}')

    def fetchOrderBook(self, coin_name: str, market_name: str, depth: int = 20):
        try:
            req = self.connectionsAdaptor.get(self.baseUrl3 + f'exchangeData/orderbook?market={market_name}&coin={coin_name}')
            updated_data = dict()
            data = req.json()
            updated_data['asks'] = data['asks'][:depth]
            updated_data['bids'] = data['bids'][:depth]
            updated_data['timestamp'] = data['timestamp']
            return {'data': updated_data, 'error': None, 'status': 1}
        except Exception as e:
            return self.genErrorMessage(None, 0, f'some error in get req :{e}')

    def fetchTrades(self, coin_name: str, market_name: str, limit: int = 100):
        try:
            req = self.connectionsAdaptor.get(self.baseUrl3 + f'exchangeData/tradedetails/?coin={coin_name}&market={market_name}')
            data = req.json()[::-1]  #revesring the order since the raw data sends oldest trades first
            return {'data': data[:limit], 'error': None, 'status': 1}
        except Exception as e:
            return self.genErrorMessage(None, 0, f'some error in get req :{e}')
   
    def fetchMarkets(self):
        try:
            req = self.connectionsAdaptor.get(self.baseUrl3 + 'order/fetchMarkets/')
            data = req.json()
            return {'data': data, 'error': None, 'status': 1}
        except Exception as e:
            return self.genErrorMessage(None, 0, f'some error in get req :{e}')
        
    #still in dev (endpoint maybe updated later)
    def fetchOHLCV(self, coin_name: str, market_name: str, page: int = 1):
        try:
            req = self.connectionsAdaptor.get(self.baseUrl3 + f'exchangeData/ohlc/?coin={coin_name}_{market_name}&page={page}')
            data = req.json()
            return {'data': data[0]['data'], 'error': None, 'status': data[0]['status']}
        except Exception as e:
            return self.genErrorMessage(None, 0, f'some error in get req :{e}')
