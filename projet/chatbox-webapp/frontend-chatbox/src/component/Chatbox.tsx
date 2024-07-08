import { FC } from "react";

import "../styles/chatbox.css";
import { IoSendSharp } from "react-icons/io5";

interface ChatboxProps {
    header:string;
}
 

interface ChatboxContainer {

}
interface ChatboxTextboxCont{

}
interface ChatboxText {
    message:string
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
 
const Chatbox_text_right:FC<ChatboxText> = ({message})=> {
    return (
        <>
            <div className="text-right">{message}</div>
        </>
    )
}

const Chatbox_text_left:FC<ChatboxText> = ({message})=> {
    return (
        <>
            <div className="text-left">{message}</div>
        </>
    )
}

const Chatbox_message_container: FC = () => {
    return (
        <>
        <div className="message-container">
            <Chatbox_text_right message="Bonjour"/>
            <Chatbox_text_right message="Je voudrais réserver"/>
            <Chatbox_text_left message="Un terrain de basket"/>
            <Chatbox_text_right message="Un terrain de basket"/>
            <Chatbox_text_right message="Un terrain de basket"/>
            <Chatbox_text_right message="Un terrain de basket"/>
            <Chatbox_text_right message="Un terrain de basket"/>
            <Chatbox_text_left message="Un terrain de basket"/>
            <Chatbox_text_right message="Un terrain de basket"/>
            <Chatbox_text_right message="Un terrain de basket"/>
            <Chatbox_text_left message="Un terrain de basket"/>
            <Chatbox_text_right message="Un terrain de basket"/>
            <Chatbox_text_left message="Un terrain de basket"/>
            <Chatbox_text_left message="Un terrain de basket"/>
            <Chatbox_text_right message="Un terrain de basket"/>
            <Chatbox_text_right message="Un terrain de basket"/>
            <Chatbox_text_right message="Un terrain de basket"/>
            <Chatbox_text_right message="Un terrain de basket"/>
            <Chatbox_text_right message="Un terrain de basket"/>
        </div>
        </>
    )
}

const Chatbox_container: FC<ChatboxContainer> = ({}) => {
    return (
        <>
        <div className="container">
            <Chatbox_header header="Réservation"/>
            <Chatbox_message_container/>
            <Chatbox_textbox_cont/>
        </div>
        </>
    )
}

const Chatbox_textbox_cont:FC<ChatboxTextboxCont>= ({})=>{
    return (
        <div className="textbox-input">
            <textarea placeholder="Entrez votre message ici..."></textarea>
            <button type="submit" value="Envoyer"><IoSendSharp className="react-send-icon" size={"3vh"} autoReverse/></button>
        </div>
    )
}

export {
    Chatbox_header as Chatbox,
    Chatbox_container,
    Chatbox_text_right,
    Chatbox_text_left,
    Chatbox_textbox_cont
};