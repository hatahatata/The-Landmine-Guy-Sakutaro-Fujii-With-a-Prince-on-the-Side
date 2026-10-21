import base64
import pandas as pd
import requests
import streamlit as st

# --- ページ基本設定 ---
st.set_page_config(
    page_title="🎓 成績ランクAI診断アプリ", page_icon="🔮", layout="wide"
)

# --- API設定 ---
API_KEY = "df4d195d-dfa9-4e10-b515-77e15096d492"
API_URL = "https://user-api.predictionone.sony.biz/v1/groups/qejw062trt0qwwav/classifiers/quipaioomqira6hd/inference"

# --- メインヘッダー ---
st.title("🔮 AI学生ライフスタイル診断 (地雷判定モード)")
st.caption(
    "グループの中で誰が一番危険か！？AIが未来の成績ランクを予測して地雷者を認定します！"
)
st.markdown("---")

# --- 人数設定（サイドバー） ---
st.sidebar.header("⚙️ 設定")
num_players = st.sidebar.number_input(
    "参加人数", min_value=1, max_value=5, value=2, step=1
)

# --- プレイヤー情報の入力セクション ---
st.subheader("📝 ステータス入力")
tabs = st.tabs([f"👤 プレイヤー {i+1}" for i in range(num_players)])

players_data = []

for i, tab in enumerate(tabs):
    with tab:
        name = st.text_input(
            f"プレイヤー {i+1} の名前",
            value=f"プレイヤー {i+1}",
            key=f"name_{i}",
        )

        col1, col2 = st.columns(2)
        with col1:
            st.markdown("##### 📚 学習・出席パラメータ")
            study_hours = st.slider(
                "1週間の学習時間 (時間)", 0, 60, 20, key=f"study_{i}"
            )
            attendance = st.slider(
                "授業の出席率 (%)", 0, 100, 80, key=f"att_{i}"
            )
            assignment = st.slider(
                "課題の完了度 (%)", 0, 100, 75, key=f"ass_{i}"
            )
            discussions = st.radio(
                "ディスカッションへの積極参加",
                [1, 0],
                format_func=lambda x: (
                    "参加している" if x == 1 else "あまり参加していない"
                ),
                horizontal=True,
                key=f"disc_{i}",
            )

        with col2:
            st.markdown("##### 🏠 環境・モチベーション")
            motivation_label = st.selectbox(
                "学習へのモチベーション",
                ["2: 高い", "1: 普通", "0: 低い"],
                key=f"mot_{i}",
            )
            motivation = int(motivation_label.split(":")[0])

            resources = st.slider(
                "活用している教材・リソース数", 0, 5, 2, key=f"res_{i}"
            )

            edutech = st.radio(
                "EdTechツール（学習アプリ等）の活用",
                [1, 0],
                format_func=lambda x: (
                    "活用している" if x == 1 else "使っていない"
                ),
                horizontal=True,
                key=f"edu_{i}",
            )
            internet = st.radio(
                "自宅のネット環境",
                [1, 0],
                format_func=lambda x: "快適" if x == 1 else "不安あり",
                horizontal=True,
                key=f"net_{i}",
            )

            with st.expander("👤 基本属性（性別・年齢）"):
                gender = st.selectbox(
                    "性別",
                    [0, 1],
                    format_func=lambda x: "女性" if x == 0 else "男性",
                    key=f"gen_{i}",
                )
                age = st.number_input("年齢", 15, 30, 20, key=f"age_{i}")

        players_data.append({
            "Name": name,
            "StudyHours": study_hours,
            "Attendance": attendance,
            "Resources": resources,
            "Motivation": motivation,
            "Internet": internet,
            "Gender": gender,
            "Age": age,
            "Discussions": discussions,
            "AssignmentCompletion": assignment,
            "EduTech": edutech,
        })

st.markdown("---")

# --- 診断実行ボタン ---
if st.button("💣 全員の成績と地雷判定を実行", use_container_width=True, type="primary"):

    results_list = []

    with st.spinner("Prediction One が分析中..."):

        # 全員のAPI通信を実行してデータを収集
        for i, p_data in enumerate(players_data):

            input_data = {
                "StudyHours": [p_data["StudyHours"]],
                "Attendance": [p_data["Attendance"]],
                "Resources": [p_data["Resources"]],
                "Motivation": [p_data["Motivation"]],
                "Internet": [p_data["Internet"]],
                "Gender": [p_data["Gender"]],
                "Age": [p_data["Age"]],
                "Discussions": [p_data["Discussions"]],
                "AssignmentCompletion": [p_data["AssignmentCompletion"]],
                "EduTech": [p_data["EduTech"]],
            }

            df = pd.DataFrame(input_data)
            csv_str = df.to_csv(index=False)
            encoded_data = base64.b64encode(csv_str.encode("utf-8")).decode(
                "ascii"
            )

            headers = {
                "x-api-key": API_KEY,
                "content-type": "application/json; charset=utf-8",
            }
            body = {
                "inputs": [
                    {"name": "pr", "type": "csv", "data": encoded_data},
                    {"name": "ar", "type": "boolean", "data": False},
                    {"name": "ad", "type": "boolean", "data": True},
                    {"name": "nc", "type": "boolean", "data": False},
                ]
            }

            response = requests.post(API_URL, headers=headers, json=body)

            if response.status_code == 200:
                response_json = response.json()
                for output in response_json.get("outputs", []):
                    if output["name"] == "prediction_valid.csv":
                        decoded_csv = base64.b64decode(output["data"]).decode(
                            "utf-8"
                        )
                        result_data = (
                            decoded_csv.strip().split("\n")[1].split(",")
                        )

                        final_grade = int(result_data[1])
                        prob_0 = float(result_data[2]) * 100
                        prob_1 = float(result_data[3]) * 100
                        prob_2 = float(result_data[4]) * 100
                        prob_3 = float(result_data[5]) * 100

                        # スコア化（ランクが高いほど危険 + ランク3の確率が高いほどスコア大）
                        risk_score = final_grade * 100 + prob_3

                        results_list.append({
                            "name": p_data["Name"],
                            "final_grade": final_grade,
                            "prob_0": prob_0,
                            "prob_1": prob_1,
                            "prob_2": prob_2,
                            "prob_3": prob_3,
                            "risk_score": risk_score,
                        })
            else:
                # 💡 エラー内容を詳細に取得して保存
                results_list.append({
                    "name": p_data["Name"],
                    "error": True,
                    "risk_score": -1,
                    "error_detail": f"HTTP {response.status_code}: {response.text}"
                })

    # 一番危険度が高い人を特定（リスクスコアが最大の人）
    if results_list:
        max_risk_player = max(results_list, key=lambda x: x["risk_score"])

        st.subheader("🎯 診断結果発表！")

        # 地雷認定の特別通知
        if num_players > 1 and max_risk_player.get("risk_score", 0) > 0:
            st.error(
                f"⚠️ **【地雷認定】** 今回のメンバーの中で最も成績リスクが高い地雷人物は **『{max_risk_player['name']}』** です！速やかに生活習慣を見直してください！"
            )

        st.markdown("---")

        # 結果をカード並びで表示
        result_cols = st.columns(num_players)

        for i, res in enumerate(results_list):
            with result_cols[i]:

                # 地雷認定されたプレイヤーへのハイライトマーク
                if (
                    num_players > 1
                    and res["name"] == max_risk_player["name"]
                    and not res.get("error")
                ):
                    st.markdown(f"### 💣 {res['name']} *(地雷!)*")
                else:
                    st.markdown(f"### 👤 {res['name']}")

                if not res.get("error"):
                    fg = res["final_grade"]

                    if fg == 0:
                        st.success("**🏆 ランク 0**\n\n絶対覇者！S評価連発！")
                    elif fg == 1:
                        st.info("**🌟 ランク 1**\n\n秀才エリート！安定のA評価")
                    elif fg == 2:
                        st.warning(
                            "**⚖️ ランク 2**\n\n標準層。少し油断すると危険！"
                        )
                    elif fg == 3:
                        st.error(
                            "**🚨 ランク 3**\n\n要警戒！単位落下の危険大！"
                        )

                    st.caption("予測確率")
                    st.progress(
                        res["prob_0"] / 100, text=f"ランク0: {res['prob_0']:.1f}%"
                    )
                    st.progress(
                        res["prob_1"] / 100, text=f"ランク1: {res['prob_1']:.1f}%"
                    )
                    st.progress(
                        res["prob_2"] / 100, text=f"ランク2: {res['prob_2']:.1f}%"
                    )
                    st.progress(
                        res["prob_3"] / 100, text=f"ランク3: {res['prob_3']:.1f}%"
                    )
                else:
                    # 💡 実際のエラーメッセージを画面に出力
                    st.error(f"通信エラーが発生しました\n\n詳細: {res.get('error_detail', '不明なエラー')}")