import React from 'react';
import axios from 'axios';

class Response extends React.Component{
    constructor(props){
        super(props);
    }
    render(){
        return (<div>
            <b>{this.props.author}</b> - {this.props.content}
        </div>);
    }

}

class Responses extends React.Component{
    constructor(props){
        super(props);
        this.state = {responses: []};
        axios.get("/api/"+this.props.gid+"/responses").then((response) => {
            this.setState({responses: response.data});
        });
    }
    render(){
        const responses = this.state.responses.map((response) => (
            <Response
                gid={this.props.gid}
                ind={response.ind}
                author={response.author}
                content={response.content}
            />
        ));
        return (
            <div>
                {responses}
            </div>
        );
    }
}

export default Responses;