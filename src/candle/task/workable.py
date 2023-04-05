import os
import zipfile
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from multiprocessing import Pool, cpu_count
import re

def extract_zip(zip_file):
    cwd = os.path.abspath(os.getcwd())
    extract_dir = zip_file[:-4]
    zip_file = os.path.join(cwd, zip_file)

    if not os.path.exists(extract_dir):
        os.makedirs(extract_dir)
    else:
        return
    with zipfile.ZipFile(zip_file, 'r') as zfile:
        zfile.extractall(path=extract_dir)


def merge_dataframes(results, files, freqs):
    merged_dfs = [pd.concat([res[i] for res in results], axis=1, keys=[os.path.splitext(os.path.basename(file))[0] for file in files]) for i in range(len(freqs))]
    return merged_dfs

def filter_data_by_type(df, data_type):
    def match_column(col, pattern):
        return re.search(pattern, str(col))

    if data_type == "内外盘五档报价":
        filtered_columns = [col for col in df.columns if (match_column(col, '买|卖')) and match_column(col, '价')]
    elif data_type == "五档挂单量_挂单额":
        filtered_columns = [col for col in df.columns if (match_column(col, '买|卖')) and match_column(col, '量')]
    elif data_type == "总挂单量_挂单额":
        filtered_columns = [col for col in df.columns if match_column(col, '成交')]
    elif data_type == "盘口一档价差":
        filtered_columns = [col for col in df.columns if match_column(col, '盘口一档')]
    else:
        return None

    return df[filtered_columns]

def save_merged_data_to_hdf(merged_dfs, output_dir='output'):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    freqs = ['1T', '5T', '15T', '30T']
    data_types = ["内外盘五档报价", "五档挂单量_挂单额", "总挂单量_挂单额", "盘口一档价差"]

    for i, freq in enumerate(freqs):
        for data_type in data_types:
            output_file = f"{output_dir}/{freq}_{data_type}.h5"
            node_name = f"df_{freq}_{data_type}"

            flat_df = merged_dfs[i]
            filtered_df = filter_data_by_type(flat_df, data_type)

            if filtered_df is not None:
                filtered_df.columns = [f'{col[0][11:19]}_{col[1]}' if isinstance(col, tuple) else col for col in filtered_df.columns]
                filtered_df.to_hdf(output_file, key=node_name, mode='w', format='fixed', complib='blosc', complevel=9)

def clean_data(df):
    df['时间'] = pd.to_datetime(df['时间'])
    df.set_index('时间', inplace=True)
    df = df.resample('3S').ffill()
    df.replace([np.inf, -np.inf], np.nan, inplace=True)
    df.fillna(method='ffill', inplace=True)
    return df

def resample_data(df, freq):
    df_resampled = df.resample(freq).agg({
        '买一价': 'last',
        '卖一价': 'last',
        '买二价': 'last',
        '卖二价': 'last',
        '买三价': 'last',
        '卖三价': 'last',
        '买四价': 'last',
        '卖四价': 'last',
        '买五价': 'last',
        '卖五价': 'last',
        '买一量': 'last',
        '卖一量': 'last',
        '买二量': 'last',
        '卖二量': 'last',
        '买三量': 'last',
        '卖三量': 'last',
        '买四量': 'last',
        '卖四量': 'last',
        '买五量': 'last',
        '卖五量': 'last',
        '成交额': 'last',
        '成交量': 'last',
    })
    return df_resampled

def calculate_features(df):
    df['盘口一档差(卖1-买1)'] = (df['卖一价'].astype(float) - df['买一价'].astype(float))
    return df
def combine_indexes_to_df(series):
    # create an empty DataFrame
    df = pd.DataFrame()

    # loop through each index and add it to the DataFrame as a new column
    for i in range(series.index.nlevels):
        column_name = series.index.get_level_values(i)[0]
        
        df[column_name] = series.index.get_level_values(i)
    
    df['卖五量']=series[u'数据由预测者网(www.yucezhe.com)整理，任何问题请联系官方QQ:2023046319。'].values
    df = df.drop(0)
    return df
def read_csv_file(file_path):
    """Read a CSV file and return its contents as a Pandas DataFrame"""
    try:
        # df = pd.read_csv(file_path,encoding='unicode_escape',engine='python')
        # df = pd.
        # (file_path,encoding='gb18030',error_bad_lines = False,engine='python'
        #  # df = pd.read_csv(file_path,encoding='GB2312',on_bad_lines='skip',engine='python')
        # df = pd.read_csv(file_path,encoding='utf-8',engine='python'))
        with open(file_path, encoding='gb2312', errors = 'ignore') as rawdata:
            # ret = chardet.detect(rawdata.read(10000))
            series = pd.read_csv(rawdata,on_bad_lines='skip', sep=',')
            # ret = pd.read_csv(rawdata,error_bad_lines=False, sep=',')
        df = combine_indexes_to_df(series)
        return df
    except FileNotFoundError:
        print(f"Error: file {file_path} not found.")
    except Exception as e:
        print(f"Error: {str(e)}")

def process_data(file):
    df = read_csv_file(file)
    df = clean_data(df)
    freqs = ['1T', '5T', '15T', '30T']
    dfs = []
    
    for freq in freqs:
        df_resampled = resample_data(df, freq)
        df_features = calculate_features(df_resampled)
        dfs.append(df_features)
    return dfs

def process_all_files(files):
    with Pool(cpu_count()) as p:
        results = p.map(process_data, files)
    return results

def main():
    zip_file = "fenbi_20170526.zip"
    extract_zip(zip_file)

    data_dir = "fenbi_20170526/"
    files = [os.path.join(data_dir, file) for file in os.listdir(data_dir)]

    results = process_all_files(files)
    print('处理完毕')

    freqs = ['1T', '5T', '15T', '30T']
    merged_dfs = merge_dataframes(results, files, freqs)
    print('合并完毕')

    save_merged_data_to_hdf(merged_dfs)
    print('保存完毕')

if __name__ == '__main__':
    main()