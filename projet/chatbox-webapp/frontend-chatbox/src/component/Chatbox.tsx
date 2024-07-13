import { FC, useContext, useEffect, useRef, useState } from "react";

import "../styles/chatbox.css";
import { IoSendSharp } from "react-icons/io5";


import { io, Socket } from "socket.io-client";
import {v4 as uuidv4} from "uuid";
import { SocketContext } from "./Socket";
import { Component_Radio, Radio_element } from "./Radio_choix";
import "../assets/iphone-x-saying-hello-dribbble-css-only/src/style.css"


interface ChatboxProps {
    header:string;
}
 

interface ChatboxContainer {

}
interface ChatboxTextboxCont{
    addMessage:(message:string,isBot:boolean)=>void,
}

interface ChatboxMessage {
    key_value:number
    type:string
}

interface ChatboxRadio extends ChatboxMessage {
    radio:Component_Radio,
    type:'radio'
}


interface ChatboxText extends ChatboxMessage{
    message:string,
    isBot:boolean,
    type:'text'
}

interface ChatboxMessageCont{
    chatList:ChatboxMessage[]
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


const Radio_container : FC<ChatboxRadio> = ({radio,key_value}) => {
    const radio_elements = radio.titles.map((title,index) => {
        return <Radio_element elements_id={radio.elements_id_array[index]} title={title} texts={radio.texts_array[index]}/>
    })
    return (
        <>
            {radio_elements}
        </>
    )
}

const Chatbox_message_container: FC<ChatboxMessageCont> = ({chatList}) => {

    const bottomChatRef = useRef<HTMLDivElement>(null);

    // https://www.youtube.com/watch?v=yaIytT_Y0DA
    // Lorsque chatList change, scroll en bas de la chatbox
    useEffect(() => {
        if(bottomChatRef.current)
            bottomChatRef.current.scrollIntoView();
    },[chatList])

    function CreateChat() : JSX.Element[]{

        const return_element = (message:ChatboxMessage,index:number) => {
            if(message.type === 'text'){
                const message_text :ChatboxText = (message as ChatboxText);
                return <Chatbox_text key={index} key_value={index} isBot={message_text.isBot} message={message_text.message} type="text"/>
            } else if (message.type === 'radio'){
                const message_radio :ChatboxRadio = (message as ChatboxRadio);
                return <Radio_container radio={message_radio.radio} type="radio" key_value={message.key_value} key={index}/>
            }else{
                return <div/>
            }
        }

        const elem_list: JSX.Element[] = chatList.map((message,index)=>{
            return return_element(message,index)               
            })

        return (
            
            elem_list
   
        )
    }

    return (
        <>
        <div className="message-container">
            {/* <Radio_container/> */}
            <CreateChat/>
            <div ref={bottomChatRef}></div>
        </div>
        </>
    )
}


const Chatbox_container: FC<ChatboxContainer> = ({}) => {

    // Utilisation de contexte afin d'avoir un socket global unique
    const [socket] = useState( useContext(SocketContext))

    const [messages,setMessages] = useState<ChatboxMessage[]>([])

    const [user_id] = useState(uuidv4())


    function addMessage(newMessage:string) {
        newMessage = newMessage.trim()
        if(newMessage.length>0){
            const newChatMessage :ChatboxText = {message:newMessage,isBot:false,key_value:0,type:'text'};
            // Utilisation de la forme fonctionnelle de setState parce que sinon les messages envoyés par d'autres appels de setState seront écrasés
            setMessages(prevMessages => [...prevMessages, newChatMessage]);
            sendMessageToBot(newMessage,user_id);
        }
    }

    useEffect(()=>{

        socket.on('chat', (bot_messages:string[])=> {
            const messagesBotTreated : ChatboxMessage[]= bot_messages.map((message,index)=>{
                return {message:message,isBot:true,key_value:index,type:'text'};
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

    // https://freefrontend.com/iphones-in-css/
    // https://freefrontend.com/assets/zip/iphones-in-css/iphone-x-saying-hello-dribbble-css-only.zip
    return (
        <>
        <div className="iphonex">
			<div className="front">
				<div className="screen">
					{/* <!-- <div className="screen__view"> --> */}
						{/* <!-- Here --> */}
                        <div className="container">
            <Chatbox_header header="Réservation"/>
            <Chatbox_message_container chatList={messages}/>
            <Chatbox_textbox_cont addMessage={addMessage}/>
        </div>
					{/* <!-- </div> --> */}
					<div className="screen__front">
						<div className="screen__front-speaker"></div>
						<div className="screen__front-camera"></div>
					</div>
				</div>
				<div className="front__line"></div>
				<div className="front__line front__line-second"></div>
			</div>
			<div className="phoneButtons phoneButtons-right"></div>
			<div className="phoneButtons phoneButtons-left"></div>
			<div className="phoneButtons phoneButtons-left2"></div>
			<div className="phoneButtons phoneButtons-left3"></div>
			<div className="back"></div>
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