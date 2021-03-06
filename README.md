[![Build Status](https://api.travis-ci.com/render1980/grassroot-assistant.svg?branch=main)](https://travis-ci.com/render1980/grassroot-assistant)
[![Version](https://img.shields.io/badge/version-1.0-green.svg)](https://img.shields.io/badge/version-1.0-green.svg)
[![Coverage Status](https://coveralls.io/repos/github/render1980/grassroot-assistant/badge.svg?branch=main)](https://coveralls.io/github/render1980/grassroot-assistant?branch=main)

# grassroot-assistant

Bot which helps to communicate with others nearby over Telegram.

[How it works](https://render1980.github.io/projects/grassrootassistant.html)

## Requirements

Preinstalled:

- pyenv
- docker-compose
- pip

Run:

```
pyenv install 3.7.5 && pyenv global 3.7.5
docker-compose up -d --build --force-recreate redis
pip install -r requirements.txt
```

## Start

```
python main.py
```

## Build package

```
python setup.py build
python setup.py sdist
```

## Telegram Bot Commands

You can find commands [here](https://github.com/render1980/grassroot-assistant/wiki/Bot-Commands)

## Environment Variables

`BOT_TOKEN` - telegram bot token
