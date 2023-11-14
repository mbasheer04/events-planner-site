$(document).ready(function(){
    $(document).on('click', '.popup-button', function(event) {
        var buttonId = $(event.target).attr('id');
        var popupBox =   "<div class='popup-background' id='popup-background'> \
                                <div class='popup' id='popup'>\
                                </div> \
                            </div>";
        $("body").prepend(popupBox);
        if ($(event.target).attr("class").includes('addticket'))
        {
            var text = "<h2>Would you like to book a ticket for " + buttonId + "?</h2> \
                        <a href='addticket?name=" + buttonId + "' class='button' id='addticket'>Buy Ticket </a>\
                        <button class='cancel' id='cancel'>Cancel</button>";
        } 
        else if ($(event.target).attr("class").includes('sellticket'))
        {
            var eventname = buttonId.substring(1);
            var text = "<h2>Are you sure you would like to sell your ticket for " + eventname + "?</h2> \
                        <a href='sellticket?name=" + eventname + "' class='button' id='sellticket'>Sell Ticket </a>\
                        <button class='cancel' id='cancel'>Cancel</button>";
        } 
        else if ($(event.target).attr("class").includes('viewticket'))
        {
            var xmlhttp = new XMLHttpRequest();
            text=""
            xmlhttp.onreadystatechange = function() {
                if (this.readyState == 4 && this.status == 200) {
                    $("#popup").prepend("<h2>" + buttonId + "</h2> \
                                         <svg>" + this.responseText + "</svg><br> \
                                         <button class='cancel' id='cancel'>Close</button>");
                }
            };
            xmlhttp.open("GET", "/generate_barcode?name="+buttonId, false);
            xmlhttp.send();  
        
        } 
        else if (buttonId=="create-event-button")
        {
            var text = "<h2>Create Event</h2> \
                        <form action='create-event' method='post'> \
                            <label for='eventname' class='formtext'>Event Name:</label> \
                                <input type='text' name='eventname' id='eventname' class='forminput'> \
                            <label for='date' class='formtext'>Date:</label> \
                                <input type='date' name='date' id='date' class='forminput'> \
                            <label for='time' class='formtext'>Time:</label> \
                                <input type='time' name='time' id='time' class='forminput'> \
                            <label for='duration' class='formtext'>Duration:</label> \
                                <input type='time' name='duration' id='duration' class='forminput'> \
                            <label for='capacity' class='formtext'>Capacity:</label> \
                                <input type='text' name='capacity' id='capacity' class='forminput'> \
                            <input class='formsubmit' type='submit' value='Submit' id='create-event'> \
                        </form> \
                        <button class='cancel' id='cancel'>Cancel</button>";
        }
        else if ($(event.target).attr("class").includes('delete-event'))
        {
            var text = "<h2>Are you sure you would like to delete the event " + buttonId + "? \
                        All attendees will be notified.</h2> \
                        <a href='delete-event?name=" + buttonId + "' class='button' id='delete-event'>Delete Event</a>\
                        <button class='cancel' id='cancel'>Cancel</button>";
        }
        else if (buttonId=="promote-user")
        {
            var text = "<h2>Promote User</h2> \
                        <form method='post' id='promote-user'> \
                            <label for='username' class='formtext'>Username:</label> \
                                <input type='text' name='username' id='username' class='forminput'> \
                            <input class='formsubmit' type='submit' value='Promote User to Website Organiser' id='class-promotion'> \
                            <label for='eventname' class='formtext'>Event Name:</label> \
                                <input type='text' name='eventname' id='eventname' class='forminput'> \
                            <input class='formsubmit' type='submit' value='Promote User to Event Organiser' id='event-promotion'> \
                        </form> \
                        <button class='cancel' id='cancel'>Cancel</button>";
        }
        $("#popup").prepend(text);
    });
    $(document).on('click','#popup-background', function(event){
        if (this == event.target){
            event.target.remove();
        }
    })
    $(document).on('click','#cancel', function(event){
        confirmBox = document.getElementById('popup-background');
        confirmBox.remove();
    })

    $(document).on('click','#create-event',function(){

        var idStrings = ["eventname","date","time","duration","capacity"];
        var fieldStrings = ["Event Name","Date","Time","Duration","Capacity"];
        var elements = [];

        for (i=0; i<idStrings.length;i++) {
            elements.push(document.getElementById(idStrings[i]));
        }
        
        for(i=0; i<elements.length;i++){
            var errortext_id = idStrings[i] + "_error";
            removeElement(document.getElementById(errortext_id))
            if (elements[i].value==null || elements[i].value=="") {
                var errortext = errorText(errortext_id,elements[i]);
                errortext.innerHTML = fieldStrings[i] + " field must be filled in.";
                return false;
            } 
        }
        return true;
    })
    
    $(document).on('click','#class-promotion',function(){
        var username = document.getElementById('username');
        var errortext_id = "username_error";
        removeElement(document.getElementById(errortext_id))
        if (username.value==null || username.value=="") {
            errortext = errorText(errortext_id,username);
            errortext.innerHTML = "Username field must be filled in.";
            return false;
        } 
        document.getElementById("promote-user").setAttribute("action","class-promotion")
        return true;
    })

    $(document).on('click','#event-promotion',function(){
        var username = document.getElementById('username');
        var eventname = document.getElementById('eventname');
        removeElement(document.getElementById("username_error"))
        removeElement(document.getElementById("eventname_error"))
        if (username.value==null || username.value=="") {
            errortext = errorText("username_error",username);
            errortext.innerHTML = "Username field must be filled in.";
            return false;
        } 
        if (eventname.value==null || eventname.value=="") {
            errortext = errorText("eventname_error",eventname);
            errortext.innerHTML = "Event Name field must be filled in.";
            return false;
        } 
        document.getElementById("promote-user").setAttribute("action","event-promotion")
        return true;
    })

    var xmlhttp = new XMLHttpRequest();
    var elements = document.getElementsByClassName("message");
    for (let i = 0; i < elements.length; i++) {
        xmlhttp.onreadystatechange = function() {
            if (this.readyState == 4 && this.status == 200) {
                elements[i].innerHTML = this.responseText;
            }
        };
        eventname = elements.item(i).nextElementSibling.getAttribute('id');
        xmlhttp.open("GET", "/check_availability?name="+eventname, false);
        xmlhttp.send(); 
    }

    //Checks if an element exists, and removes it if it does.
    function removeElement(element){
        if (document.contains(element)) {
            element.remove();
        }
    }
    //Makes an input box play the error animation (input box shakes)
    function inputError(element){
        element.classList.remove("error");
        element.offsetWidth;
        element.classList.add("error");
    }
    //Creates an error text for an input box. Parameters are: id of errortext, and the element preceding the errortext
    function errorText(errortext_id,element){
        inputError(element); 
        var errortext = document.createElement("small");
        errortext.setAttribute("class","errortext");
        errortext.setAttribute("id",errortext_id);
        element.after(errortext);
        return errortext;
    }
})