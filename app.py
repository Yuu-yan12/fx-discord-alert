from flask import Flask, render_template, request, redirect, url_for
from dotenv import load_dotenv
import json
import uuid
import threading
import time
import requests
import yfinance as yf
import os

load_dotenv()

DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")
CHECK_INTERVAL = int(os.getenv("CHECK_INTERVAL", 60))


app = Flask(__name__)
ALERTS_FILE = "alerts.json"

def load_alerts():
    try:
        with open(ALERTS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def save_alerts(alerts):
    with open(ALERTS_FILE, "w", encoding="utf-8") as f:
        json.dump(alerts, f, ensure_ascii=False, indent=2)

@app.route("/", methods=["GET"])
def index():
    alerts = load_alerts()
    return render_template("index.html", alerts=alerts)

@app.route("/add", methods=["POST"])
def add_alert():
    alerts = load_alerts()
    alerts.append({
        "id": str(uuid.uuid4()),
        "ticker": request.form["ticker"],
        "price": float(request.form["price"]),
        "direction": request.form["direction"]
    })
    save_alerts(alerts)
    return redirect(url_for("index"))

# ★ 追加：削除
@app.route("/delete/<alert_id>", methods=["POST"])
def delete_alert(alert_id):
    alerts = load_alerts()
    alerts = [a for a in alerts if a["id"] != alert_id]
    save_alerts(alerts)
    return redirect(url_for("index"))

@app.route("/edit/<alert_id>", methods=["GET", "POST"])
def edit_alert(alert_id):
    alerts = load_alerts()
    alert = next((a for a in alerts if a["id"] == alert_id), None)

    if alert is None:
        return redirect(url_for("index"))

    if request.method == "POST":
        alert["ticker"] = request.form["ticker"]
        alert["price"] = float(request.form["price"])
        alert["direction"] = request.form["direction"]
        save_alerts(alerts)
        return redirect(url_for("index"))

    return render_template("edit.html", alert=alert)


def send_discord(message: str) -> None:
    if not DISCORD_WEBHOOK_URL:
        print("⚠️ DISCORD_WEBHOOK_URL が未設定です")
        return
    requests.post(DISCORD_WEBHOOK_URL, json={"content": message}, timeout=10)

def get_latest_prices(ticker: str):
    df = yf.download(
        tickers=ticker,
        period="1d",
        interval="1m",
        auto_adjust=False,
        progress=False
    )
    if df.empty or len(df) < 2:
        return None
    return (
        float(df["Close"].iloc[-2].item()),
        float(df["Close"].iloc[-1].item())
    )

def is_breakout(prev_price, curr_price, level, direction):
    if direction == "break_above":
        return prev_price < level <= curr_price
    elif direction == "break_below":
        return prev_price > level >= curr_price
    return False

CHECK_INTERVAL = 60  # 秒

def alert_monitor():
    print("🔔 Alert monitor started")
    alert_state = {}

    while True:
        alerts = load_alerts()

        for alert in alerts:
            key = (alert["id"])
            ticker = alert["ticker"]
            level = alert["price"]
            direction = alert["direction"]

            prices = get_latest_prices(ticker)
            if prices is None:
                continue

            prev_price, curr_price = prices

            if key not in alert_state:
                alert_state[key] = False

            # ブレイク検知
            if not alert_state[key] and is_breakout(prev_price, curr_price, level, direction):
                direction_jp = "上抜け" if direction == "break_above" else "下抜け"
                msg = (
                    "📈 FX Alert\n"
                    f"{ticker}\n"
                    f"{level} を {direction_jp}\n"
                    f"現在値: {curr_price}"
                )
                send_discord(msg)
                alert_state[key] = True

            # リセット条件
            if alert_state[key]:
                if direction == "break_above" and curr_price < level:
                    alert_state[key] = False
                elif direction == "break_below" and curr_price > level:
                    alert_state[key] = False

        time.sleep(CHECK_INTERVAL)


if __name__ == "__main__":
    thread = threading.Thread(target=alert_monitor, daemon=True)
    thread.start()

    app.run(debug=True, use_reloader=False)
