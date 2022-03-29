import requests
import pandas as pd
import time
import json
import csv
import os

# Taiwan Future Url
Govement_url = "https://mis.taifex.com.tw/futures/api/getQuoteList"
postdata = {"MarketType":"1",
            "SymbolType":"F",
            "KindID":"1",
            "CID":"MXF",
            "ExpireMonth":"",
            "RowSize":"全部",
            "PageNo":"",
            "SortColumn":"",
            "AscDesc":"A"}

# Yahoo Url
Yahoo_url = "https://tw.stock.yahoo.com/future/futures.html?fumr=futurefull/"

def check_morning(time):
    if time.tm_hour >= 9 and time.tm_hour <= 12:
        return True
    elif time.tm_hour == 8 and time.tm_min >= 45:
        return True
    elif time.tm_hour == 13 and time.tm_min <= 45:
        return True
    else:
        return False

def check_night(time):
    if time.tm_hour >= 15 or time.tm_hour < 5:
        return True
    else:
        return False

def Confirm_StockisOpen(time):
    # 台股期貨日盤時間：08:45~13:45 夜盤時間：15:00~05:00
    if check_morning(time) :
         return 'morning'
    elif check_night(time) :
        return 'night'
    else:
        return 'close' 

    # 組成stock_list
    stock_list = '|'.join('tse_{}.tw'.format(target) for target in targets) 
    
    #　query data
    query_url = "http://mis.twse.com.tw/stock/api/getStockInfo.jsp?ex_ch="+ stock_list
    data = json.loads(urlopen(query_url).read())

    # 過濾出有用到的欄位
    columns = ['c','n','z','tv','v','o','h','l','y']
    df = pd.DataFrame(data['msgArray'], columns=columns)
    df.columns = ['股票代號','公司簡稱','當盤成交價','當盤成交量','累積成交量','開盤價','最高價','最低價','昨收價']
    df.insert(9, "漲跌百分比", 0.0) 
    
    # 新增漲跌百分比
    for x in range(len(df.index)):
        if df['當盤成交價'].iloc[x] != '-':
            df.iloc[x, [2,3,4,5,6,7,8]] = df.iloc[x, [2,3,4,5,6,7,8]].astype(float)
            df['漲跌百分比'].iloc[x] = (df['當盤成交價'].iloc[x] - df['昨收價'].iloc[x])/df['昨收價'].iloc[x] * 100

def get_trace_list():
  # 開啟 CSV 檔案
  with open('tracelist.csv', newline='') as csvfile:

    # 讀取 CSV 檔案內容
    rows = csv.reader(csvfile)
    list = []
    # 以迴圈輸出每一列
    for row in rows:
      list.append(row)

  return list

# TW Stock
def get_TW_Stock_price(item):
    # res = requests.get('https://tw.stock.yahoo.com/_td-stock/api/resource/FinanceChartService.ApacLibraCharts;autoRefresh=1648311604781;symbols=%5B%226147.TWO%22%5D;type=tick?bkt=&device=desktop&ecma=modern&feature=ecmaModern%2CuseVersionSwitch%2CuseNewQuoteTabColor&intl=tw&lang=zh-Hant-TW&partner=none&prid=djvbn5th3uf7o&region=TW&site=finance&tz=Asia%2FTaipei&ver=1.2.1233&returnMeta=true')
    res = requests.get('https://tw.stock.yahoo.com/_td-stock/api/resource/FinanceChartService.ApacLibraCharts;symbols=%5B%22'+ item +'.TWO%22%5D;type=tick?bkt=&returnMeta=true')
    price_now = res.json()['data'][0]['chart']['meta']['regularMarketPrice']
    price_lastday = res.json()['data'][0]['chart']['meta']['previousClose']

    difference = round(price_now - price_lastday,2)
    percent = round((price_now - price_lastday)*100/price_lastday,2)
    if difference>0:
        sdifference = '+' + str(difference)
        spercent = '+' + str(percent)
    else:
        sdifference = str(difference)
        spercent = str(percent)

    return item.rjust(5) + ': ' + str(price_now).rjust(8) + sdifference.rjust(8) + '(' + spercent.ljust(5,'0') + '%)'

# TW Future
def get_TW_Future_price(item):
    # TW Future
    # res = requests.get('https://tw.screener.finance.yahoo.net/future/aa03?fumr=futurepart')
    return 0

def combinestring(list):
    str = ''
    for item in list:
        str = str + item + '\n'
    return str

if __name__ == '__main__':
    list = get_trace_list()
    price = []
    while(True):

        for item in list:
            price.append(get_TW_Stock_price(item[0]))
  
        os.system("cls")
        print(combinestring(price))
        time.sleep(2)
        price.clear()


  