import urllib
import urllib.parse
import urllib.request
import json

fdp_url = "172.17.0.5:5000"
url = "history"

params = { "service":"history", "exchange":"binance", "symbol":"BTC_USD", "start":"2022-10-01", "interval": "1d", "indicators":{"close":None}}
print(params)

request = urllib.request.Request(fdp_url+'/'+url, urllib.parse.urlencode(params).encode())
response = urllib.request.urlopen(request).read().decode()
print(response)
jiji = json.loads(response)

