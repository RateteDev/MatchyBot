# Matchybot

OWのカスタムマッチをする際に自動でチームの振り分けを行ってくれるボット

## 事前準備

### Discord BOTを作成

[Dev Portal](https://discord.com/developers/applications)で**BOTの作成**,**TOKENの発行**,**サーバーへの招待**を済ませておく。

### このリポジトリのクローン作業

Gitを使用してこのリポジトリをクローンしておく。

```bash
git clone https://github.com/RateteDev/MatchyBot
```

## インストール・実行方法

カレントディレクトリがこのプロジェクト担っている状態で作業を始めてください。

```bash
# 依存ライブラリのインストール
uv sync
# Pythonの仮想環境を有効化
source .venv/bin/activate
# .envの作成
cp .env.sample .env
```

`.env`を編集して、`DISCORD_TOKEN`を設定してください。

```ini
# Discord BOT Token
# Get from here: https://discord.com/developers/applications
BOT_TOKEN="YOUR_TOKEN" ← ここにDiscordのBOT Tokenを記述
```

```bash
# 実行
uv run src/main.py
```
