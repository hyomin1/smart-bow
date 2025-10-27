#!/bin/bash
cd /home/gwandugjung/workspace/smart-bow/frontend

export NVM_DIR="/home/gwandugjung/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"

export PATH="$NVM_DIR/versions/node/v22.21.0/bin:$PATH"

npm run build
exec npx serve -s dist -l 3000

