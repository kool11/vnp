# encoding: UTF-8

"""
导入MC导出的CSV历史数据到MongoDB中
"""

from vnpy.trader.app.ctaStrategy.ctaBase import MINUTE_DB_NAME
from vnpy.trader.app.ctaStrategy.ctaHistoryData import loadMcCsv,loadTbCsv


if __name__ == '__main__':
    loadTbCsv('IF18122.csv',MINUTE_DB_NAME,'IF1812')
    #loadMcCsv('IF0000_1min.csv', MINUTE_DB_NAME, 'IF0000')
    #loadMcCsv('rb0000_1min.csv', MINUTE_DB_NAME, 'rb0000')
