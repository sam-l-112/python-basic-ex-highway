import requests

response = requests.request("GET", url='https://www.ptt.cc/bbs/')#可直接用request函式並在參數內選擇方法(get,post)

print(response.text)  #印出資料，也就是文字版的網頁
print(type(response)) #看它的資料型態
print(vars(response)) #看它的屬性
print(response.status_code) #看它的狀態碼
print(response.headers) #看它的標頭
print(response.cookies) #看它的cookies
print(response.url) #看它的url
print(response.history) #看它的歷史
print(response.encoding) #看它的編碼
