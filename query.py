import requests
import re

url = 'http://fw.ybj.beijing.gov.cn/ddyy/ddyy/list'

# 打开txt文档  要求utf-8编码
with open(r"C:\Users\77542\Desktop\yanxinglie.txt", "a") as f:
    for i in range(1, 197):

        response = requests.post(url, data={
            "search_LIKE_yymc": "",
            "page": i
        })
        print(i)
        pattern = re.compile(r'<td bgcolor="#FFFFFF">.*?<a href="javascript:" onclick="view.*?">(.*?)</a>.*?</td>.*?<td height="40" align="center".*?">.*?<td bgcolor="#FFFFFF" align="center"></td>.*?align="center">(.*?)</td>', re.S)
        results = re.findall(pattern, response.text)
    
        for result in results:
            f.write(result[0].replace(" ", "").replace("\r\n", "") + ", " + result[1] + "\r\n")
