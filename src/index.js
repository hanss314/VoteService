import React from 'react';
import ReactDOM from 'react-dom';
import { BrowserRouter as Router, Route } from "react-router-dom";
import axios from 'axios';
import Guilds from './guilds';
import Control from './control';

function defaultError(err){
    if (err.response && err.response.status === 312) {
        axios.post('/oauth2/save', {location: window.location.href});
        window.location.replace(err.response.headers.location);
    }
    return Promise.reject(err);
}

axios.interceptors.response.use(null, defaultError);

const Home = () => (<h2>Home</h2>);

class App extends React.Component {
    render() {
        return (
            <Router><div>
                <h1>Welcome to the vote service!</h1>
                <Route exact path="/" component={Home} />
                <Route
                    exact path="/guilds"
                    render={(props) =>
                        <Guilds {...props} needsAuth={false} add={false}/>
                    }
                />
                <Route
                    path="/guilds/add"
                    render={(props) =>
                        <Guilds {...props} needsAuth={true} add={true}/>
                    }
                />
                <Route
                    path="/guild/:gid"
                    render={({match}) => <Control gid={match.params.gid} />}
                />
            </div></Router>
        );
    }
}




ReactDOM.render(<App />, document.getElementById('root'));
