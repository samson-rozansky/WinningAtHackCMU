import requests
# r = requests.get('https://discord.com/api/v9/guilds/1275882998591656016/messages/search?channel_id=1275914959858958450&include_nsfw=true&sort_by=timestamp&sort_order=asc&offset=0', auth = ('authorization', 'NTAzMDM3MjgwMjY1NTY4MjY3.GLxbwr.rrUE679H8xLgAOgC2oklpuKlnx0h4sakqYOc6g'))
message = "Hello World!"

token= 'NTAzMDM3MjgwMjY1NTY4MjY3.GLxbwr.rrUE679H8xLgAOgC2oklpuKlnx0h4sakqYOc6g'
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:102.0) Gecko/20100101 Firefox/102.0',
    'Authorization': token
}


r = requests.get('https://discord.com/api/v9/channels/1275914959858958450/messages', headers = headers)
print(r.json())
for i in range(100):
    previd = r.json()[-1]['id']
    r = requests.get('https://discord.com/api/v9/channels/1275914959858958450/messages?before='+previd, headers = headers)
    print(r.json())
