import { FC } from "react";
import "../assets/radio-button/src/style.css"

interface Component_Radio {
    titles: string[],
    elements_id_array: string[][],
    texts_array:string[][],
    addToChoices:(e:React.MouseEvent<HTMLInputElement, MouseEvent>)=>void
}

interface Element_Radio {
    title:string,
    elements_id:string[],
    texts:string[],
    radio_id:number,
    addToChoices:(e:React.MouseEvent<HTMLInputElement, MouseEvent>)=>void
}

interface Radio_button {
    element_id: string,
    text:string,
    radio_id:number,
    addToChoices:(e:React.MouseEvent<HTMLInputElement, MouseEvent>)=>void
}
// https://freefrontend.com/css-radio-buttons/
// https://freefrontend.com/assets/zip/css-radio-buttons/2023-radio-button.zip


const Radio_element : FC<Element_Radio> = ({title,elements_id,texts,radio_id,addToChoices}) => {
    const radio_buttons =  texts.map((txt,index) => {
        return <Radio_button addToChoices={ addToChoices} radio_id={radio_id} key={index} element_id={elements_id[index]} text={txt} />
    })

    return (
        <>
        <div className="radio_container">
            <div className="radio-list">
                <p>{title}</p>
                {radio_buttons}
            </div>
            
        </div>
        </>
    )
}

const Radio_button : FC<Radio_button> = ({element_id,text,radio_id,addToChoices}) => {
    const radioName = "radio"+radio_id
    return (
        <div className="radio-item"><input onClick={(e)=>addToChoices(e)} name={radioName} value={element_id} id={element_id+radio_id} type="radio"/><label  htmlFor={element_id+radio_id}>{text}</label></div>
    )
}


export {Radio_element};
export type {
    Component_Radio
}