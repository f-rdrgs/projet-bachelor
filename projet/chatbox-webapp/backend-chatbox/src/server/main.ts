import express from "express";
import { Server, Socket } from "socket.io";
import cors from "cors";
require('dotenv').config()
// https://dev.to/novu/building-a-chat-app-with-socketio-and-react-2edj

// https://socket.io/get-started/chat/
const app = express();
const http = require("http");
const server = http.createServer(app);
const PORT = process.env.PORT;

const io =  new Server(server, {
  cors: {
    origin: "*",
    methods: ["GET", "POST"],
    allowedHeaders: []
  },
  allowEIO3: true 
});


app.use(cors({origin:["*"]}));

async function query_rasa(message:string,uuid:string) : Promise<string[]> {

  try {
    const response = await fetch(`${process.env.API_IP}/communicate-rasa`,{
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
        const processed_messages = await Promise.all(
          content.map(async (content) => {
            if (content["text"].startsWith("[FILE]")) {
              const response = await fetch(
                `${process.env.API_IP}/get-ics-file/${content["text"].replace("[FILE]", "")}`,
                {
                  method: "GET",
                }
              );
              console.log(content)
              const resp_json: { [file_base64: string]: string } = await response.json()
              const base64Str = resp_json["file_base64"].slice(8,-1)
              // const decodedStr = Buffer.from(base64Str,'base64').toString('utf-8')
              return "[FILE]"+base64Str;
            } else {
              return content["text"];
            }
          })
        );
        return processed_messages;
      }else return [];
      
    }
    else return [];
  } catch (error) {
    console.log(error)
    return ["Une erreur s'est produite, veuillez ressayer ultérieurement."]
  }
  
}

io.on("connection", (socket: Socket) => {
  socket.on("disconnect", () => {
    console.log(`a user with id \"${socket.id}\" has disconnected`);
  });
  console.log(`a user with id \"${socket.id}\" connected`);
  socket.on('chat',async (message:string,uuid:string) => {
    const rasa_messages :string[]  = await query_rasa(message,uuid);
    // const rasa_messages: string[] = await get_file()
    // console.log(rasa_messages)
    // const rasa_messages : string[] = ["[OPTION][0][TITLE][Avec ou sans couverts ?][OPTIONS][(Avec,1)(Sans,2)(Je sais pas,3)][OPTION][1][TITLE][Avec ou sans chaussures ?][OPTIONS][(Avec,1)(Sans,2)(Je sais pas,3)]"];
    socket.emit("chat", rasa_messages);
    console.log(uuid + ": "+ message)
  })
});

server.listen(PORT, () =>
  console.log(`Server is listening on ${server.address().address}:${PORT}...`)
);
