import trading_lib as tl

import os
import pandas as pd
import numpy as np
import vaex

pd.set_option('display.max_columns', 20)


# Создание новых файлов с премаркет объёмом и ценой откртыия на 9-25
def count_volume_premarket_price_m1():
    time_925 = np.timedelta64(9, 'h') + np.timedelta64(25, 'm')

    for file in os.listdir('Data'):
        if file.endswith('.csv'):
            pandas_df = pd.read_csv('Data/' + file)
            print(file)

            pandas_df['date'] = pd.to_datetime(pandas_df['date'])
            pandas_df['date_int'] = pd.to_datetime(pandas_df['date']).astype(np.int64)

            columns_list = pandas_df.columns.tolist()
            columns_list = columns_list[-1:] + columns_list[:-1]
            pandas_df = pandas_df[columns_list]

            vaex_df = vaex.from_pandas(pandas_df)

            start_date = np.datetime64(vaex_df.data.date[0], 'D')
            end_date = np.datetime64(vaex_df.data.date[-1], 'D')

            date = []
            volume = []
            open_924 = []
            while start_date < end_date:
                date.append(start_date)
                midnight = start_date.astype('datetime64[ms]').astype('int64') * 1_000_000
                premarket_stop = (start_date + time_925).astype('datetime64[ms]').astype('int64') * 1_000_000

                vaex_df.select((vaex_df.date_int > midnight) & (vaex_df.date_int < premarket_stop))
                volume.append(vaex_df.sum("volume", selection=True))

                if vaex_df.evaluate("open", selection=True).size > 0:
                    open_924.append(vaex_df.evaluate("open", selection=True)[-1])
                else:
                    open_924.append(0)

                start_date = np.busday_offset(start_date + np.timedelta64(1, 'D'), 0, roll='forward')

            pd.DataFrame(
                {'Date': date,
                 'Open_924': open_924,
                 'Volume': volume}).to_csv('Data/New_Files/' + file)


# Добавим в каждый файл цену вчерашнего закрытия и столбик с названием тикера
def add_yest_close():
    splits = 0
    total_tickers = 0
    for file in os.listdir('Data/New_Files'):
        if file.endswith('.csv'):
            print(file)

            new_df = pd.read_csv('Data/New_Files/' + file)
            try:
                daily_df = pd.read_csv('Data/sierra_daily/' + file)
                daily_df['date'] = pd.to_datetime(daily_df['date'], yearfirst=True)
            except:
                print(f"For {file.replace('.csv', '')} don't have daily data.")
                continue

            total_tickers += 1
            new_df['Data'] = pd.to_datetime(new_df['Data'], yearfirst=True)
            new_df['Ticker'] = file.replace('.csv', '')
            new_df['Yest_Close'] = 0
            new_df['Vol_10Days'] = 0
            new_df['Today_Open'] = 0
            new_df['Today_Close'] = 0

            if len(new_df) < 1 or len(daily_df) < 11 or new_df.Data.iloc[-1] < daily_df.date.iloc[0]:
                continue

            try:
                younger_data = pd.datetime(year=2018, month=11, day=30)
                older_date = max(new_df.Data[0], daily_df.date[10])
                i = 0
                while daily_df[daily_df.date == older_date].size == 0:
                    i += 1
                    older_date = new_df.Data[i]

                new_df = new_df.loc[(new_df.Data >= older_date) & (new_df.Data <= younger_data)].reset_index(drop=True)
                daily_df = daily_df[daily_df[daily_df.date == older_date].index[0]-10:].reset_index(drop=True)

                for id in range(len(new_df)):
                    cur_date = new_df.Data[id]

                    if new_df.Volume[id] > 0 and daily_df[daily_df.date == cur_date].size > 0:
                        data_id = daily_df[daily_df.date == cur_date].index[0]
                        new_df.loc[id, 'Yest_Close'] = daily_df.close[data_id-1]
                        new_df.loc[id, 'Vol_10Days'] = daily_df.volume[data_id-10:data_id].mean()
                        new_df.loc[id, 'Today_Open'] = daily_df.open[data_id]
                        new_df.loc[id, 'Today_Close'] = daily_df.close[data_id]
                        new_df.loc[id, 'Gap'] = (new_df['Open_924'][id] / new_df['Yest_Close'][id] - 1) * 100

            except:
                print(new_df[new_df.Volume > 0])
                print(daily_df)
                input()

            check_df = new_df[new_df.Volume > 0]
            if check_df.size > 0 and abs(check_df.Today_Open.iloc[0] / check_df.Open_924.iloc[0] - 1) > 0.2 \
                    and check_df.Today_Open.iloc[0] != 0.0:
                splits += 1
                print('Daily open: ', check_df.Today_Open.iloc[0], ' 9_25 price: ', check_df.Open_924.iloc[0])
                print('Current tickers: ', total_tickers, ' Total splits: ', splits)

            if check_df.size > 0 and check_df.Today_Open.iloc[0] == 0.0:
                print(new_df[new_df.Volume > 0])
                print(daily_df)

            new_df.to_csv('Data/Final_Files/' + file)


if __name__ == "__main__":
    add_yest_close()
