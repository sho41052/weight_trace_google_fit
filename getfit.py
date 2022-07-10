import os
import itertools
import pandas as pd
import pathlib
from scripts.google_fit_api import google_fit_api
from datetime import datetime, timedelta


def get_data():
    fitness_service = google_fit_api()

    datasource_step = 'derived:com.google.step_count.delta:com.google.android.gms:estimated_steps'
    datatype_step = 'com.google.step_count.delta'
    datasource_weight = 'derived:com.google.weight:com.google.android.gms:merge_weight'
    datatype_weight = 'merge_weight'
    datasource_fat = 'derived:com.google.body.fat.percentage:com.google.android.gms:merged'
    datatype_fat = 'com.google.body.fat.percentage'

    # preparing data frame
    cols = ['day', 'weight', 'step', 'fat']
    df = pd.DataFrame(index=[], columns=cols)
    d1 = datetime(2021, 11, 1).date()
    d2 = datetime.today().date()
    for i in range((d2 - d1).days + 1):
        date = d1 + timedelta(i)
        record = pd.Series([date, None, None, None], index=df.columns, name=date)
        df.loc[len(df)] = record
    df = df.set_index('day')

    min_start = datetime(2021, 11, 1)

    # load previous data
    if os.path.exists('data/main_data.pkl'):
        last_update = datetime.fromtimestamp(pathlib.Path('data/main_data.pkl').stat().st_mtime).date()
        if last_update == datetime.today().date():
            df = pd.read_pickle('data/main_data.pkl')
            min_start = datetime.today()# - timedelta(days=1)

    for i in itertools.count():
        start_day = datetime.today() - timedelta(days=30) * (i + 1)
        if start_day < min_start:
            start_day = min_start
        end_day = datetime.today() - timedelta(days=30) * i

        step_result = fitness_service.get_data_multi_days(datasource_step, datatype_step, start_day, end_day)
        weight_result = fitness_service.get_data_multi_days(datasource_weight, datatype_weight, start_day, end_day)
        fat_result = fitness_service.get_data_multi_days(datasource_fat, datatype_fat, start_day, end_day)
        for daily_data in step_result['bucket']:
            start = datetime.fromtimestamp(int(daily_data['startTimeMillis']) / 1000).date()
            try:
                step = int(daily_data['dataset'][0]['point'][0]['value'][0]['intVal'])
            except IndexError as e:
                step = 0
            df.at[start, 'step'] = step

        for daily_data in weight_result['bucket']:
            start = datetime.fromtimestamp(int(daily_data['startTimeMillis']) / 1000).date()
            try:
                weight = float(daily_data['dataset'][0]['point'][0]['value'][0]['fpVal'])
            except IndexError as e:
                continue
            df.at[start, 'weight'] = weight

        for daily_data in fat_result['bucket']:
            start = datetime.fromtimestamp(int(daily_data['startTimeMillis']) / 1000).date()
            try:
                fat = float(daily_data['dataset'][0]['point'][0]['value'][0]['fpVal'])
            except IndexError as e:
                continue
            df.at[start, 'fat'] = fat

        if start_day == min_start:
            break

    df.to_pickle('data/main_data.pkl')
    df.to_csv('data/main_data.csv')
    return df


if __name__ == "__main__":
    get_data()
