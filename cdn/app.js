const express = require('express');
const NodeCache = require('node-cache');
const axios = require('axios');
const app = express();
const cache = new NodeCache();

const args = process.argv.slice(2);

const cdn_port = args[0] || 3001
const webapp_port = args[1] || 3001
const webapp_IP=  args[2] || 'localhost'

app.use('/', async (req, res) => {
    // console.log(req)

  let key=req.method+req.url;
  const cachedResponse = cache.get(key);
  if (cachedResponse) {
    console.log('Cache hit for: ',key);
    res.send(cachedResponse);
  } else {
    console.log('Cache miss for: ',key);
    try {
    console.log("REQUEST URL: ",req.url)
    // TODO: update localhost to the IP of webapp server
      const response = await axios.get(`http://${webapp_IP}:${webapp_port}`+req.url); 
      cache.set(key, response.data);
      res.send(response.data);
    } catch (error) {
      console.error(error);
      res.status(500).send('Internal server error');
    }
  }
});

// listening on port 3001
app.listen(cdn_port, () => {
  console.log('CDN Server is listening on port 3001...');
});
