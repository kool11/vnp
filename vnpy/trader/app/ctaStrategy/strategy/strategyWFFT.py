# encoding: UTF-8

from __future__ import division

from vnpy.trader.vtObject import VtBarData
from vnpy.trader.vtConstant import EMPTY_STRING
from vnpy.trader.app.ctaStrategy.ctaTemplate import (CtaTemplate,
                                                     BarGenerator,
                                                   ArrayManager)
import time
from WFFTStrategyWrapper import WFFTStrategyWrapper,Action,Command


class WfftStrategy(CtaTemplate):
    className = 'WfftStrategy'
    
    initDays = 10     

    N = 15
    len_ = 30
    q = 15
    Tq = 0.0001
    Length = 30
    Dq = 0.5

    BarsSinceEntry = -1

    HighestAfterEntry = []
    LowestAfterEntry = []

    TrailingStart = 40
    TrailingStop = 5
    MinPoint = 0.2
    StopLossSet = 40
    paramList = ['name',
                 'className',
                 'author',
                 'vtSymbol',
                 'N',
                 'len',
                 'q',
                 'Tq',
                 'Length',
                 'Dq',
                 'TrailingStart',
                 'TrailingStop',
                 'StopLossSet']

    varList = ['inited',
               'trading',
               'pos']

    syncList = ['pos']

    def __init__(self, ctaEngine, setting):
        super(WfftStrategy, self).__init__(ctaEngine, setting)
        self.MinPoint = ctaEngine.getPriceTick(self)
        self.bg = BarGenerator(self.onBar, 5)

        self.wfft = WFFTStrategyWrapper(int(1))
        self.wfft.setWfftSetting(self.N, self.len_, self.q, self.Tq, self.Length, self.Dq,
                                 int(self.TrailingStart), int(self.TrailingStop),
                                 float(self.MinPoint), int(self.StopLossSet))

    def onInit(self):
        self.writeCtaLog(u'%s策略初始化' % self.name)
        initData = self.loadBar(self.initDays)
        for bar in initData:
            self.onBar(bar)
        self.putEvent()

    def onStart(self):
        self.writeCtaLog(u'%s策略启动' % self.name)
        self.putEvent()

    def onStop(self):
        self.writeCtaLog(u'%s策略停止' % self.name)
        self.putEvent()

    def onTick(self, tick):
        open_ = tick.lastPrice
        high = tick.lastPrice
        low = tick.lastPrice
        close = tick.lastPrice

        if self.pos != 0:
            self.BarsSinceEntry = self.BarsSinceEntry+1

        self.bg.updateTick(tick)

        results = self.wfft.stopLoss(high, close, open_, low)

        for ret in results:
            print('----stoploss----')
            direction = ret.action
            price = ret.price
            vol = ret.volume
            if direction == Action._buy:
                print(tick.time + " buy")
                self.buy(price, vol)
            elif direction == Action._short:
                print(tick.time + " short")
                self.short(price, vol)
            elif direction == Action._sell:
                print(tick.time + " sell")
                self.sell(price, vol)
            elif direction == Action._cover:
                print(tick.time + " cover")
                self.cover(price, vol)

    def onBar(self, bar):
        date = bar.date.encode('utf-8')
        time = bar.time.encode('utf-8')
        open_ = bar.open
        close = bar.close
        high = bar.high
        low = bar.low
        volume = int(bar.volume)

        results = self.wfft.onNewBar(date, time, open_, high, low, close, volume, self.pos)

        for ret in results:
            direction = ret.action
            price = ret.price
            vol = ret.volume
            if direction == Action._buy:
                print(bar.time+" buy")
                self.buy(price, vol)
            elif direction == Action._short:
                print(bar.time + " short")
                self.short(price, vol)
            elif direction == Action._sell:
                print(bar.time + " sell")
                self.sell(price, vol)
            elif direction == Action._cover:
                print(bar.time + " cover")
                self.cover(price, vol)

    def onOrder(self, order):
        pass

    def onTrade(self, trade):
        '''if trade.offset == u'open' and trade.direction == u'long':
            self.wfft.onNewTrade(trade.price, True)
        elif trade.offset == u'open' and trade.direction == u'short':
            self.wfft.onNewTrade(trade.price, True)
        else:
            self.wfft.onNewTrade(trade.price, False)'''
        pass

    def onStopOrder(self, so):
        pass
