import express from "express";
import { Server, Socket } from "socket.io";

// https://dev.to/novu/building-a-chat-app-with-socketio-and-react-2edj

// https://socket.io/get-started/chat/
const app = express();
const http = require("http");
const server = http.createServer(app);
const PORT = 3000;

const io =  new Server(server, {
  cors: {
    origin: ["http://localhost:4000","http://172.17.147.194:4000/","*"]
  }
});

const cors = require("cors");

app.use(cors({origin:["http://localhost:4000","http://172.17.147.194:4000/","*"]}));

async function query_rasa(message:string,uuid:string) : Promise<string[]> {

  
  const response = await fetch("http://localhost:5500/communicate-rasa",{
    body: JSON.stringify({
      "message":message,
      "sender":uuid
    }),
    method: 'POST',
    headers: {
      'content-type': 'application/json'
    }
  })
  if(response.ok){
    const content : { [x: string]: string; }[] = await response.json();
    if(content.length> 0){
      return content.map((content,_)=> {
        return content["text"];
      })
    }else return [];
    
  }
  else return [];
}

io.on("connection", (socket: Socket) => {
  socket.on("disconnect", () => {
    console.log(`a user with id \"${socket.id}\" has disconnected`);
  });
  console.log(`a user with id \"${socket.id}\" connected`);
  socket.on('chat',async (message:string,uuid:string) => {
    socket.emit("chat",await query_rasa(message,uuid));
    console.log(uuid + ": "+ message)
  })
});

server.listen(PORT, () =>
  console.log(`Server is listening on port ${PORT}...`)
);
