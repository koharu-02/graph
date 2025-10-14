import streamlit as st
import pandas as pd
import plotly.express as px

st.title("工程編成検討ツール")

uploaded_file = st.file_uploader("Excelファイルをアップロードしてください（工程, 作業位置, 要素作業, 時間）", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file, engine="openpyxl")
    if 'ID' not in df.columns:
        df['ID'] = df.index.astype(str)

    st.subheader("元データ")
    st.dataframe(df)

    fig = px.bar(
        df,
        x="工程",
        y="時間",
        color="要素作業",
        text="作業位置",
        hover_data=["ID", "作業位置", "要素作業", "時間"],
        title="工程別作業時間（積み上げ棒グラフ）"
    )
    fig.update_layout(barmode="stack", xaxis_title="工程", yaxis_title="時間")
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("作業の移動")
    selected_ids = st.multiselect("移動する作業IDを選択してください", options=df["ID"])
    target_process = st.selectbox("移動先の工程を選択してください", options=sorted(df["工程"].unique()))

    if st.button("✅ 移動実行"):
        df.loc[df["ID"].isin(selected_ids), "工程"] = target_process
        st.success(f"{len(selected_ids)} 件の作業を工程 {target_process} に移動しました。")

        fig_updated = px.bar(
            df,
            x="工程",
            y="時間",
            color="要素作業",
            text="作業位置",
            hover_data=["ID", "作業位置", "要素作業", "時間"],
            title="更新後の工程別作業時間"
        )
        fig_updated.update_layout(barmode="stack", xaxis_title="工程", yaxis_title="時間")
        st.plotly_chart(fig_updated, use_container_width=True)

        updated_filename = "updated_process_plan.xlsx"
        df.drop(columns=["ID"]).to_excel(updated_filename, index=False)
        with open(updated_filename, "rb") as f:
            st.download_button("📥 更新後のExcelファイルをダウンロード", f, file_name=updated_filename)
