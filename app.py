import streamlit as st

from utils.data_loader import load_data
from services.analysis import analyze_inventory

from services.charts import (
    create_stock_chart,
    create_abc_chart,
    create_risk_chart
)


# =========================
# ページ設定
# =========================

st.set_page_config(
    page_title='在庫最適化ダッシュボード',
    page_icon='📦',
    layout='wide'
)


# =========================
# 上部余白調整
# =========================

st.markdown(
    '''
    <style>
        /* 上部余白を小さくする */
        .block-container {
            padding-top: 1.5rem;
        }

        /* multiselect の選択タグが切れないよう高さ制限を解除 */
        [data-testid="stSidebarContent"] [data-baseweb="select"] > div:first-child {
            max-height: none !important;
            height: auto !important;
            flex-wrap: wrap !important;
        }
    </style>
    ''',
    unsafe_allow_html=True
)

# 画面のタイトルと補足説明
st.title('在庫最適化ダッシュボード')
st.caption('欠品防止・過剰在庫削減・発注判断支援')


# =========================
# CSV読込
# =========================

try:
    # CSVの存在チェック
    df = load_data('./data/sample_inventory.csv')

    # 分析処理
    df = analyze_inventory(df)

except FileNotFoundError:
    st.error('sample_inventory.csv が見つかりません')
    st.stop()


# =========================
# フィルタ設定
# 画面左側に4つのフィルタ機能を設定
# ・警告
# ・カテゴリ（複数選択）
# ・ABCランク（複数選択）
# ・商品名（部分一致のキーワード検索）
# =========================

st.sidebar.header('フィルタ')

# 1.警告フィルタ
alert_filter = st.sidebar.radio(
    '警告フィルタ',
    [
        'すべて',
        '欠品リスクのみ',
        '過剰在庫のみ'
    ]
)

# 2.カテゴリフィルタ
category_list = sorted(
    df['カテゴリ'].unique()
)

selected_categories = st.sidebar.multiselect(
    'カテゴリ選択',
    category_list,
    default = category_list
)

# 3.ABCランクフィルタ
selected_rank = st.sidebar.multiselect(
    'ABCランク',
    ['A', 'B', 'C'],
    default = ['A', 'B', 'C']
)

# 4.商品検索
keyword = st.sidebar.text_input('商品検索')


# =========================
# フィルタ適用
# =========================

# 基本フィルタ
filtered_df = df[
    (df['カテゴリ'].isin(selected_categories))
    & (df['ABCランク'].isin(selected_rank))
]

# 警告フィルタ
if alert_filter == '欠品リスクのみ':
    filtered_df = filtered_df[
        filtered_df['欠品リスク'] == True
    ]

elif alert_filter == '過剰在庫のみ':
    filtered_df = filtered_df[
        filtered_df['過剰在庫'] == True
    ]

# 商品検索
if keyword:
    filtered_df = filtered_df[
        filtered_df['商品名'].str.contains(
            keyword,
            case=False
        )
    ]

# 件数表示
st.caption(f'表示件数: {len(filtered_df)}件')


# =========================
# KPI用集計
# =========================

risk_count = filtered_df['欠品リスク'].sum()
over_count = filtered_df['過剰在庫'].sum()
total_stock = filtered_df['在庫数'].sum()


# =========================
# アラート
# =========================

# 欠品リスクや過剰在庫が1件以上ある場合、画面に警告帯表示
if risk_count > 0:
    st.error(f'欠品リスク商品が {risk_count} 件あります')

if over_count > 0:
    st.warning(f'過剰在庫商品が {over_count} 件あります')

st.markdown('<br>', unsafe_allow_html=True)


# =========================
# KPIカード
# =========================
col1, col2, col3, col4 = st.columns(4)

# 総商品数カード
with col1:
    st.metric('総商品数', f"{len(filtered_df)}件")

# 欠品リスク商品カード
with col2:
    st.metric('欠品リスク商品', f'{risk_count}件')

# 過剰在庫商品カード
with col3:
    st.metric('過剰在庫商品', f'{over_count}件')

# 総在庫数カード
with col4:
    st.metric('総在庫数', f'{total_stock:,}')

st.divider()


# =========================
# グラフ表示
# Plotly Express 視覚的なグラフを描画
# 左側: カテゴリ別在庫数（棒グラフ）
# 右側: ABC分析（円グラフ）
# 下部: 欠品リスク＝在庫回転率 TOP10（棒グラフ）
# 商品一覧: データテーブル（st.dataframe）
# =========================

left_col, right_col = st.columns(2)

# 左側: カテゴリ別在庫数
with left_col:
    fig_stock = create_stock_chart(filtered_df)

    st.plotly_chart(
        fig_stock,
        use_container_width=True
    )

# 右側:ABC分析
with right_col:
    fig_abc = create_abc_chart(filtered_df)

    st.plotly_chart(
        fig_abc,
        use_container_width=True
    )

# 欠品リスク TOP10

st.subheader('欠品リスク商品 TOP10')

risk_df = filtered_df[
    filtered_df['欠品リスク'] == True
]

if len(risk_df) > 0:

    fig_risk = create_risk_chart(
        filtered_df
    )

    st.plotly_chart(
        fig_risk,
        use_container_width=True
    )

else:
    st.success('欠品リスク商品はありません')


# =========================
# データテーブル
# =========================

st.subheader('商品一覧')

display_columns = [
    '商品ID',
    '商品名',
    'カテゴリ',
    '在庫数',
    '月間売上',
    '売上金額',
    '在庫回転率',
    '発注推奨数',
    'ABCランク',
    '欠品リスク',
    '過剰在庫'
]

st.dataframe(
    filtered_df[display_columns],
    use_container_width=True,
    height=600
)


# =========================
# CSVダウンロード
# =========================

csv_data = filtered_df.to_csv(index=False).encode('utf-8-sig')

st.download_button(
    label='分析結果CSVダウンロード',
    data=csv_data,
    file_name='inventory_analysis.csv',
    mime='text/csv'
)
