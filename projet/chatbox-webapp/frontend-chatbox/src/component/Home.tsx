import { FC } from "react"
import { Link } from "react-router-dom"

interface HomePage {

}

const HomeContainer: FC<HomePage> = ({}) => {
    return <>
    <h1>Page home</h1>
    <Link to='/bot'>Vers Bot</Link>
    </>
}

export {
    HomeContainer
}