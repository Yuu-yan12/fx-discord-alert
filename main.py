import requests
import yfinance as yf

DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/1455074360665833493/DcIXt_Z855lraR55IUOofIIYd7LuliRdl1_KAlxNFInWFmv3d-h9JSmT0suDiszYgVoP"

def send_discord(message: str) -> None:
    payload = {"content": message}
    response = requests.post(DISCORD_WEBHOOK_URL, json=payload, timeout=10)
    response.raise_for_status()

def get_current_price(ticker: str) -> float:
    df = yf.download(
        tickers=ticker,
        period="1d",
        interval="1m",
        progress=False
    )
    if df.empty:
        raise RuntimeError("価格データが取得できませんでした")
    return float(df["Close"].iloc[-1])

if __name__ == "__main__":
    ticker = "USDJPY=X"
    price = get_current_price(ticker)
    print(f"Current price ({ticker}): {price}")
