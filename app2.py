import os
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs

# -----------------------------
# BMI計算ロジック
# -----------------------------
def calculate_bmi(height_cm, weight_kg):
    try:
        h = float(height_cm) / 100
        w = float(weight_kg)
        if h <= 0 or w <= 0:
            return 0, "入力値が不正です"
        bmi = w / (h * h)
    except Exception:
        # 例外時は0扱い
        return 0, "入力値が不正です"

    # 判定
    if bmi < 18.5:
        result = "低体重"
    elif bmi < 25:
        result = "標準体重"
    elif bmi < 30:
        result = "肥満（1度）"
    elif bmi < 35:
        result = "肥満（2度）"
    elif bmi < 40:
        result = "肥満（3度）"
    else:
        result = "肥満（4度）"

    return round(bmi, 2), result


# -----------------------------
# HTTPハンドラ
# -----------------------------
class SimpleHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(self.render_page().encode("utf-8"))

    def do_POST(self):
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length).decode("utf-8")
        params = parse_qs(body)

        height = params.get("height", [""])[0]
        weight = params.get("weight", [""])[0]

        bmi, result = calculate_bmi(height, weight)

        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(self.render_page(height, weight, bmi, result).encode("utf-8"))

    def render_page(self, height="", weight="", bmi=None, result=""):
        result_html = ""
        if bmi is not None:
            result_html = f"""
            <div class="result">
                <p><strong>BMI:</strong> {bmi}</p>
                <p><strong>判定:</strong> {result}</p>
            </div>
            """

        return f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>BMI計算機</title>
<style>
body {{
    font-family: Arial, sans-serif;
    background-color: #f4f6f8;
    padding: 40px;
}}
.container {{
    max-width: 400px;
    margin: auto;
    background: white;
    padding: 20px;
    border-radius: 8px;
    box-shadow: 0 0 10px rgba(0,0,0,0.1);
}}
h1 {{
    text-align: center;
}}
label {{
    display: block;
    margin-top: 10px;
}}
input {{
    width: 100%;
    padding: 8px;
    margin-top: 5px;
}}
button {{
    margin-top: 15px;
    padding: 10px;
    width: 48%;
}}
.buttons {{
    display: flex;
    justify-content: space-between;
}}
.result {{
    margin-top: 20px;
    padding: 10px;
    background: #e9f5ff;
    border-radius: 6px;
}}
</style>
<script>
function clearForm() {{
    document.getElementById("height").value = "";
    document.getElementById("weight").value = "";
}}
</script>
</head>
<body>
<div class="container">
    <h1>BMI計算機</h1>
    <form method="POST">
        <label>身長 (cm)</label>
        <input type="number" step="0.1" name="height" id="height" value="{height}" required>

        <label>体重 (kg)</label>
        <input type="number" step="0.1" name="weight" id="weight" value="{weight}" required>

        <div class="buttons">
            <button type="submit">計算する</button>
            <button type="button" onclick="clearForm()">クリア</button>
        </div>
    </form>
    {result_html}
</div>
</body>
</html>
"""


# -----------------------------
# サーバ起動
# -----------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    server = HTTPServer(("0.0.0.0", port), SimpleHandler)
    print(f"Server running on port {port}")
    server.serve_forever()