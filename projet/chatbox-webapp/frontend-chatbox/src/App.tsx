import './App.css'

import { Chatbox_container} from './component/Chatbox';
import { SocketContext,socket } from "./component/Socket";

function App() {

  return (
    <>
    <SocketContext.Provider value={socket}>

    <Chatbox_container/>

    </SocketContext.Provider>
    </>
  )
}

export default App
