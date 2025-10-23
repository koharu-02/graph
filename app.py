import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(layout="wide")
st.title("工程編成検討ツール（IDごとに移動先指定）")

uploaded_file = st.file_uploader("Excelファイルをアップロードしてください（工程, 作業位置, 要素作業, 時間）", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file, engine="openpyxl")

    # ID割り振り（歩行は下の行と工程が同じなら同じID）
    ids = []
    current_id = 1
    n = len(df)
    for i in reversed(range(n)):
        if df.loc[i, "要素作業"] == "歩行":
            if i + 1 < n and df.loc[i, "工程"] == df.loc[i + 1, "工程"]:
                ids.append(None)
            else:
                ids.append(current_id)
                current_id += 1
        else:
            ids.append(current_id)
            current_id += 1
    ids = ids[::-1]
    for i in range(n):
        if ids[i] is None:
            ids[i] = ids[i + 1]
    df["ID"] = ids

    st.subheader("元データ")
    st.dataframe(df)

    # ラベル列（ID含む）＋ 作業位置がない場合は「なし」と表示
    df["ラベル"] = "ID:" + df["ID"].astype(str) + " | " + df["作業位置"].fillna("なし") + " | " + df["要素作業"] + " | " + df["時間"].astype(str) + "秒"

    # 色分けカテゴリ：作業位置があればそれを、なければ要素作業を使う
    df["色分けカテゴリ"] = df["作業位置"].where(df["作業位置"].notna(), df["要素作業"])

    # 初期グラフ
    fig = px.bar(
        df,
        x="工程",
        y="時間",
        color="色分けカテゴリ",
        text="ラベル",
        hover_data=["ID", "作業位置", "要素作業", "時間"],
        title="工程別作業時間（作業位置または要素作業ごとに積み上げ）"
    )
    fig.update_traces(marker=dict(line=dict(color="black", width=1)))
    fig.update_layout(
        barmode="stack",
        xaxis_title="工程",
        yaxis_title="時間",
        showlegend=False,
        height=600,
        margin=dict(l=40, r=40, t=60, b=40)
    )
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("IDごとに移動先工程を指定（直接入力）")
    id_input = st.text_input("移動したいIDをカンマ区切りで入力してください（例: 1,2,5）")

    try:
        selected_ids = [int(x.strip()) for x in id_input.split(",") if x.strip()]
    except ValueError:
        st.error("IDは数値で入力してください。")
        selected_ids = []

    move_targets = {}
    for id_ in selected_ids:
        if id_ in df["ID"].values:
            current_process = df.loc[df["ID"] == id_, "工程"].values[0]
            move_targets[id_] = st.selectbox(
                f"ID:{id_}（現在：{current_process}）の移動先工程",
                options=[x for x in sorted(df["工程"].unique()) if x != current_process],
                key=f"move_{id_}"
            )
        else:
            st.warning(f"ID:{id_} はデータに存在しません。")

    if st.button("✅ 一括移動実行"):
        for id_, to_process in move_targets.items():
            df.loc[df["ID"] == id_, "工程"] = to_process

        st.success(f"{len(move_targets)} 件のIDの移動を実行しました。")

        # ラベルと色分けカテゴリを再計算
        df["ラベル"] = "ID:" + df["ID"].astype(str) + " | " + df["作業位置"].fillna("なし") + " | " + df["要素作業"] + " | " + df["時間"].astype(str) + "秒"
        df["色分けカテゴリ"] = df["作業位置"].where(df["作業位置"].notna(), df["要素作業"])

        # 更新後グラフ
        fig_updated = px.bar(
            df,
            x="工程",
            y="時間",
            color="色分けカテゴリ",
            text="ラベル",
            hover_data=["ID", "作業位置", "要素作業", "時間"],
            title="更新後の工程別作業時間（作業位置または要素作業ごとに積み上げ）"
        )
        fig_updated.update_traces(marker=dict(line=dict(color="black", width=1)))
        fig_updated.update_layout(
            barmode="stack",
            xaxis_title="工程",
            yaxis_title="時間",
            showlegend=False,
            height=600,
            margin=dict(l=40, r=40, t=60, b=40)
        )
        st.plotly_chart(fig_updated, use_container_width=True)

        updated_filename = "updated_process_plan.xlsx"
        df.drop(columns=["色分けカテゴリ"]).to_excel(updated_filename, index=False)
        with open(updated_filename, "rb") as f:
            st.download_button("📥 更新後のExcelファイルをダウンロード", f, file_name=updated_filename)