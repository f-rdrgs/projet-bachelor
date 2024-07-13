import { FC } from "react";
import "../assets/radio-button/src/style.css"

interface Component_Radio {
    titles: string[],
    elements_id_array: string[][],
    texts_array:string[][]
}

interface Element_Radio {
    title:string,
    elements_id:string[],
    texts:string[]
}

interface Radio_button {
    element_id: string,
    text:string
}
// https://freefrontend.com/css-radio-buttons/
// https://freefrontend.com/assets/zip/css-radio-buttons/2023-radio-button.zip


const Radio_element : FC<Element_Radio> = ({title,elements_id,texts}) => {
    const radio_buttons =  texts.map((txt,index) => {
        return <Radio_button  key={index} element_id={elements_id[index]} text={txt} />
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

const Radio_button : FC<Radio_button> = ({element_id,text}) => {
    return (
        <div className="radio-item"><input name="radio" id={element_id} type="radio"/><label htmlFor={element_id}>{text}</label></div>
    )
}


export {Radio_element};
export type {
    Component_Radio
}