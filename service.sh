#!/bin/bash
export HOME=/home/pi
export PATH=$HOME/.pyenv/bin:$PATH
export PYENV_VIRTUALENV_DISABLE_PROMPT=1
eval "$(pyenv init -)"
eval "$(pyenv virtualenv-init -)"
pyenv activate py38
exec python /home/pi/fjerkroa/discord_bot.py /var/www/html/kooking.data /home/pi/fjerkroa
