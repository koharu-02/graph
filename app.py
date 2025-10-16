import streamlit as st
import pandas as pd
import plotly.express as px

st.title("工程編成検討ツール（IDごとに移動先指定）")

uploaded_file = st.file_uploader("Excelファイルをアップロードしてください（工程, 作業位置, 要素作業, 時間）", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file, engine="openpyxl")
    if 'ID' not in df.columns:
        df['ID'] = df.index.astype(str)

    st.subheader("元データ")
    st.dataframe(df)

    # ラベル列（ID含む）
    df["ラベル"] = "ID:" + df["ID"] + " | " + df["作業位置"] + " | " + df["要素作業"] + " | " + df["時間"].astype(str) + "秒"

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

    st.subheader("IDごとに移動先工程を指定")
    selected_ids = st.multiselect("移動したいIDを選択してください", options=df["ID"])

    move_targets = {}
    for id_ in selected_ids:
        current_process = df.loc[df["ID"] == id_, "工程"].values[0]
        move_targets[id_] = st.selectbox(
            f"ID:{id_}（現在：{current_process}）の移動先工程",
            options=[x for x in sorted(df["工程"].unique()) if x != current_process],
            key=f"move_{id_}"
        )

    if st.button("✅ 一括移動実行"):
        for id_, to_process in move_targets.items():
            df.loc[df["ID"] == id_, "工程"] = to_process

        st.success(f"{len(move_targets)} 件のIDの移動を実行しました。")

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