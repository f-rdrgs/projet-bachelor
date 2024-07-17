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
    addMessage:(message:string, index ?:number)=>void,
}

interface ChatboxMessage {
    key_value:number
    type:string
}

interface ChatboxRadio extends ChatboxMessage {
    titles: string[],
    elements_id_array: string[][],
    texts_array:string[][],
    type:'radio',
    addMessage: (message:string, index?:number) =>void
}


interface ChatboxText extends ChatboxMessage{
    message:string,
    isBot:boolean,
    type:'text'
}

interface ChatboxMessageCont{
    chatList:ChatboxMessage[],
    addMessage: (message:string, index?:number) =>void
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
            <div key={key_value} className="text-left" dangerouslySetInnerHTML={{__html:message}} />
        ): (
            <div key={key_value} className="text-right" dangerouslySetInnerHTML={{__html:message}} />
       );
};


const Radio_container : FC<ChatboxRadio> = ({titles,elements_id_array,texts_array,key_value,addMessage}) => {
    
    const [radioChoices,setRadioChoices] = useState<{[name:string]:string}>({})
    const [radioIndex,setRadioIndex] = useState<number>(0)
    function addtoChoices(e:React.MouseEvent<HTMLInputElement>){
        const value = (e.target as HTMLInputElement).value;
        const target_name = (e.target as HTMLInputElement).name;
        setRadioChoices((prevChoices) => {
            return {...prevChoices,[target_name]:value}
        })
    }

    function submitRadio() {
        console.log("CHOICES: "+Object.keys(radioChoices).length)
        const lenChoices = Object.keys(radioChoices).length
        if(lenChoices> 0)
        {
            let newMessage :string = ""
            for(let key in radioChoices){
                newMessage += radioChoices[key]+" "

            }
            console.log(newMessage)
            setRadioIndex((prevIndex) => {
                const len = prevIndex+ lenChoices
                return len
            })
            setRadioChoices({})
            addMessage(newMessage.trim())
            
        }
    }

    useEffect(() => {
        console.log("RADIO CHOICES: ", radioChoices);
        console.log("RADIO INDEX: "+radioIndex)
    }, [radioChoices,radioIndex]);

    const radio_elements = titles.map((title,index) => {
        return <Radio_element addToChoices={addtoChoices} radio_id={key_value + index} key={index+key_value} elements_id={elements_id_array[index]} title={title} texts={texts_array[index]}/>
    })
    return (
        <>
            {radio_elements}
            <button onClick={submitRadio} className="radio-submit" type="submit" name="send-radio">Confirmer</button>
        </>
    )
}

const Chatbox_message_container: FC<ChatboxMessageCont> = ({chatList,addMessage}) => {

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
                return <Radio_container addMessage={addMessage} elements_id_array={message_radio.elements_id_array} texts_array={message_radio.texts_array} titles={message_radio.titles}  type="radio" key_value={message.key_value} key={index}/>
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

    const [radioIndex,setRadioIndex] = useState(0)

    const [user_id] = useState(uuidv4())


    // \[(.*?)\]
    // [OPTION][0][TITLE][Avec ou sans couverts ?][OPTIONS][(Avec,1)(Sans,2)(Je sais pas,3)][OPTION][1][TITLE][Avec ou sans chaussures ?][OPTIONS][(Avec,1)(Sans,2)(Je sais pas,3)]

    // [OPTION][0][TITLE][option1][OPTIONS][(Un choix 1,1)(Un choix 2,2)(Un choix 3,3)][OPTION][1][TITLE][option2][OPTIONS][(Un choix 1,4)(Un choix 2,5)(Un choix 3,6)]
    function process_message(newMessage:string, index ?: number) : ChatboxMessage{

        const parse_array = (text:string) =>  {
            const match = text.match(/\[([^\]]*)\]/);  
            return match ? match : null;
        }


        if(newMessage.startsWith("[OPTION]")) {
            const options = newMessage.split('[OPTION]').filter((message,index) => message.length>0)
            // Parser le message radio bouton et créer les éléments nécessaires, possiblement changer le retour de fonction en array de ChatboxMessages vu qu'il peut y avoir une multitude de radio boutons
            // const ids = options[]

            let titles : string[] = [];
            let components_id : string[][] = [];
            let texts_array: string[][] = [];
            
            const regex_title = /\[TITLE\]\[(.*?)\]/;
            const regex_index = /^\[(.*?)\]/;
            const regex_options = /\[OPTIONS]\[(.*?)\]/;
            const regex_single_opt = /\((.*?)\)/g;

            // const regex_single_opt_elems = /(.*?),(.*?)/g;
            options.forEach((option,index) => {
                let radio_index = 0;
                // console.log("OPTION: "+option)
                const match_title = option.match(regex_title);
                const match_index = option.match(regex_index);
                const match_options = option.match(regex_options);
                if(match_index !== null)
                    {
                        radio_index = +match_index[1]
                        // console.log("INDEX: "+radio_index)
                        components_id[radio_index] = []
                        texts_array[radio_index] = []
                        if(match_title !== null)
                        {
                            // console.log(match_title[1]);
                            titles.push(match_title[1]);
                        }
                            
                    }
                    
                if(match_options !== null)
                {

                    // texts_array[radioIndex].push()
                    const opts = match_options[1]
                    // console.log("OPTIONS: " +match_options[1])
                    let matched_opts = opts.match(regex_single_opt);
                    
                    if (matched_opts !== null)
                    {
                        const new_matched_opts = matched_opts.map((elem,_) => { return elem.replace('(',"").replace(')',"")}).map((elem,_) => elem.split(','))
                        // console.log(new_matched_opts)
                        new_matched_opts.forEach((elems,_) => {
                            // console.log("ELEMS: "+elems)
                            components_id[radio_index] = [...components_id[radio_index],elems[1]]
                            texts_array[radio_index] = [...texts_array[radio_index],elems[0]]
                        })
                    }
                }

                
            })
            // console.log(options.length)
            setRadioIndex((prevIndex)=> prevIndex+options.length);

            // console.log(titles)
            // console.log(components_id)
            // console.log(texts_array)

            

                
            
            
            const radio_message : ChatboxRadio = {elements_id_array:components_id, texts_array:texts_array,titles:titles,key_value:radioIndex,type:'radio',addMessage}
            return radio_message;
        } else{
            let processed_message = newMessage
            processed_message = processed_message.replace(/\[br\]/g,"<br>")
            processed_message = processed_message.replace(/\[tab\]/g,"&ensp;")
            const text_message : ChatboxText= {message:processed_message,isBot:true,key_value:(index != undefined ? index : 0),type:'text'}
            return text_message;
        }
    }

    function addMessage(newMessage:string, index ?:number) {
        newMessage = newMessage.trim()
        if(newMessage.length>0){
            const newChatMessage :ChatboxText = {message:newMessage,isBot:false,key_value:(index != undefined ? index : 2),type:'text'}
            // Utilisation de la forme fonctionnelle de setState parce que sinon les messages envoyés par d'autres appels de setState seront écrasés
            setMessages(prevMessages => [...prevMessages, newChatMessage]);
            sendMessageToBot(newMessage,user_id);
        }
    }

    useEffect(()=>{
        console.log("Radio index: "+radioIndex)
        socket.on('chat', (bot_messages:string[])=> {
            const messagesBotTreated : ChatboxMessage[]= bot_messages.map((message,index)=>{
                return  process_message(message,index);
            })
            // Utilisation de la forme fonctionnelle de setState parce que sinon les messages envoyés par d'autres appels de setState seront écrasés
            setMessages(prevMessages => [...prevMessages, ...messagesBotTreated])
        })

        // retrait du listener pour s'assurer que le on chat n'est pas appelé plusieurs fois
        return () => {
            socket.off('chat');
        };
    },[radioIndex])

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
            <Chatbox_message_container addMessage={addMessage} chatList={messages}/>
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
        addMessage(message);
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
            <button className="chat-send" type="button" value="Envoyer"  onClick={() => addNewMessage()}>
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