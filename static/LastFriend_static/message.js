document.addEventListener('DOMContentLoaded', () => {
   // By default, submit button is disabled
    document.querySelector('#submit').disabled = true;
    // Enable button only if there is text in the input field
    document.querySelector('#txtarea').onkeyup = () => {
        if (document.querySelector('#txtarea').value.length > 0){
            // submit button is disabled if no chat is opened
            if (document.querySelector('#last_msg_username').innerHTML==""){
                document.querySelector('#submit').disabled = true;   
            }  
            else{ document.querySelector('#submit').disabled = false;
        }
    }
        else
        document.querySelector('#submit').disabled = true;
    };
    //show unseen counter
    document.querySelectorAll('.numberCircle').forEach(numberCircle => {
        const count =  parseInt(numberCircle.innerHTML);
        if (count == 0){
            numberCircle.style.display = "none";
        }
        else{
            numberCircle.parentElement.previousElementSibling.lastElementChild.style.fontWeight = "bolder";
        }
    });
     
    //open friend chat
    document.querySelectorAll('.friend-msg').forEach(friend => {
        friend.onclick = () => {
                // Initialize new request
                const request = new XMLHttpRequest();                
                request.open('POST', '/last_msg_username');
                
                // Callback function for when request completes
                request.onload = () => {
                // Extract JSON data from request
                const data = JSON.parse(request.responseText);
                if (data.success) {
                location.reload();
                }
                else {
                    alert(`User is not on your Friends. Reload Page.`);
                    location.reload();
                }
                }         
                // Add data to send with request
                const data = new FormData();
                const last_msg_username = friend.dataset.username;
                data.append('last_msg_username', last_msg_username);
                // Send request
                request.send(data);
       
        };
    
    });

    //send new message
    document.querySelector('#new_msg').onsubmit = () => {
        var message = document.querySelector('#txtarea').value;
        var reciever_username = document.querySelector('#last_msg_username').innerHTML;
        
        var private_socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port + '/private');

        private_socket.emit('emit_msg', {'reciever_username': reciever_username , 'msg': message}); 

            //****************************reset unseen counter****************************************************** */           
            // unseen count
            let counter =  0;
            //remove unseen counter
            document.getElementById(reciever_username).style.fontWeight = "normal";
            document.getElementById(reciever_username+'counter').innerHTML = `${counter}`;
            document.getElementById(reciever_username+'counter').style.display = "none";

           
            /****************************************************************************************************** */


       
        document.querySelector('#txtarea').value = '';
        document.querySelector('#submit').disabled = true;
        // Stop form from submitting
        return false;
    };
    var private_socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port + '/private');

    private_socket.on('failed_msg', data => {
        alert(data.alert);
        location.reload();     
    });

    private_socket.on('announce_msg_me', data => {

        const msg = data.msg;
        const date = data.date;
        const msg_id = data.msg_id;
        const reciever = data.reciever;
    // last message of the sender in the my friends tab
    document.getElementById(reciever).innerHTML = msg;

    document.querySelector('#feed').innerHTML += ` <div id=${msg_id} class="container-fluid message me "> 
        <button data-id=${msg_id} class="hide">x</button>      
          <p>${msg}</p>
                      <span class="time-right">${date}</span>
                    </div>` ;
    });

    //announce new message
    private_socket.on('announce_msg', data => {

        const msg = data.msg;
        const sender = data.sender
        const date = data.date;
        const msg_id = data.msg_id;
        // last message of the sender in the my friends tab
        document.getElementById(sender).innerHTML = msg;  
    
        // if the sender is opend
        if (document.querySelector('#last_msg_username').innerHTML == sender){
                    document.querySelector('#feed').innerHTML += `
                    <div id=${msg_id} class="container-fluid message other ">         
                          <p>${msg}</p>
                          <span class="time-left">${date}</span>
                        </div>`; 
            //****************************reset unseen counter****************************************************** */           
            // unseen count
            let counter =  0;
            //remove unseen counter
            document.getElementById(sender).style.fontWeight = "normal";
            document.getElementById(sender+'counter').innerHTML = `${counter}`;
            document.getElementById(sender+'counter').style.display = "none";

            //request to update unseen in server
            // Initialize new request
            const request = new XMLHttpRequest();                
            request.open('POST', '/reset_unseen_counter');
             // Callback function for when request completes
             request.onload = () => {
                // Extract JSON data from request
                const data = JSON.parse(request.responseText);
                if (data.success) {
                    console.log('sucsses');
                }
                else {
                    console.log('fail');
                }
                }   
                            
             // Add data to send with request
            const data = new FormData();
            data.append('friend_username', sender);
            // Send request
            request.send(data);
            /****************************************************************************************************** */
        }
        else{
            // unseen count
            let counter =  data.counter;
            //increase unseen counter
            document.getElementById(sender).style.fontWeight = "bolder";
            document.getElementById(sender+'counter').innerHTML = `${counter}`;
            document.getElementById(sender+'counter').style.display = "block";

            //notification new unseen message
           
            if(localStorage.getItem('mute') == "false"){
                document.getElementById('audio').play();
                document.getElementById('audio').muted = false;
            }

        }              
        
    }); 

    // connect to delete message
    
    // If hide button is clicked, delete the message.
    document.addEventListener('click', event => {
    const element = event.target;
    if (element.className === 'hide') {
    const msg_id =  element.dataset.id;                         
    private_socket.emit('emit_delete_msg', {'msg_id': msg_id} ); 
    }
    });
    // When a message is deleted, delete to the all users
    private_socket.on('announce_delete', data => {
        const msg_id = data.msg_id;
        document.querySelectorAll('.container-fluid.message ').forEach(function(msg) {
            if(msg_id == msg.id){
                msg.style.animationPlayState = 'running'; 
                msg.addEventListener('animationend', () =>  {
                msg.remove();});
            }            

        });   
       
    });

          
         


});