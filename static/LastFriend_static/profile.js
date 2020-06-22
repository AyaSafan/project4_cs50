document.addEventListener('DOMContentLoaded', () => {

    //current profile username
    let session_username = document.querySelector('#session_username').innerHTML;
     // Connect to websocket
    var socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port);

    // Emit new post from profile
    socket.on('connect', () => {
        document.querySelector('#postform').onsubmit = () => {
            const title = document.querySelector('#title').value;
            const post = document.querySelector('#post').value;
            socket.emit('new post', {'title': title , 'post': post});

            document.querySelector('#title').value = '';
            document.querySelector('#post').value = '';
            return false;   
        }; 
    });

    // announce new post if the username of the post == username of the current profile loaded
    socket.on('announce post', data => {
        const title = data.title;
        const post = data.post;
        const date = data.date;
        const username = data.username;
        const post_id = data.post_id;
        if ( username == session_username){
        document.querySelector('#posts').innerHTML += 
            `<div class="container-fluid post" id= ${post_id}>
                    <button  class="hide hide-post">x</button>  
                        <div><label class="post-header"> ${title}</label> <label class="post-time"> ${date}</label></div>
                        <hr class="post">
                        <div class="post-body">
                        ${post}
                        </div>
                        <hr class="post">
            </div>`;
        }
        
    });

    // connect to delete message
    socket.on('connect', () => {
    // If hide button is clicked, delete the post.
    document.addEventListener('click', event => {
        const element = event.target;
        if (element.className === 'hide hide-post') {
        const post_id =  element.parentElement.id; 
        socket.emit('emit_delete_post', {'post_id': post_id} ); 
        }
        });
    });
    // When a post is deleted announce to delete post with that id
    socket.on('announce_delete_post', data => {
            const post_id = data.post_id;
            document.querySelectorAll('.container-fluid.post ').forEach(function(post) {
                if(post_id == post.id){
                    post.style.animationPlayState = 'running'; 
                    post.addEventListener('animationend', () =>  {
                    post.remove();});
                }            
    
            });   
           
    });

/********************************************************************************************************************************* */

    if(document.getElementById('alert') != null ){
    if(document.getElementById('alert').innerHTML != "" ){        
        alert(document.getElementById('alert').innerHTML);
        document.querySelector('#alert').innerHTML = ""; 
   };
};

/******************************************************************************************************************************* */


});