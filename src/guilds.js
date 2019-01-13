import React from 'react';
import axios from 'axios';
import { Link } from 'react-router-dom';

class GuildEntry extends React.Component {
    constructor(props){
        super(props);
        this.makeReq = this.makeReq.bind(this);

    }

    render() {
        if (this.props.add) {
            return (
                <div onClick={this.makeReq}>
                    {this.props.name}
                </div>
            );
        } else {
            return (<Link to={"/guild/"+this.props.id}>{this.props.name}</Link>);
        }
    }
    makeReq(){
        console.log(this.props.id);
        axios.put("/api/"+this.props.id+"/");
    }
}

class Guilds extends React.Component {
    constructor(props){
        super(props);
        this.state = {guilds: []};
        axios.get("/api/guilds/").then((response) => {
            this.setState({guilds: response.data});
        });

    }
    render() {
        const guilds = this.state.guilds.filter((guild) =>
            !this.props.needsAuth || (guild.permissions & 32) === 32
        ).map((guild) =>
            (<li key={guild.id}><GuildEntry {...guild} add={this.props.add}/></li>)
        );

        return (
            <div>
                <ol>{guilds}</ol>
            </div>
        );
    }
}

export default Guilds;
