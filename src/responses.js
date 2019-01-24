import React from 'react';
import axios from 'axios';

class Response extends React.Component{
    constructor(props){
        super(props);
        this.state = {editing: false, author: props.author, content: props.content};
    }
    render(){
        if (!this.state.editing) {
            return (<div>
                <b>{this.state.author}</b> - {this.state.content}
                <button onClick={()=>this.setEdit()}>Edit</button>
                <button onClick={()=>this.onDelete()}>Delete</button>
            </div>);
        }
        return(<div>
            <form onSubmit={(e)=>this.handleSubmit(e)} encType="multipart/form-data">
            <input
                type="text"
                value={this.state.author}
                onChange={(e)=>this.authorChange(e)}
            />
            <input
                type="text"
                value={this.state.content}
                onChange={(e)=>this.contentChange(e)}
            />
            <input type="submit" value="Submit" />
            </form>
            </div>
        );

    }
    onDelete(){
        axios.delete(
            '/api/'+this.props.gid+'/responses/'+this.props.ind
        );
        this.props.onDelete(this.props.ind);
    }
    setEdit(){
        this.setState({editing: true});
    }
    authorChange(event) {
        this.setState({author: event.target.value});
    }
    contentChange(event) {
        this.setState({content: event.target.value});
    }
    handleSubmit(event) {
        axios.patch('/api/'+this.props.gid+'/responses/'+this.props.ind, {
            author: this.state.author,
            content: this.state.content
        });
        this.setState({editing: false});
        event.preventDefault();
    }

}

class Responses extends React.Component{
    constructor(props){
        super(props);
        this.state = {responses: []};
        this.update()
    }
    render(){
        const responses = this.state.responses.map((r) => {
            return (<li key={r.ind}><Response
                gid={this.props.gid}
                ind={r.ind}
                author={r.author}
                content={r.content}
                onDelete={(i)=>this.onDelete(i)}
            /></li>);
        });
        return (
            <div><ol>
                {responses}
            </ol></div>
        );
    }
    onDelete(i){
        const newResponses = this.state.responses.filter((response) => response.ind !== i);
        this.setState({responses: newResponses});
    }
    update(){
        axios.get("/api/"+this.props.gid+"/responses").then((response) => {
            this.setState({responses: response.data});
        });
    }
}


export default Responses;