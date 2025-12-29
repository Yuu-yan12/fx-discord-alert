import requests

DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/1455074360665833493/DcIXt_Z855lraR55IUOofIIYd7LuliRdl1_KAlxNFInWFmv3d-h9JSmT0suDiszYgVoP"

def send_discord(message: str) -> None:
    payload = {
        "content": message
    }
    response = requests.post(DISCORD_WEBHOOK_URL, json=payload)
    response.raise_for_status()

if __name__ == "__main__":
    send_discord("🚀 FX Discord Alert started!")