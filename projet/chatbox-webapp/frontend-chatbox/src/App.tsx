import { BrowserRouter, Route, Routes } from 'react-router-dom';
import './App.css'

import { Chatbox_container} from './component/Chatbox';
import { SocketContext,socket } from "./component/Socket";
import { HomeContainer } from './component/Home';

function App() {

  return (
    <>
    <SocketContext.Provider value={socket}>
    <BrowserRouter>
    <Routes>
      <Route path='/bot' Component={Chatbox_container}/>
      <Route path='/' Component={HomeContainer}/>
    </Routes>
    </BrowserRouter>
    </SocketContext.Provider>
    </>
  )
}
/* <Chatbox_container/> */

export default App
