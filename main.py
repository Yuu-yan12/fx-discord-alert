import time
import requests
import yfinance as yf

# ====================
# 設定
# ====================
TICKER = "USDJPY=X"
ALERT_PRICE = 155.950
DIRECTION = "break_above"  # break_above / break_below
CHECK_INTERVAL = 60        # 秒

DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/1455074360665833493/DcIXt_Z855lraR55IUOofIIYd7LuliRdl1_KAlxNFInWFmv3d-h9JSmT0suDiszYgVoP"

# ====================
# Discord通知
# ====================
def send_discord(message: str) -> None:
    payload = {"content": message}
    response = requests.post(DISCORD_WEBHOOK_URL, json=payload, timeout=10)
    response.raise_for_status()

# ====================
# 価格取得（直近2本）
# ====================
def get_latest_prices() -> tuple[float, float]:
    df = yf.download(
        tickers=TICKER,
        period="1d",
        interval="1m",
        progress=False
    )
    if df.empty or len(df) < 2:
        raise RuntimeError("価格データが不足しています")

    prev_price = float(df["Close"].iloc[-2])
    curr_price = float(df["Close"].iloc[-1])
    return prev_price, curr_price

# ====================
# ブレイク判定~
# ====================
def is_breakout(prev_price: float, curr_price: float) -> bool:
    if DIRECTION == "break_above":
        return prev_price < ALERT_PRICE <= curr_price
    elif DIRECTION == "break_below":
        return prev_price > ALERT_PRICE >= curr_price
    return False

# ====================
# メイン処理
# ====================
def main():
    print("🔍 Price alert monitoring started")
    alert_triggered = False

    while True:
        try:
            prices = get_latest_prices()
            if prices is None:
                time.sleep(CHECK_INTERVAL)
                continue

            prev_price, curr_price = prices
            print(f"Price: {prev_price} → {curr_price}")

            # ===== ブレイク判定 =====
            if not alert_triggered and is_breakout(prev_price, curr_price):
                direction_jp = "上抜け" if DIRECTION == "break_above" else "下抜け"
                message = (
                    "📈 **FX Price Alert**\n"
                    f"Pair: {TICKER}\n"
                    f"Condition: {ALERT_PRICE} を {direction_jp}\n"
                    f"Current Price: {curr_price}"
                )
                send_discord(message)
                print("✅ Alert sent to Discord")
                alert_triggered = True

            # ===== フラグ解除条件 =====
            if alert_triggered:
                if DIRECTION == "break_above" and curr_price < ALERT_PRICE:
                    alert_triggered = False
                    print("🔄 Alert reset (price below alert line)")
                elif DIRECTION == "break_below" and curr_price > ALERT_PRICE:
                    alert_triggered = False
                    print("🔄 Alert reset (price above alert line)")

        except Exception as e:
            print("⚠️ Error:", e)

        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    main()
