# encoding: utf8
from __future__ import print_function
import sys
sys.path.append('.')

from vnpy.trader.app.ctaStrategy.ctaTemplate import (CtaTemplate,
                                                     BarGenerator)
from vnpy.trader.vtGlobal import globalSetting


from MSDStrategyWrapper import MSDStrategyWrapper


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

    syncList = []

    # ----------------------------------------------------------------------

    def onBar(self, bar):
        date = bar.date.encode('utf-8')
        time = bar.time.encode('utf-8')
        open_ = bar.open
        close = bar.close
        high = bar.high
        low = bar.low
        volume = int(bar.volume)
        ret = self.wrapper.onBarWrapper(date, time, open_, high, low, close, volume, self.pos)
        if len(ret) == 3:
            direction = int(ret[0])
            price = ret[1]
            vol = int(ret[2])
            if direction == 1:
                self.buy(price, vol)
            elif direction == 2:
                self.short(price, vol)
            elif direction == 3:
                self.sell(price, vol)
            elif direction == 4:
                self.cover(price, vol)

    # ----------------------------------------------------------------------
    def __init__(self, ctaEngine, setting):
        super(MSDStrategy, self).__init__(ctaEngine, setting)
        self.bg = BarGenerator(self.onBar, 1, self.onBar)
        self.wrapper = MSDStrategyWrapper()
        self.wrapper.setSettingWrapper(self.threshold,
                                       150,15, 0.2, 130)

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
        self.bg.updateTick(tick)

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
