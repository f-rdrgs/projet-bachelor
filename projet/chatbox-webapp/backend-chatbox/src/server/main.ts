import express from "express";

// https://dev.to/novu/building-a-chat-app-with-socketio-and-react-2edj

const app = express();
const PORT = 3000;

const cors = require('cors');

app.use(cors());

app.get("/hello", (_, res) => {
  res.send("Hello Vite + TypeScript!");
});

app.listen(PORT,"localhost",() => 
  console.log(`Server is listening on port ${PORT}...`)
)
