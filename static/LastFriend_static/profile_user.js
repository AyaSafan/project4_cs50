function load() {
    
    //current profile_user username
    let profile_user_username = document.querySelector('#profile_user_username').innerHTML;
    let session_name = document.querySelector('#session_name').innerHTML;

    const initial_btns = `<div class="row row-profile-add" id="initial_btns">
    <div class="col">
        <a href="#" id="send_friend_request" class="btn btn-add pluse" data-toggle="tooltip" data-placement="bottom" title="Send Friend Request" ><i class="fa fa-plus fa-add" aria-hidden="true"></i></a>
    </div>
    <div class="col">
        <a href="#"  id="block" class="btn btn-add block" data-toggle="tooltip" data-placement="bottom" title="Block User"><i class="fa fa-ban fa-add" aria-hidden="true"></i> </i></a>
    </div>
</div>`

    const cancel_reqest_btns = `<div class="row row-profile-add" id="cancel_reqest_btns">
    <div class="col">
        <a href="#" id="remove_friend_request" class="btn btn-add pluse" data-toggle="tooltip" data-placement="bottom" title="Cancel Friend Request" ><i class="fa fa-minus fa-add" aria-hidden="true"></i></a>
    </div>
    <div class="col">
        <a href="#" id="block" class="btn btn-add block" data-toggle="tooltip" data-placement="bottom" title="Block User"><i class="fa fa-ban fa-add" aria-hidden="true"></i> </i></a>
    </div>
</div>`

    const friends_btns = `<div class="row row-profile-add" id="friends_btns">
    <div class="col">
        <a href="#" id="message_request"  class="btn btn-add message" data-toggle="tooltip" data-placement="bottom" title="Message Friend"><i class="fa fa-comments fa-add" aria-hidden="true"></i></i></a>
    </div>
    <div class="col">
        <a href="#" id="remove_friend_request" class="btn btn-add remove" data-toggle="tooltip" data-placement="bottom" title="Remove Friend"><i class="fa fa-times fa-add" aria-hidden="true"></i></a>
    </div>
    <div class="col">
        <a href="#" id="block" class="btn btn-add block" data-toggle="tooltip" data-placement="bottom" title="Block User"><i class="fa fa-ban fa-add" aria-hidden="true"></i> </i></a>
    </div>
</div>`

   const unblock_btns = `<div class="row row-profile-add" id="unblock_btns">
    <div class="col">
        <a href="#" id="unblock" class="btn btn-add unblock" data-toggle="tooltip" data-placement="bottom" title="Unblock User"><i class="fa fa-ban fa-add" aria-hidden="true"></i> </i></a>
    </div> </div>`

      
    
   
    if (document.querySelector('#send_friend_request') != null){
    document.querySelector('#send_friend_request').onclick = () => {
        // Initialize new request
        const request = new XMLHttpRequest();
        
        request.open('POST', '/send_friend_request');
        
        // Callback function for when request completes
        request.onload = () => {
        // Extract JSON data from request
        const data = JSON.parse(request.responseText);
        // Update the result div
        if (data.success == "404") {
            location.reload();
        }
        else if (data.success) {
        document.querySelector('#btns-container').innerHTML = cancel_reqest_btns;
        var notification = `New friend request from ${session_name}. `; 
        var private_socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port + '/private');
        private_socket.emit('emit_notification', {'reciever_username': profile_user_username , 'notification': notification});  

        load();
        }
        else {
        alert(`You have an incoming friend request from ${profile_user_username}. Reload Page.`);
        location.reload();
        }
        }         
        // Add data to send with request
        const data = new FormData();
        data.append('profile_user_username', profile_user_username);
        // Send request
        request.send(data);
        };        
    };

    if (document.querySelector('#accept_friend_request') != null){
        document.querySelector('#accept_friend_request').onclick = () => {
                // Initialize new request
                const request = new XMLHttpRequest();
                
                request.open('POST', '/accept_friend_request');                
                // Callback function for when request completes
                request.onload = () => {
                // Extract JSON data from request
                const data = JSON.parse(request.responseText);
                // Update the result div
                if (data.success == "404") {
                    location.reload();
                }
                else if (data.success) {
                document.querySelector('#btns-container').innerHTML = friends_btns; 
                var notification = `${session_name} accepted your friend request.`;  
                var private_socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port + '/private');
                private_socket.emit('emit_notification', {'reciever_username': profile_user_username , 'notification': notification});  
                load();
                }
                else {
                alert(`Friend request is already removed. Reload Page.`);
                location.reload();
                }
                }         
                // Add data to send with request
                const data = new FormData();
                data.append('profile_user_username', profile_user_username);
                // Send request
                request.send(data);
        };        
    };

    if (document.querySelector('#remove_friend_request') != null){
        document.querySelector('#remove_friend_request').onclick = () => {
            // Initialize new request
            const request = new XMLHttpRequest();
            
            request.open('POST', '/remove_friend_request');
            
            // Callback function for when request completes
            request.onload = () => {
            // Extract JSON data from request
            const data = JSON.parse(request.responseText);
            // Update the result div
            if (data.success == "404") {
                location.reload();
            }
            else if (data.success) {
            document.querySelector('#btns-container').innerHTML = initial_btns;
            load();
            }
            else {
            alert(`Friend request is already removed. Reload Page.`);
            location.reload();
            }
            }         
            // Add data to send with request
            const data = new FormData();
            data.append('profile_user_username', profile_user_username);
            // Send request
            request.send(data);
            };        
        };

    if (document.querySelector('#block') != null){
        document.querySelector('#block').onclick = () => {
                // Initialize new request
                const request = new XMLHttpRequest();
                
                request.open('POST', '/block');                
                // Callback function for when request completes
                request.onload = () => {
                // Extract JSON data from request
                const data = JSON.parse(request.responseText);
                // Update the result div
                if (data.success == "404") {
                    location.reload();
                }
                else if (data.success) {
                document.querySelector('#btns-container').innerHTML = unblock_btns;
                document.querySelector('#remove_on_block').style.display = "none";
                load();
                }
                else {
                alert('User is already blocked.');
                loacation.reload;
                }
                }         
                // Add data to send with request
                const data = new FormData();
                data.append('profile_user_username', profile_user_username);
                // Send request
                request.send(data);
        };        
    };

    if (document.querySelector('#unblock') != null){
        document.querySelector('#unblock').onclick = () => {
                // Initialize new request
                const request = new XMLHttpRequest();
                
                request.open('POST', '/unblock');                
                // Callback function for when request completes
                request.onload = () => {
                // Extract JSON data from request
                const data = JSON.parse(request.responseText);
                // Update the result div
                if (data.success) {
                document.querySelector('#btns-container').innerHTML = initial_btns;
                document.querySelector('#remove_on_block').style.display = "block";
                load();
                }
                else {
                alert('fail');
                }
                }         
                // Add data to send with request
                const data = new FormData();
                data.append('profile_user_username', profile_user_username);
                // Send request
                request.send(data);
        };        
    };

    if (document.querySelector('#message_request') != null){
        document.querySelector('#message_request').onclick = () => {
                // Initialize new request
                const request = new XMLHttpRequest();                
                request.open('POST', '/last_msg_username');
                
                // Callback function for when request completes
                request.onload = () => {
                // Extract JSON data from request
                const data = JSON.parse(request.responseText);
                if (data.success) {
                    location.replace(location.protocol + '//' + document.domain + ':' + location.port + '/messages');
                }
                else {
                    alert(`User is not on your Friends. Reload Page.`);
                    location.reload();
                }
                }         
                // Add data to send with request
                const data = new FormData();
                const last_msg_username = profile_user_username;
                data.append('last_msg_username', last_msg_username);
                // Send request
                request.send(data);
       
        };        
    };


}

document.addEventListener('DOMContentLoaded', () => {
    load();
    let profile_user_username = document.querySelector('#profile_user_username').innerHTML;
     // Connect to websocket
    var socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port);
     // announce new post if the username of the post == username of the current profile_user loaded
    socket.on('announce post', data => {
        const title = data.title;
        const post = data.post;
        const date = data.date;
        const username = data.username;
        const post_id = data.post_id;
        if ( username == profile_user_username){
        document.querySelector('#posts').innerHTML += 
            `<div class="container-fluid post" id= ${post_id}>
                        <div><label class="post-header"> ${title}</label> <label class="post-time"> ${date}</label></div>
                        <hr class="post">
                        <div class="post-body">
                        ${post}
                        </div>
                        <hr class="post">
            </div>`;
        }
        
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


});