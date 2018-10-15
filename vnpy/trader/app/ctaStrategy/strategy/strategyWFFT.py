# encoding: UTF-8

from __future__ import division

from vnpy.trader.vtObject import VtBarData
from vnpy.trader.vtConstant import EMPTY_STRING
from vnpy.trader.app.ctaStrategy.ctaTemplate import (CtaTemplate,
                                                     BarGenerator,
                                                   ArrayManager)
import time
import WFFT



class WfftStrategy(CtaTemplate):
    className = 'WfftStrategy'
    
    initDays = 10     

    N = 25
    len_ = 50
    q = 15
    Tq = 0.0001
    Length = 30
    Dq = 1.5

    BarsSinceEntry = -1

    HighestAfterEntry = []
    LowestAfterEntry = []

    TrailingStart = 72
    TrailingStop = 27
    MinPoint = 0.01
    StopLossSet = 37
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

    pos2 = 0
    open_pos2 = 0
    short_pos = 0
    hi = 0
    lo = 0
    op = 0

    def __init__(self, ctaEngine, setting):
        super(WfftStrategy, self).__init__(ctaEngine, setting)
        self.MinPoint = ctaEngine.getPriceTick(self)
        self.bg = BarGenerator(self.onBar, 5)  
        self.am = ArrayManager()

        self.wfft = WFFT.pythonToCpp()
        self.wfft.setWfftSetting(self.N, self.len_, self.q, self.Tq, self.Length, self.Dq,
                                 int(self.TrailingStart), int(self.TrailingStop),
                                 float(self.MinPoint), int(self.StopLossSet))

    def onInit(self):
        self.writeCtaLog(u'%s策略初始化' % self.name)
        initData = self.loadBar(self.initDays)
        for bar in initData:
            self.onBar(bar)

        self.putEvent()

    # ----------------------------------------------------------------------
    def onStart(self):
        self.pos2 = self.pos
        self.writeCtaLog(u'%s策略启动' % self.name)
        self.putEvent()

    # ----------------------------------------------------------------------
    def onStop(self):
        self.writeCtaLog(u'%s策略停止' % self.name)
        self.putEvent()

    # ----------------------------------------------------------------------
    def onTick(self, tick):
        open_ = tick.lastPrice
        high = tick.lastPrice
        low = tick.lastPrice
        close = tick.lastPrice

        #req = {}
        #req['date'] = str(tick.date)
        #req['time'] = str(tick.time)
        #req['open'] = open_

        #req['volume'] = int(volume)
        #self.reqID += 1

        if self.pos2 != 0:
            self.BarsSinceEntry = self.BarsSinceEntry+1

        self.bg.updateTick(tick)

        list1 = self.wfft.stopLoss(int(self.pos2),int(self.BarsSinceEntry),high,close,open_,low)
        if len(list1) == 3:
            print('----stoploss----')

            direction = int(list1[0])
            price = list1[1]
            vol = int(list1[2])
            if direction == 3:
                ll = self.sell(price-1, vol)
                print('sell')
                if len(ll):
                    self.BarsSinceEntry = 0
                    #self.MyEntryPrice = []
                    self.pos2 = 0
            elif direction == 4:
                ll = self.cover(price+1, vol)
                print('cover')
                if len(ll):
                    self.BarsSinceEntry = 0
                    #self.MyEntryPrice = []
                    self.pos2 = 0

            print('-----finish----------')


    # ----------------------------------------------------------------------
    def onBar(self, bar):
        #self.bg.updateBar(bar)
        date = bar.date.encode('utf-8')
        time = bar.time.encode('utf-8')
        open_ = bar.open
        close = bar.close
        high = bar.high
        low = bar.low
        volume = int(bar.volume)

        if self.pos2 != 0:
            self.BarsSinceEntry = self.BarsSinceEntry+1

        print('-----onBar-----')

        list1 = self.wfft.onNewBar(date, time, open_, high, low, close, volume, self.pos2)

        if len(list1) == 4:
            direction = int(list1[1])
            price = list1[2]
            vol = int(list1[3])
            print(self.pos, self.pos2, direction, list1[0])
            if direction == 1:
                self.buy(price, vol)
                self.pos2 = 1
                print('buy')
            elif direction == 2:
                self.short(price, vol)
                self.pos2 = -1
                print('short')
            elif direction == 3:
                ll = self.sell(price-self.MinPoint*5, vol)
                if len(ll):
                    self.pos2 = 0
                print('sell')
            elif direction == 4:
                ll = self.cover(price+self.MinPoint*5, vol)
                if len(ll):
                    self.pos2 = 0
                print('cover')
            self.BarsSinceEntry = 0
        elif len(list1) == 7:
            print('two following steps')
            direction = int(list1[1])
            price = list1[2]
            vol = int(list1[3])
            print(self.pos, self.pos2, direction, list1[0])
            if direction == 3:
                ll = self.sell(price-self.MinPoint*5, vol)
                if len(ll):
                    self.pos2 = 0
                print('sell')
            elif direction == 4:
                ll = self.cover(price+self.MinPoint*5, vol)
                if len(ll):
                    self.pos2 = 0
                print('cover')
            direction2 = int(list1[4])
            price2 = list1[5]
            vol2 = int(list1[6])
            if direction2 == 1:
                self.buy(price2, vol2)
                self.pos2 = 1
                print('buy')
            elif direction2 == 2:
                self.short(price2, vol2)
                self.pos2 = -1
                print('short')
            self.BarsSinceEntry = 0

        list1 = self.wfft.stopLoss(int(self.pos2),int(self.BarsSinceEntry),high,close,open_,low)
        if len(list1) == 3:
            print('----stoploss----')

            direction = int(list1[0])
            price = list1[1]
            vol = int(list1[2])
            if direction == 3:
                ll = self.sell(price - 1, vol)
                print('sell')
                if len(ll):
                    self.BarsSinceEntry = 0
                    #self.MyEntryPrice = []
                    self.pos2 = 0
            elif direction == 4:
                ll = self.cover(price + 1, vol)
                print('cover')
                if len(ll):
                    self.BarsSinceEntry = 0
                    #self.MyEntryPrice = []
                    self.pos2 = 0

            print('-----finish----------')


        print('----onBarfinish----')

    def onOrder(self, order):
        pass

        # ----------------------------------------------------------------------

    def onTrade(self, trade):
        if trade.offset == u'open' and trade.direction == u'long':
            #self.BarsSinceEntry = 0
            #self.pos = 1
            self.wfft.onNewTrade(trade.price, True)
        elif trade.offset == u'open' and trade.direction == u'short':
            #self.BarsSinceEntry = 0
            #self.pos = -1
            #self.MyEntryPrice
            self.wfft.onNewTrade(trade.price, True)
        else:
            #self.BarsSinceEntry = 0
            #self.pos = 0
            self.wfft.onNewTrade(trade.price, False)



    def onStopOrder(self, so):
        pass
