# -*- encoding: UTF-8 -*-

import data_fetcher
import settings
import strategy.enter as enter
from strategy import turtle_trade, climax_limitdown
from strategy import backtrace_ma250
from strategy import breakthrough_platform
from strategy import parking_apron
from strategy import low_backtrace_increase
from strategy import keep_increasing
from strategy import high_tight_flag
import akshare as ak
import push
import logging
import time
import datetime


def prepare():
    logging.info("************************ process start ***************************************")
    all_data = ak.stock_zh_a_spot_em()
    subset = all_data[['代码', '名称']]

    subset = subset[subset['代码'].str.startswith(('600', '601', '603', '605', '000', '002'))]
    subset = subset[~subset['名称'].str.contains('ST')]
    stocks = [tuple(x) for x in subset.values]
    statistics(all_data, stocks)

    strategies = {
        '放量上涨': enter.check_volume,
        '均线多头': keep_increasing.check,
        '停机坪': parking_apron.check,
        #'回踩年线': backtrace_ma250.check,
        '突破平台': breakthrough_platform.check,
        '无大幅回撤': low_backtrace_increase.check,
        #'海龟交易法则': turtle_trade.check_enter,
        '高而窄的旗形': high_tight_flag.check,
        #'放量跌停': climax_limitdown.check,
    }

    if datetime.datetime.now().weekday() == 0:
        strategies['均线多头'] = keep_increasing.check

    strategies_result, stocks_data = process(stocks, strategies)

    set1= strategies_result['放量上涨'].intersection(strategies_result['均线多头'])
    logging.info(f"放量上涨 & 均线多头: \n {set1}")
    set2= strategies_result['突破平台'].intersection(strategies_result['均线多头'])
    logging.info(f"突破平台 & 均线多头: \n {set2}")

    #import pdb; pdb.set_trace()
    logging.info("************************ process   end ***************************************")

def process(stocks, strategies):
    stocks_data = data_fetcher.run(stocks)
    strategies_result={}
    for strategy, strategy_func in strategies.items():
        results = check(stocks_data, strategy, strategy_func)
        strategies_result[strategy] = results
        time.sleep(2)

    #import pdb; pdb.set_trace()
    return strategies_result, stocks_data

def check(stocks_data, strategy, strategy_func):
    end = settings.config['end_date']
    m_filter = check_enter(end_date=end, strategy_fun=strategy_func)
    results = dict(filter(m_filter, stocks_data.items()))
    if len(results) > 0:
        push.strategy('**************"{0}"**************\n{1}\n**************"{0}"**************\n'.format(strategy, list(results.keys())))
    
    return set(results.keys())

def check_enter(end_date=None, strategy_fun=enter.check_volume):
    def end_date_filter(stock_data):
        if end_date is not None:
            if end_date < stock_data[1].iloc[0].日期:  # 该股票在end_date时还未上市
                logging.debug("{}在{}时还未上市".format(stock_data[0], end_date))
                return False
        return strategy_fun(stock_data[0], stock_data[1], end_date=end_date)


    return end_date_filter


# 统计数据
def statistics(all_data, stocks):
    limitup = len(all_data.loc[(all_data['涨跌幅'] >= 9.5)])
    limitdown = len(all_data.loc[(all_data['涨跌幅'] <= -9.5)])

    up5 = len(all_data.loc[(all_data['涨跌幅'] >= 5)])
    down5 = len(all_data.loc[(all_data['涨跌幅'] <= -5)])

    msg = "涨停数：{}   跌停数：{}\n涨幅大于5%数：{}  跌幅大于5%数：{}".format(limitup, limitdown, up5, down5)
    push.statistics(msg)


