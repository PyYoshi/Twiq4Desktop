#!/bin/bash
export ENV_NAME=Twiq
export VIRTUALENV_PATH=$HOME/.virtualenvs/$ENV_NAME
source $VIRTUALENV_PATH/bin/activate
python app.py
