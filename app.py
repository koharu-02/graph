import streamlit as st
import pandas as pd
import plotly.express as px

st.title("工程編成検討ツール（要素作業ごと複数工程一括移動対応）")

uploaded_file = st.file_uploader("Excelファイルをアップロードしてください（工程, 作業位置, 要素作業, 時間）", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file, engine="openpyxl")
    if 'ID' not in df.columns:
        df['ID'] = df.index.astype(str)

    st.subheader("元データ")
    st.dataframe(df)

    # ラベル列（ID含む）
    df["ラベル"] = "ID:" + df["ID"] + " | " + df["作業位置"] + " | " + df["要素作業"] + " | " + df["時間"].astype(str) + "分"

    # 初期グラフ
    fig = px.bar(
        df,
        x="工程",
        y="時間",
        color="要素作業",
        text="ラベル",
        hover_data=["ID", "作業位置", "要素作業", "時間"],
        title="工程別作業時間（積み上げ棒グラフ）"
    )
    fig.update_traces(marker=dict(line=dict(color="black", width=1)))
    fig.update_layout(barmode="stack", xaxis_title="工程", yaxis_title="時間")
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("要素作業ごとの複数工程一括移動設定")
    move_count = st.number_input("移動ペア数を入力してください", min_value=1, max_value=10, value=2)

    move_pairs = []
    for i in range(move_count):
        st.write(f"移動ペア {i+1}")
        element = st.selectbox(f"要素作業 {i+1}", options=sorted(df["要素作業"].unique()), key=f"element_{i}")
        from_process = st.selectbox(f"移動元工程 {i+1}", options=sorted(df["工程"].unique()), key=f"from_{i}")
        to_process = st.selectbox(f"移動先工程 {i+1}", options=sorted(df["工程"].unique()), key=f"to_{i}")
        move_pairs.append((element, from_process, to_process))

    if st.button("✅ 一括移動実行"):
        for element, from_process, to_process in move_pairs:
            mask = (df["工程"] == from_process) & (df["要素作業"] == element)
            df.loc[mask, "工程"] = to_process

        st.success(f"{len(move_pairs)} ペアの移動を実行しました。")

        # ラベル更新
        df["ラベル"] = "ID:" + df["ID"] + " | " + df["作業位置"] + " | " + df["要素作業"] + " | " + df["時間"].astype(str) + "分"

        # 更新後グラフ
        fig_updated = px.bar(
            df,
            x="工程",
            y="時間",
            color="要素作業",
            text="ラベル",
            hover_data=["ID", "作業位置", "要素作業", "時間"],
            title="更新後の工程別作業時間"
        )
        fig_updated.update_traces(marker=dict(line=dict(color="black", width=1)))
        fig_updated.update_layout(barmode="stack", xaxis_title="工程", yaxis_title="時間")
        st.plotly_chart(fig_updated, use_container_width=True)

        updated_filename = "updated_process_plan.xlsx"
        df.drop(columns=["ID"]).to_excel(updated_filename, index=False)
        with open(updated_filename, "rb") as f:
            st.download_button("📥 更新後のExcelファイルをダウンロード", f, file_name=updated_filename)