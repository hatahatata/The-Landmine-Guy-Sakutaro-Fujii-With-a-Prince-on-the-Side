import base64
import pandas as pd
import requests
import streamlit as st

# --- ページ基本設定 ---
st.set_page_config(
    page_title="🎓 成績ランクAI診断アプリ", page_icon="🔮", layout="wide"
)

# --- API設定 ---
API_KEY = "4273d517-cdc4-48ce-9544-954103110bd6"
API_URL = "https://user-api.predictionone.sony.biz/v1/groups/i5bm94my1c8f99w2/classifiers/1v7ew1izwq4xso6u/inference"

# --- メインヘッダー ---
st.title("🔮 AI学生ライフスタイル診断")
st.caption(
    "あなたの普段の生活習慣や学習スタイルから、AIが将来の成績ランクを精度高く予測します！"
)
st.markdown("---")

# --- 入力フォームセクション ---
st.subheader("📝 あなたのステータスを入力してください")

col1, col2 = st.columns(2)

with col1:
    st.markdown("##### 📚 学習・出席パラメータ")
    study_hours = st.slider("1週間の作業時間 (時間)", 0, 60, 20)
    attendance = st.slider("参加率 (%)", 0, 100, 80)
    assignment = st.slider("課題の提出度 (%)", 0, 100, 75)
    discussions = st.radio(
        "議論・発言の積極性",
        [1, 0],
        format_func=lambda x: "参加している" if x == 1 else "あまり参加していない",
        horizontal=True,
    )

with col2:
    st.markdown("##### 🏠 環境・モチベーション")
    motivation_label = st.selectbox("学習へのモチベーション", ["2: 高い", "1: 普通", "0: 低い"])
    motivation = int(motivation_label.split(":")[0])

    resources = st.slider("活用している教材・リソース数", 0, 5, 2)

    edutech = st.radio(
        "EdTechツール（学習アプリ等）の活用",
        [1, 0],
        format_func=lambda x: "活用している" if x == 1 else "使っていない",
        horizontal=True,
    )
    internet = st.radio(
        "自宅のネット環境",
        [1, 0],
        format_func=lambda x: "快適" if x == 1 else "不安あり",
        horizontal=True,
    )

    with st.expander("👤 基本属性（性別・年齢）"):
        gender = st.selectbox("性別", [0, 1], format_func=lambda x: "女性" if x == 0 else "男性")
        age = st.number_input("年齢", 15, 30, 20)

st.markdown("---")

# --- 診断実行ボタン ---
if st.button("✨ AIで将来の成績を診断する", use_container_width=True, type="primary"):
    with st.spinner(" Prediction One が未来の成績を解析中..."):

        # フォームにある項目のみを辞書にまとめる
        input_data = {
            "StudyHours": [study_hours],
            "Attendance": [attendance],
            "Resources": [resources],
            "Motivation": [motivation],
            "Internet": [internet],
            "Gender": [gender],
            "Age": [age],
            "Discussions": [discussions],
            "AssignmentCompletion": [assignment],
            "EduTech": [edutech],
        }

        # CSV文字列化＆Base64エンコード
        df = pd.DataFrame(input_data)
        csv_str = df.to_csv(index=False)
        lines = csv_str.strip().split("\n")
        csv_payload = lines[0] + "\n" + lines[1] + "\n"
        encoded_data = base64.b64encode(csv_payload.encode("utf-8")).decode("ascii")

        # API通信
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
                    decoded_csv = base64.b64decode(output["data"]).decode("utf-8")
                    result_data = decoded_csv.strip().split("\n")[1].split(",")

                    # 各予測値の取得
                    final_grade = int(result_data[1])
                    prob_0 = float(result_data[2]) * 100
                    prob_1 = float(result_data[3]) * 100
                    prob_2 = float(result_data[4]) * 100
                    prob_3 = float(result_data[5]) * 100

                    st.balloons()
                    st.subheader("🎯 AI診断結果")

                    # ランクごとのエンタメ演出切り替え
                    if final_grade == 0:
                        st.success("### 🏆 判定：【ランク 0】 伝説の無双キャンパスライフ")
                        st.markdown(
                            "**称号: 『学問を極めし絶対覇者』**\n\n"
                            "圧倒的な学習習慣と完璧な自己管理です！このまま進めば学科トップの成績（S評価連発）は間違いありません。"
                        )
                    elif final_grade == 1:
                        st.info("### 🌟 判定：【ランク 1】 秀才エリート")
                        st.markdown(
                            "**称号: 『安定の文武両道プレイヤー』**\n\n"
                            "非常に優れたバランスで学業をこなせています！周囲からの信頼も厚く、上位成績（A評価クラス）を余裕で狙えます。"
                        )
                    elif final_grade == 2:
                        st.warning("### ⚖️ 判定：【ランク 2】 平和主義な標準層")
                        st.markdown(
                            "**称号: 『ギリギリを攻める省エネ思考』**\n\n"
                            "単位取得圏内ですが、少し油断するとランク3へ落ちるリスクも…。あとほんの少しだけ勉強時間を増やすと一気にバケけます！"
                        )
                    elif final_grade == 3:
                        st.error("### 🚨 判定：【ランク 3】 単位危険水域（要警戒！）")
                        st.markdown(
                            "**称号: 『崖っぷちのラストスパート待ち』**\n\n"
                            "このままのペースだと単位を落とす確率が非常に高いです！まずは「出席率の確保」と「課題提出」から速やかに改善を開始しましょう。"
                        )

                    # 確率メーターの表示
                    st.markdown("#### 📊 ランク別の発生確率")
                    m_col0, m_col1, m_col2, m_col3 = st.columns(4)
                    m_col0.metric("ランク 0 (最高)", f"{prob_0:.1f}%")
                    m_col1.metric("ランク 1 (良好)", f"{prob_1:.1f}%")
                    m_col2.metric("ランク 2 (可)", f"{prob_2:.1f}%")
                    m_col3.metric("ランク 3 (危険)", f"{prob_3:.1f}%")

        else:
            st.error("AIサーバーとの通信に失敗しました。")
            st.code(response.text)