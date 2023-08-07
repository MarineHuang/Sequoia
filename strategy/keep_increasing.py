# -*- encoding: UTF-8 -*-

import talib as tl
import pandas as pd
import logging


# 均线多头排列（MA5, MA10, MA20, MA120向上）
def check(code_name, data, end_date=None, threshold=120):
    if len(data) < threshold:
        logging.debug("{0}:样本小于{1}天...\n".format(code_name, threshold))
        return
    data['ma5'] = pd.Series(tl.MA(data['收盘'].values, 5), index=data.index.values)
    data['ma10'] = pd.Series(tl.MA(data['收盘'].values, 10), index=data.index.values)
    data['ma20'] = pd.Series(tl.MA(data['收盘'].values, 20), index=data.index.values)
    data['ma120'] = pd.Series(tl.MA(data['收盘'].values, 120), index=data.index.values)

    if end_date is not None:
        mask = (data['日期'] <= end_date)
        data = data.loc[mask]

    data = data.tail(n=threshold)

    #if data.iloc[0]['ma30'] < data.iloc[step1]['ma30'] < \
    #    data.iloc[step2]['ma30'] < data.iloc[-1]['ma30'] and data.iloc[-1]['ma30'] > 1.2*data.iloc[0]['ma30']:
    
    
    # 在最近的3个交易日均线均多头排列
    if (data.iloc[-1]['ma5']  >= data.iloc[-1]['ma10']
        and data.iloc[-1]['ma10'] >= data.iloc[-1]['ma20']
        and data.iloc[-1]['ma20'] >= data.iloc[-1]['ma120']
        #and data.iloc[1]['ma5']  >= data.iloc[1]['ma10']
        #and data.iloc[1]['ma10'] >= data.iloc[1]['ma20']
        #and data.iloc[1]['ma20'] >= data.iloc[1]['ma120']
        #and data.iloc[2]['ma5']  >= data.iloc[2]['ma10']
        #and data.iloc[2]['ma10'] >= data.iloc[2]['ma20']
        #and data.iloc[2]['ma20'] >= data.iloc[2]['ma120']
    ):
        return True
    else:
        return False
