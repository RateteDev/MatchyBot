#!/bin/sh

# Clone this repository
git clone https://github.com/RateteDev/MatchyBot.git

# Change directory
cd MatchyBot

# Install dependencies
uv sync
uv pip install -e .

# Copy .env.sample to .env
cp .env.sample .env
