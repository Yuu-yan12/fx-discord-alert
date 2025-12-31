# FX Discord Alert

FXの価格が指定したラインを上抜け / 下抜けしたときに  
Discordへ通知する Flask 製 Web アプリです。

## Features
- 複数通貨ペア対応
- 複数アラート同時監視
- Web UI から追加 / 編集 / 削除
- Discord Webhook 通知
- JSON による設定の永続化

## Tech Stack
- Python
- Flask
- HTML / CSS
- yfinance
- Discord Webhook

## Setup
```bash
pip install -r requirements.txt
python app.py


## Notes
- This project is for learning purposes.
- Flask development server is used.
- Not intended for production use.