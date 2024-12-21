# Matchybot

OWのカスタムマッチをする際に自動でチームの振り分けを行ってくれるボット

## Install

**Prerequisite**

- git
- uv

> [!NOTE]
> uv install here : https://docs.astral.sh/uv/getting-started/installation/#standalone-installer

**Script**

```bash
# Clone this repository
git clone https://github.com/RateteDev/MatchyBot.git
# Change directory
cd MatchyBot
# Install the dependencies
uv sync
# Install the package
uv pip install -e .
# Copy .env.sample to .env
cp .env.sample .env
```

## Run

> [!IMPORTANT]
> Don't forget set the environment variables in the `.env` file, before running the bot

```bash
source .venv/bin/activate
python main.py
```
