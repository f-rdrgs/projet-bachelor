import {io} from "socket.io-client";
import {createContext} from "react";
io().connect()
export const socket = io(`:3000`, {
     transports: [ "polling" ]
})
export const SocketContext = createContext(socket);