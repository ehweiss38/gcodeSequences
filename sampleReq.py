import requests

url='http://localhost:5000/values'

myobj={'locs':"hello"}

requests.post(url,json=myobj)