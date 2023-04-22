curl -s https://deb.nodesource.com/setup_16.x | sudo bash
sudo apt install nodejs -y
node -v

cd webapp && npm install

port=3000
if $1:
then
port = $1
fi
# IP='127.0.0.1'
# if $2:
# then
# IP = $2
# fi

node app.js $port # $IP
