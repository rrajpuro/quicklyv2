curl -s https://deb.nodesource.com/setup_16.x | sudo bash
sudo apt install nodejs -y
node -v

cd cdn && npm install

cdn_port=3001
if $1:
then
cdn_port = $1
fi

webapp_port=3001
if $2:
then
webapp_port = $2
fi

webapp_IP='127.0.0.1'
if $3:
then
webapp_IP = $3
fi

node app.js $cdn_port $webapp_port $webapp_IP #3001
