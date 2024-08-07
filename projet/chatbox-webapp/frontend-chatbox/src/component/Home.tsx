import { FC } from "react";
import { Link } from "react-router-dom";
import "../styles/home.css";
import qr_telegram from "../assets/qr_telegram.png";
interface HomePage {}

const HomeContainer: FC<HomePage> = ({}) => {
  return (
    <>
      <div className="HomeContainer">
        <h1>Page d'accueil</h1>
        <Link to="/bot">
          <h2>Vers Bot Web</h2>
        </Link>
        <div>
          <h2>Vers bot Telegram (QR Code cliquable)</h2>
          <a href="https://t.me/WiREV_bot">
            <img src={qr_telegram}></img>
          </a>
        </div>
      </div>
    </>
  );
};

export { HomeContainer };
