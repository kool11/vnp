# encoding: utf8
from __future__ import print_function
import sys
sys.path.append('.')

from vnpy.trader.app.ctaStrategy.ctaTemplate import (CtaTemplate,
                                                     BarGenerator)
from vnpy.trader.vtObject import VtBarData

from vnpy.trader.vtGlobal import globalSetting

from MSDStrategyWrapper import MSDStrategyWrapper, Action, Command


########################################################################
class MSDStrategy(CtaTemplate):
    """蛛网策略"""
    className = 'MSDStrategy'
    author = u'pz'

    threshold = -0.12

    paramList = ['name',
                 'className',
                 'author',
                 'vtSymbol',

                 "threshold",
                 'TrailingStart',
                 'TrailingStop',
                 'MinPoint',
                 'StopLossSet']

    varList = ['inited',
               'trading',
               'pos']

    syncList = ['pos']

    # ----------------------------------------------------------------------

    def onBar(self, bar):
        date = bar.date.encode('utf-8')
        time = bar.time.encode('utf-8')
        open_ = bar.open
        close = bar.close
        high = bar.high
        low = bar.low
        volume = int(bar.volume)
        # print(date+" "+time+" ", open_)
        results = self.wrapper.onBarWrapper(date, time, open_, high, low, close, volume, self.pos)

        for ret in results:
            direction = ret.action
            price = ret.price
            vol = ret.volume
            if direction == Action._buy:
                print(bar.time + " buy")
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

        for ret in results:
            direction = ret.action
            if direction != Action._none:
                f = file("OrderRecord.json", "a+")
                f.write(str(date))
                f.write(",")
                f.write(str(time))
                f.write(",")
                f.write(str(ret.price))
                f.write(",")
                f.write(str(ret.volume))
                f.write(",")
                if direction == Action._buy:
                    f.write(",buy\n")
                elif direction == Action._short:
                    f.write(",short\n")
                elif direction == Action._sell:
                    f.write(",sell\n")
                elif direction == Action._cover:
                    f.write(",cover\n")

        '''if len(ret) == 3:
            direction = int(ret[0])
            price = ret[1]
            vol = int(ret[2])
            print(date+" "+time, price, vol, direction)
            if direction == 1:
                self.buy(price, vol)
            elif direction == 2:
                self.short(price, vol)
            elif direction == 3:
                self.sell(price, vol)
            elif direction == 4:
                self.cover(price, vol)
        '''

    # ----------------------------------------------------------------------
    def __init__(self, ctaEngine, setting):
        super(MSDStrategy, self).__init__(ctaEngine, setting)

        self.wrapper = MSDStrategyWrapper()
        self.wrapper.setSettingWrapper(self.threshold,
                                       self.TrailingStart, self.TrailingStop, self.MinPoint, self.StopLossSet)

    def onInit(self):
        """初始化策略（必须由用户继承实现）"""
        self.writeCtaLog(u'%s策略初始化' % self.name)

    # ----------------------------------------------------------------------
    def onStart(self):
        """启动策略（必须由用户继承实现）"""
        self.writeCtaLog(u'%s策略启动' % self.name)
        self.putEvent()

    # ----------------------------------------------------------------------
    def onStop(self):
        """停止策略（必须由用户继承实现）"""
        self.writeCtaLog(u'%s策略停止' % self.name)
        self.putEvent()

    # ----------------------------------------------------------------------
    def onTick(self, tick):
        """收到行情TICK推送（必须由用户继承实现）"""
        bar = VtBarData()
        bar.open = tick.lastPrice
        bar.close = tick.lastPrice
        bar.low = tick.lastPrice
        bar.high = tick.lastPrice
        self.onBar(bar)

    # ----------------------------------------------------------------------
    def onOrder(self, order):
        """收到委托变化推送（必须由用户继承实现）"""
        pass

    # ----------------------------------------------------------------------
    def onTrade(self, trade):
        # 发出状态更新事件
        self.putEvent()

    # ----------------------------------------------------------------------
    def onStopOrder(self, so):
        """停止单推送"""
        pass
