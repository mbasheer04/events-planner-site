$(document).ready(function(){
    $("#registration").submit(function(){
        var idStrings = ["fullname","username","email","password","cpassword"];
        var fieldStrings = ["Full Name","Username","Email","Password","Confirm Password"];
        var elements = [];
        var formelement = document.getElementById("registration");

        for (i=0; i<idStrings.length;i++) {
            elements.push(document.getElementById(idStrings[i]));
        }
        
        for(i=0; i<elements.length;i++){
            var errortext_id = idStrings[i] + "_error";
            removeElement(document.getElementById(errortext_id))
            if (elements[i].value==null || elements[i].value=="") {
                errortext = errorText(errortext_id,elements[i]);
                errortext.innerHTML = fieldStrings[i] + " field must be filled in.";
                return false;
            } 
        }

        if(elements[1].value.length < 8 || elements[1].value.length > 20){
            errortext = errorText("username_error",elements[1]);
            errortext.innerHTML = "Username must be between 8 and 20 characters.";
            return false;
        }

        if(!validPassword(elements[3].value)){
            errortext = errorText("password_error",elements[3]);
            errortext.innerHTML = "Password must be between 8 and 20 characters, contain lowercase letters, uppercase letters, and numbers.";
            return false;
        }
        if(elements[3].value !== elements[4].value){
            errortext = errorText("cpassword_error",elements[4]);
            errortext.innerHTML = "Passwords do not match.";
            return false;
        }

        var organiserkey = document.getElementById("organiserkey")
        if(organiserkey.value != "" && organiserkey.value != "Dc5_G1gz"){
            errortext = errorText("organiserkey_error",organiserkey);
            errortext.innerHTML = "Invalid organiser code.";
            return false;
        }
        return true;
    })

    $("#login").submit(function(){
        username = document.getElementById("username");
        password = document.getElementById("password");
        if(username.value == null || username.value == ""){
            errortext = errorText("username_error",username);
            errortext.innerHTML = "Username field must be filled in.";
            return false;
        } else if(password.value == null || password.value == ""){
            errortext = errorText("password_error",password);
            errortext.innerHTML = "Password field must be filled in.";
            return false;
        }
    })

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
    //Password
    function validPassword(password){
        var check_lowercase = false;
        var check_uppercase = false;
        var check_number = false;
        for (let i = 0; i < password.length; i++) {
            var char = password.charAt(i);
            if (!isNaN(char * 1)){
                check_number=true;
            } else if(char == char.toUpperCase()){
                check_uppercase=true;
            } else if(char == char.toLowerCase()){
                check_lowercase=true;
            }
        }
        return (check_lowercase && check_uppercase && check_number && password.length >= 8 && password.length <= 20);

    }
  });