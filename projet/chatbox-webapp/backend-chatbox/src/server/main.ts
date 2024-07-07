import express from "express";
import { Server, Socket } from "socket.io";

// https://dev.to/novu/building-a-chat-app-with-socketio-and-react-2edj

// https://socket.io/get-started/chat/
const app = express();
const http = require("http");
const server = http.createServer(app);
const PORT = 3000;

const io = new Server(server, { cors: { origin: "*" } });

const cors = require("cors");

app.use(cors());

io.on("connection", (socket: Socket) => {
  socket.on("disconnect", () => {
    console.log("a user has disconnected");

  });
  console.log(`a user with id \"${socket.id}\" connected`);
  socket.on('test',(text)=>{
    console.log(`${socket.id}: ${text}`);
  })
});

app.get("/hello", (_, res) => {
  res.send("Hello Vite + TypeScript!");
});

server.listen(PORT, () =>
  console.log(`Server is listening on port ${PORT}...`)
);
