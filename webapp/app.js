const express = require('express')
const app = express()
const args = process.argv.slice(2);
const port = args[0] || 3000

app.get('/', (req, res) => {
  res.send('Hello World!')
})

app.get('/page1', (req, res) => {
    res.sendFile('./file1.html', {root: __dirname })
  })

  app.get('/page2', (req, res) => {
    res.sendFile('./file2.html', {root: __dirname })
  })

  app.get('/page3', (req, res) => {
    res.sendFile('./file3.html', {root: __dirname })
  })

  // listening on port 3000
app.listen(port, () => {
  console.log(`WEBAPP Example app listening on port ${port}`)
})