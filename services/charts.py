import plotly.express as px


# =========================
# カテゴリ別在庫数グラフ（棒グラフ）
# =========================

def create_stock_chart(df):

    stock_chart = (
        df.groupby('カテゴリ')['在庫数']
        .sum()
        .reset_index()
    )

    #棒グラフを作成
    fig = px.bar(
        stock_chart,
        x='カテゴリ',
        y='在庫数',
        title='カテゴリ別在庫数'
    )

    return fig


# =========================
# ABC分析グラフ（円グラフ）
# =========================

def create_abc_chart(df):

    abc_chart = (
        df['ABCランク']
        .value_counts()
        .reset_index()
    )

    # .value_counts() を行うと列名が自動設定されるため列名を変更する
    abc_chart.columns = [
        'ABCランク',
        '件数'
    ]

    # 円グラフを作成
    fig = px.pie(
        abc_chart,
        names='ABCランク',
        values='件数',
        title='ABC分析'
    )

    return fig


# =========================
# 欠品リスクTOP10グラフ（色分け棒グラフ）
# =========================

def create_risk_chart(df):

    # 「欠品リスク」列の値がTrueのみ抽出
    risk_df = df[
        df['欠品リスク'] == True
    ]

    # sort後、上位10件だけ抽出
    risk_df = risk_df.sort_values(
        by='在庫回転率',
        ascending=False
    ).head(10)

    # 棒グラフを作成
    # 商品の「カテゴリ」ごとに色を自動で塗り分け
    fig = px.bar(
        risk_df,
        x='商品名',
        y='在庫回転率',
        color='カテゴリ',
        title='在庫回転率が高い商品'
    )

    return fig