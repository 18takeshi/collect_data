import streamlit as st
import pandas as pd
import numpy as np

st.title('勤務データ集計アプリ')
st.caption('ver.1.0 2023/1/6')

#csvコンバーター
def convert_df(df):
    return df.to_csv().encode('Shift-JIS')

#データアップロード
uploaded_file = st.sidebar.file_uploader("出勤データをアップロードしてください", type='csv',accept_multiple_files=True)
origin_sheet = st.sidebar.file_uploader('勤務表をアップロードしてください',type='xlsx')

if uploaded_file is not None and origin_sheet is not None:

    #勤務表df(df_sheet)前処理
    df_sheet = pd.read_excel(origin_sheet,index_col=1)
    df_sheet = df_sheet.drop('出退勤')
    df_sheet = df_sheet[['社員番号','社員']]
    df_sheet['~17時'] = 0
    df_sheet['17時~'] = 0

    #出勤データ編集
    for file in uploaded_file:
        df = pd.read_csv(file,encoding='shift-jis',index_col=0)
        df = df[['労働時間','index','~17時','17時~']]
        day = str(file.name)
        day = day.split('_')
        day = day[0]
        df = df.rename(columns={'労働時間':day})

        df_sheet[day] = np.nan
        
        for d,i,b17,a17 in zip(df[day],df['index'],df['~17時'],df['17時~']):
            df_sheet.at[i,day] = d
            df_sheet.at[i,'~17時'] += b17   #17時集計の更新
            df_sheet.at[i,'17時~'] += a17

    df_sheet = df_sheet.drop('社員',axis=1)

    #エクスポート用ファイル名
    columns = list(df_sheet.columns)
    start = columns[3]
    finish = columns.pop()

    #勤務時間合計
    df_sheet['合計'] = df_sheet['17時~'] + df_sheet['~17時']

    st.header('集計結果')
    st.dataframe(df_sheet)

    #合計勤務時間アラート
    df_sheet['index'] = df_sheet.index
    over_80 = []
    for n,i in zip(df_sheet['合計'],df_sheet['index']):
        if n>= 80:
            over_80.append(i)

    st.header('勤務時間チェック')
    st.write('勤務時間が80時間を超えているスタッフ：'+str(over_80))

    df_sheet = df_sheet.drop('index',axis=1)
    csv = convert_df(df_sheet)
    st.download_button(label="集計結果出力",data=csv,file_name='from'+start+'to'+finish+'_集計結果.csv',mime='text/csv')      