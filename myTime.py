import requests


def getTime():
    key = '282160D5F99E5F9CF34C9E5CD9285E81'

    headers = {
        'X-BITBNS-APIKEY': key,
    }

    response = requests.get('https://api.bitbns.com/api/trade/v1/getServerTime', headers=headers)

    response = response.json()

    return response['serverTime']
