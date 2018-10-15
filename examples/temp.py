# encoding: UTF-8
from vnpy.trader.app.ctaStrategy.ctaBase import MINUTE_DB_NAME,DAILY_DB_NAME
from vnpy.trader.vtGlobal import globalSetting
from vnpy.trader.vtObject import VtBarData
import pymongo
import csv
from datetime import datetime, timedelta


def loadOKEXCsv(fileName, dbName, symbol):
    """将OKEX导出的csv格式的历史分钟数据插入到Mongo数据库中"""
    #start = time()
    print(u'开始读取CSV文件%s中的数据插入到%s的%s中' % (fileName, dbName, symbol))

    # 锁定集合，并创建索引
    client = pymongo.MongoClient(globalSetting['mongoHost'], globalSetting['mongoPort'])
    collection = client[dbName][symbol]
    collection.ensure_index([('datetime', pymongo.ASCENDING)], unique=True)

    # 读取数据和插入到数据库
    reader = csv.reader(open(fileName, "r"))
    for d in reader:
        if len(d[0]) > 9:
            bar = VtBarData()
            bar.vtSymbol = symbol
            bar.symbol = symbol

            bar.date = d[0].replace('-', '')
            bar.time = ''
            bar.datetime = datetime.strptime(d[0], '%Y-%m-%d').strftime('%Y%m%d')

            bar.open = float(d[2])
            bar.high = float(d[3])
            bar.low = float(d[4])
            bar.close = float(d[5])

            bar.volume = int(d[1])
            #bar.openInterest = float(d[6])

            flt = {'datetime': bar.datetime}
            collection.update_one(flt, {'$set': bar.__dict__}, upsert=True)
            print('%s \t %s' % (bar.date, bar.time))
    #print(u'插入完毕，耗时：%s' % (time() - start))


if __name__ == '__main__':
    loadOKEXCsv('IF888_DayData.csv', DAILY_DB_NAME, 'IF888')