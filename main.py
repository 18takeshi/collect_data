import streamlit as st
import pandas as pd
import numpy as np
import datetime

st.title('勤務データ集計アプリ')
st.caption('ver.1.03 2023/4/08')

#csvコンバーター
def convert_df(df):
    return df.to_csv().encode('Shift-JIS')

#データアップロード
uploaded_file = st.sidebar.file_uploader("出勤データをアップロードしてください", type='csv',accept_multiple_files=True)
origin_sheet = st.sidebar.file_uploader('勤務表をアップロードしてください',type='xlsx')

if uploaded_file is not None and origin_sheet is not None:

    #勤務表df(df_sheet)前処理
    df_sheet = pd.read_excel(origin_sheet,index_col=0)
    df_sheet = df_sheet.drop('出退勤')
    df_sheet = df_sheet[['時給','交通費','社員','契約社員']]
    df_sheet['給料'] = 0

    #社員、契約社員は集計しない
    df_sheet = df_sheet.drop('社員',axis=1)
    df_sheet = df_sheet.drop('契約社員',axis=1)

    #出勤データ編集
    for file in uploaded_file:
        df = pd.read_csv(file,encoding='shift-jis',index_col=0)
        df = df[['労働時間','日給']]
        day = str(file.name)
        day = day.split('_')
        day = day[0]
        after = datetime.datetime.strptime(day, '%Y-%m-%d')

        df = df.rename(columns={'労働時間':day})

        df_sheet[day] = np.nan
        df['index'] = df.index

        for d,i,m in zip(df[day],df['index'],df['日給']):
            df_sheet.at[i,day] = d
            df_sheet.at[i,'給料'] += m      #給料の更新

    #勤務時間合計
    df_sum = df_sheet.drop('時給',axis=1)
    df_sum = df_sum.drop('交通費',axis=1)
    df_sum = df_sum.drop('給料',axis=1)
    df_sheet['合計時間'] = df_sum.sum(axis=1)
    
    #出勤日時ソート 日付のみバラしてソート
    df_date = df_sheet.drop(['時給','交通費','合計時間','給料'],axis=1)
    date_columns = df_date.columns
    date_columns = sorted(date_columns)
    df_date = df_date.reindex(date_columns,axis=1)
    df_sheet = pd.concat([df_sheet[['時給','交通費','合計時間','給料']],df_date],axis=1)

    #エクスポート用ファイル名
    columns = list(df_sheet.columns)
    start = columns[4]
    finish = columns.pop()

    #Streamlit用に0の空白化、数値丸め込み
    df_sheet = df_sheet.replace(0,np.nan)
    df_format = df_sheet.style.highlight_null(props="color: transparent;")
    df_format = df_format.format("{:.1f}".format)

    st.header('集計結果')
    st.dataframe(df_format)

    #合計勤務時間アラート
    df_sheet['index'] = df_sheet.index
    over_80 = []
    for n,i in zip(df_sheet['合計時間'],df_sheet['index']):
        if n>= 80:
            over_80.append(i)

    st.header('勤務時間チェック')
    st.write('勤務時間が80時間を超えているスタッフ：'+str(over_80))

    df_sheet = df_sheet.drop('index',axis=1)
    csv = convert_df(df_sheet)
    st.download_button(label="集計結果出力",data=csv,file_name='from'+start+'to'+finish+'_集計結果.csv',mime='text/csv')      