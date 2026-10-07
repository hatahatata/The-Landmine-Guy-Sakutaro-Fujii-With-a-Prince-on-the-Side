import base64
import requests
import pandas as pd

# 1. API設定情報
API_KEY = "cef3ba7f-8758-4678-a5ef-b7fb16e05a95"
API_URL = "https://user-api.predictionone.sony.biz/v1/groups/qejw062trt0qwwav/classifiers/cs4tql0478nmeecr/inference"

# 2. テスト用データの作成
data = {
    'StudyHours': [25, 10, 35, 18, 20],
    'Attendance': [90, 65, 95, 75, 80],
    'Resources': [2, 0, 2, 1, 1],
    'Extracurricular': [1, 0, 1, 0, 1],
    'Motivation': [2, 0, 2, 1, 1],
    'Internet': [1, 1, 1, 1, 1],
    'Gender': [0, 1, 1, 0, 1],
    'Age': [20, 22, 19, 21, 23],
    'LearningStyle': [1, 2, 3, 1, 2],
    'OnlineCourses': [10, 3, 15, 8, 12],
    'Discussions': [1, 0, 1, 1, 0],
    'AssignmentCompletion': [85, 55, 95, 70, 78],
    'EduTech': [1, 0, 1, 0, 1],
    'StressLevel': [1, 2, 0, 1, 1],
}

# DataFrameをCSV形式の文字列に変換し、ヘッダーとデータ行に分ける
df = pd.DataFrame(data)
csv_str = df.to_csv(index=False)
lines = csv_str.strip().split('\n')
header = lines[0] + '\n'

headers = {
    'x-api-key': API_KEY,
    'content-type': 'application/json; charset=utf-8'
}

# 3. 1人（1行）ずつAPIにリクエストを送信
for idx, line in enumerate(lines[1:]):
    # ヘッダーと1行分のデータを結合し、Base64にエンコード
    csv_payload = header + line + '\n'
    encoded_data = base64.b64encode(csv_payload.encode('utf-8')).decode('ascii')

    # マニュアルで指定された正しいリクエストボディの構造
    body = {
        "inputs": [
            {
                "name": "pr",
                "type": "csv",
                "data": encoded_data
            },
            {
                "name": "ar",
                "type": "boolean",
                "data": False  # 処理を早くするため予測理由(寄与度)の出力をオフ
            },
            {
                "name": "ad",
                "type": "boolean",
                "data": True   # 結果に元のデータを含める
            },
            {
                "name": "nc",
                "type": "boolean",
                "data": False  # 予測結果（確率など）を出力させるためFalse
            }
        ]
    }

    response = requests.post(API_URL, headers=headers, json=body)

    # 4. 結果のデコードと表示
    if response.status_code == 200:
        response_json = response.json()
        if 'outputs' in response_json:
            for output in response_json['outputs']:
                # 返ってきたBase64形式のCSV結果を元の文字列に戻して表示
                if output['name'] == 'prediction_valid.csv':
                    decoded_csv = base64.b64decode(output['data']).decode('utf-8')
                    print(f"=== 【{idx + 1}人目】の予測成功 ===")
                    
                    # 見やすくするために結果のCSVから2行目（結果データ）だけ抽出
                    result_lines = decoded_csv.strip().split('\n')
                    print("ヘッダー:", result_lines[0])
                    print("データ  :", result_lines[1])
                    print("-" * 50)
    else:
        print(f"エラーが発生しました: {response.status_code}")
        print(response.text)