import { FC, useContext, useEffect, useRef, useState } from "react";
import "../assets/radio-button/dist/style.css"
interface Container_Radio{

}
// https://freefrontend.com/css-radio-buttons/
// https://freefrontend.com/assets/zip/css-radio-buttons/2023-radio-button.zip
const Radio_container : FC<Container_Radio> = () => {
    return (
        <div className="radio_container">
            
        	<div className="radio-list">
                <p>Which Social Media you Often use?</p>
                <div className="radio-item"><input name="radio" id="radio1" type="radio"/><label htmlFor="radio1">INSTAGRAM</label></div>
                <div className="radio-item"><input name="radio" id="radio2" type="radio"/><label htmlFor="radio2">Un très long message qui message bien comme il se devrait l'être</label></div>
                <div className="radio-item"><input name="radio" id="radio3" type="radio"/><label htmlFor="radio3">LINKEDIN</label></div>
	        </div>

        </div>
    )
}

export {Radio_container};