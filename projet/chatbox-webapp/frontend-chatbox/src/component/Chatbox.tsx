import { FC, useContext, useEffect, useRef, useState } from "react";

import "../styles/chatbox.css";
import { IoSendSharp } from "react-icons/io5";


import { io, Socket } from "socket.io-client";
import {v4 as uuidv4} from "uuid";
import { SocketContext } from "./Socket";



interface ChatboxProps {
    header:string;
}
 

interface ChatboxContainer {

}
interface ChatboxTextboxCont{
    addMessage:(message:string,isBot:boolean)=>void,
}
interface ChatboxText {
    message:string,
    isBot:boolean,
    key_value:number
}

interface ChatboxMessageCont{
    chatList:ChatboxText[]
}
// https://felixgerschau.com/react-typescript-components/

// https://dev.to/wpreble1/typescript-with-react-functional-components-4c69

// https://www.youtube.com/watch?v=LD7q0ZgvDs8

const Chatbox_header: FC<ChatboxProps> = ({header}) => {
    return ( 
        <>
        <h1 className="header">{header}</h1>
        </>
     );
}
 
const Chatbox_text:FC<ChatboxText> = ({message,isBot,key_value}) => {
       return isBot ?  (
            <div key={key_value} className="text-left">{message}</div>
        ): (
            <div key={key_value} className="text-right">{message}</div>
       );
};


const Chatbox_message_container: FC<ChatboxMessageCont> = ({chatList}) => {

    const bottomChatRef = useRef<HTMLDivElement>(null);

    // https://www.youtube.com/watch?v=yaIytT_Y0DA
    // Lorsque chatList change, scroll en bas de la chatbox
    useEffect(() => {
        if(bottomChatRef.current)
            bottomChatRef.current.scrollIntoView();
    },[chatList])

    function CreateChat() : JSX.Element[]{
        return (
            chatList.map((message,index)=>{
                return <Chatbox_text key={index} key_value={index} isBot={message.isBot} message={message.message}/>
            })
        )
    }

    return (
        <>
        <div className="message-container">
            <CreateChat/>
            <div ref={bottomChatRef}></div>
        </div>
        </>
    )
}


const Chatbox_container: FC<ChatboxContainer> = ({}) => {

    // Utilisation de contexte afin d'avoir un socket global unique
    const [socket] = useState( useContext(SocketContext))

    const [messages,setMessages] = useState<ChatboxText[]>([])

    const [user_id] = useState(uuidv4())


    function addMessage(newMessage:string) {
        newMessage = newMessage.trim()
        if(newMessage.length>0){
            const newChatMessage :ChatboxText = {message:newMessage,isBot:false,key_value:0};
            // Utilisation de la forme fonctionnelle de setState parce que sinon les messages envoyés par d'autres appels de setState seront écrasés
            setMessages(prevMessages => [...prevMessages, newChatMessage]);
            sendMessageToBot(newMessage,user_id);
        }
    }

    useEffect(()=>{

        socket.on('chat', (bot_messages:string[])=> {
            const messagesBotTreated : ChatboxText[]= bot_messages.map((message,index)=>{
                return {message:message,isBot:true,key_value:index};
            })
            // Utilisation de la forme fonctionnelle de setState parce que sinon les messages envoyés par d'autres appels de setState seront écrasés
            setMessages(prevMessages => [...prevMessages, ...messagesBotTreated])
        })

        // retrait du listener pour s'assurer que le on chat n'est pas appelé plusieurs fois
        return () => {
            socket.off('chat');
        };
    },[])

    function sendMessageToBot(message:string,uuid:string){
        socket.emit("chat", message,uuid)
    }

    return (
        <>
        <div className="container">
            <Chatbox_header header="Réservation"/>
            <Chatbox_message_container chatList={messages}/>
            <Chatbox_textbox_cont addMessage={addMessage}/>
        </div>
        </>
    )
}

const Chatbox_textbox_cont:FC<ChatboxTextboxCont>= ({addMessage,})=>{

    const [message,setMessage] = useState("")
    function addNewMessage() {
        addMessage(message,false);
        setMessage("");
    }

    function handleEnterKey(event: React.KeyboardEvent<HTMLTextAreaElement>){
        if (event.key === 'Enter' && !event.shiftKey) {
            event.preventDefault();
            addNewMessage();
        }
    }

    return (
        <div className="textbox-input">
            <textarea placeholder="Entrez votre message ici..."
            value={message}
            onChange={e => setMessage(e.target.value)}
            onKeyDown={handleEnterKey}
            ></textarea>
            <button type="button" value="Envoyer"  onClick={() => addNewMessage()}>
                <IoSendSharp className="react-send-icon" size={"3vh"} /></button>
        </div>
    )
}

export {
    Chatbox_header as Chatbox,
    Chatbox_container,
    Chatbox_text,
    Chatbox_textbox_cont
};