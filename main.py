import time
import requests
import yfinance as yf

CHECK_INTERVAL = 60
DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/1455244327830945934/g3Fsmufx-LTlXzc-PLmpQKdEn0ThFEFfFm9Oy57Wc0lY0kQHo-RnILEBDGkNuU4WNqj9"

# ====================
# 監視設定
# ====================
ALERT_CONFIG = {
    "USDJPY=X": {
        "direction": "break_above",
        "levels": [156.11, 156.0, 157.0]
    },
    "EURUSD=X": {
        "direction": "break_below",
        "levels": [1.080, 1.075]
    }
}

# ====================
# Discord通知
# ====================
def send_discord(message: str) -> None:
    payload = {"content": message}
    res = requests.post(DISCORD_WEBHOOK_URL, json=payload, timeout=10)
    res.raise_for_status()

# ====================
# 価格取得
# ====================
def get_latest_prices(ticker: str) -> tuple[float, float] | None:
    df = yf.download(
        tickers=ticker,
        period="1d",
        interval="1m",
        auto_adjust=False,
        progress=False
    )
    if df.empty or len(df) < 2:
        return None

    prev_price = df["Close"].iloc[-2].item()
    curr_price = df["Close"].iloc[-1].item()
    return float(prev_price), float(curr_price)

# ====================
# ブレイク判定
# ====================
def is_breakout(prev: float, curr: float, level: float, direction: str) -> bool:
    if direction == "break_above":
        return prev < level <= curr
    elif direction == "break_below":
        return prev > level >= curr
    return False

# ====================
# メイン処理
# ====================
def main():
    print("🔍 Multi-pair alert monitoring started")

    # 通貨×ラインごとの状態
    alert_state = {}

    # 初期化
    for ticker, cfg in ALERT_CONFIG.items():
        for level in cfg["levels"]:
            alert_state[(ticker, level)] = False

    while True:
        for ticker, cfg in ALERT_CONFIG.items():
            prices = get_latest_prices(ticker)
            if prices is None:
                continue

            prev_price, curr_price = prices
            print(f"{ticker}: {prev_price} → {curr_price}")

            for level in cfg["levels"]:
                key = (ticker, level)
                direction = cfg["direction"]

                # ===== ブレイク検知 =====
                if not alert_state[key] and is_breakout(prev_price, curr_price, level, direction):
                    direction_jp = "上抜け" if direction == "break_above" else "下抜け"
                    message = (
                        "📈 **FX Price Alert**\n"
                        f"Pair: {ticker}\n"
                        f"Level: {level} ({direction_jp})\n"
                        f"Current Price: {curr_price}"
                    )
                    send_discord(message)
                    alert_state[key] = True
                    print(f"✅ Alert sent: {ticker} {level}")

                # ===== リセット条件 =====
                if alert_state[key]:
                    if direction == "break_above" and curr_price < level:
                        alert_state[key] = False
                    elif direction == "break_below" and curr_price > level:
                        alert_state[key] = False

        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    main()
