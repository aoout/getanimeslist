import requests

follow_status=0
page=1
uid=9145020
url = f'https://api.bilibili.com/x/space/bangumi/follow/list?type=1&follow_status={follow_status}&pn={page}&ps=15&vmid={uid}&ts=1611454168274'
r=requests.get(url)
print(r.text)