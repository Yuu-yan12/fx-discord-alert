import time
import requests
import yfinance as yf

# ====================
# 設定
# ====================
TICKER = "USDJPY=X"
ALERT_PRICE = 156.30
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

    while True:
        try:
            prev_price, curr_price = get_latest_prices()
            print(f"Price: {prev_price} → {curr_price}")

            if is_breakout(prev_price, curr_price):
                direction_jp = "上抜け" if DIRECTION == "break_above" else "下抜け"
                message = (
                    "📈 **FX Price Alert**\n"
                    f"Pair: {TICKER}\n"
                    f"Condition: {ALERT_PRICE} を {direction_jp}\n"
                    f"Current Price: {curr_price}"
                )
                send_discord(message)
                print("✅ Alert sent to Discord")
                break  # 1回通知したら終了（外せば常時監視）

        except Exception as e:
            print("⚠️ Error:", e)

        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    main()
