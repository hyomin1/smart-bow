#!/bin/bash
cd /home/gwandugjung/workspace/smart-bow/fastapi-ai

export VENV_PATH="/home/gwandugjung/workspace/smart-bow/fastapi-ai/venv"

source $VENV_PATH/bin/activate
export PATH=$VENV_PATH/bin:$PATH

exec uvicorn app.main:app --host 0.0.0.0 --port 8000

