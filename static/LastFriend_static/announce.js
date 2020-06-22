document.addEventListener('DOMContentLoaded', () => {

    if(localStorage.getItem('mute') == "true"){
        document.getElementById('unmute').style.display = "block";
        document.getElementById('mute').style.display = "none";
    }
    else{
        document.getElementById('unmute').style.display = "none";
        document.getElementById('mute').style.display = "block";
        localStorage.setItem('mute', "false");
    }



     // Connect to websocket
    var private_socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port + '/private');
    private_socket.emit('session_sid');
     // announce new post if the username of the post == username of the current profile_user loaded
    private_socket.on('announce_notification', data => {
        const notification = data.notification;
        if(localStorage.getItem('mute') == "false"){
            console.log(localStorage.getItem('mute') == "false")
            document.getElementById('audio').play();
            document.getElementById('audio').muted = false;
        }
        alert(notification);
        
        const sender = data.sender;            
            // if user is in profile user , if that profile_user is the notification sender , reload page to get new buttons
            if (document.querySelector('#profile_user_username') != null){
                if (document.querySelector('#profile_user_username').innerHTML == sender){
                    location.reload();
                }
            } 
             // if user is in friends page -->reload
            if (document.querySelector('#my-friends') != null){
                location.reload();
            } 
        
    });  

});