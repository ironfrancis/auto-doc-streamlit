import requests

resp = requests.get("""

https://mp.weixin.qq.com/misc/datacubequery?action=query_download&busi=3&tmpl=19&args={%22begin_date%22:20250718,%22end_date%22:20250817}&token=640095281&lang=zh_CN
""")
print(resp.text)