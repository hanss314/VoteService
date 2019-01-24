import React from 'react';
import axios from 'axios';
import Responses from './responses';

class Control extends React.Component{
    constructor(props){
        super(props);
        this.state = {author: '', content: '', file: null};
        this.authorChange = this.authorChange.bind(this);
        this.contentChange = this.contentChange.bind(this);
        this.fileChange = this.fileChange.bind(this);
        this.handleSubmit = this.handleSubmit.bind(this);
        axios.get("/api/guilds/registered/"+this.props.gid).then((response) => {
            this.setState({guild: response.data});
        });
        this.responses = (<Responses gid={this.props.gid} />);
    }
    render(){
        const title = this.state.guild === undefined ? '' : this.state.guild.name;
        return (
            <div>
            <form onSubmit={this.handleSubmit} encType="multipart/form-data">
            <h2>{title}</h2>
            <label>
                Author:
                <input
                    type="text"
                    value={this.state.author}
                    onChange={this.authorChange}
                />
            </label>
            <br />
            <label>
                Content:
                <input
                    type="text"
                    value={this.state.content}
                    onChange={this.contentChange}
                />
            </label>
            <br />
            <label>
                File Upload:
                <input
                    type="file"
                    onChange={this.fileChange}
                />
            </label><br />
            <input type="submit" value="Submit" />
            </form>
            {this.responses}
            </div>

        );
    }
    authorChange(event) {
        this.setState({author: event.target.value});
    }
    contentChange(event) {
        this.setState({content: event.target.value});
    }
    fileChange(event) {

        this.setState({file: event.target.files[0]});
    }

    handleSubmit(event) {
        if (this.state.file === null) {
            axios.post('/api/'+this.props.gid+'/responses', {
                author: this.state.author,
                content: this.state.content
            });
        } else {
            let formData = new FormData();
            const file = new Blob([this.state.file], {type: this.state.file.type});
            formData.append('file', file, this.state.file.name);
            console.log(this.state.file);
            const config = {
                headers: { 'content-type': 'multipart/form-data' },
            };
            axios.post('/api/'+this.props.gid+'/responses/upload', formData, config);
        }
        this.setState({author: '', content: ''});
        this.responses.update();
        event.preventDefault();
    }
}

export default Control;