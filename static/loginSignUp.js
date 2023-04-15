function printError(elemId, hintMsg) {
    document.getElementById(elemId).innerHTML = hintMsg;
}

function validateLoginForm(){
    var loginUsername = document.getElementById("loginUsername").value;
    var loginPass = document.getElementById("loginPass").value;

    

    if(loginUsername==""){
        printError("loginUsernameErr", "Please enter your username.")
    }else{              
        var usernameRegEx =  /^[A-Za-z][A-Za-z0-9_]{8,20}$/;
        if(usernameRegEx.test(loginUsername)){
            printError("loginUsernameErr", "");
            loginUsernameErr = false;
        }else{
            printError("loginUsernameErr", "Please enter a valid username not less than 8 characters.");
        }
    }
    
    if(loginPass==""){
        printError("loginPassErr", "Please enter your password")
    }else{
        var loginPassRegEx = /^(?=.*[0-9])(?=.*[!@#$%^&*])[a-zA-Z0-9!@#$%^&*]{7,15}$/;
        if(loginPassRegEx.test(loginPass)){
            printError("loginPassErr", "");
            loginPassErr = false;
        }else{
            printError("loginPassErr", "Password didn't matched");
        }
    }


    if(!loginUsernameErr && !loginPassErr){
        alert("Your have login successfully !!!");
        return true;
    }else{
        return false;
    }

}

function validateSignupForm(){
    var signupUsername = document.getElementById("signupUsername").value;
    var emailAdd = document.getElementById("emailAdd").value;
    var telephone = document.getElementById("telephone").value;
    var createPass = document.getElementById("createPass").value;
    var confirmPass = document.getElementById("confirmPass").value;

    if(signupUsername==""){
        printError("signupUsernameErr", "Please enter your username.")
    }else{              
        var signupusernameRegEx =  /^[A-Za-z][A-Za-z0-9_]{8,20}$/;
        if(signupusernameRegEx.test(signupUsername)){
            printError("signupUsernameErr", "");
            signupUsernameErr = false;
        }else{
            printError("signupUsernameErr", "Please enter a valid username not less than 8 characters.");
        }
    }

    if(emailAdd==""){
        printError("emailAddErr", "Please enter your e-mail address")
    }else{
        var emailRegEx = /^\w+([\.-]?\w+)*@\w+(\.\w{2,3})+$/
        if(emailRegEx.test(emailAdd)){
            printError("emailAddErr", "");
            emailAddErr = false;
        }else{
            printError("emailAddErr", "Please enter a valid  e-mail address as 'usermail@gmail.com'.")
        }
    }

    if(telephone==""){
        printError("telephoneErr", "Please enter your password")
    }else{
        var emailRegEx =  /^\d{10}$/;
        if(emailRegEx.test(telephone)){
            printError("telephoneErr", "");
            telephoneErr = false;
        }else{
            printError("telephoneErr", "Please enter a valid 10-digit phone number.")
        }
    }


    if(createPass==""){
        printError("createPassErr", "Please enter your password")
    }else{
        var createPassRegEx = /^(?=.*[0-9])(?=.*[!@#$%^&*])[a-zA-Z0-9!@#$%^&*]{7,15}$/;
        if(createPassRegEx.test(createPass)){
            printError("createPassErr", "");
            createPassErr = false;
        }else{
            printError("createPassErr", "Please create a strong password between 7 to 15 characters which contain at least one numeric digit and a special character'.")
        }
    }

    if(confirmPass==""){
        printError("confirmPassErr", "Please enter your password")
    }else{
        if(confirmPass == createPass){
            printError("confirmPassErr", "");
            createPassErr = false;
        }else{
            printError("confirmPassErr", "Password does not matched");
        }
    }

    if(!signupUsernameErr && !emailAddErr && !telephoneErr && !createPassErr && !confirmPassErr){
        alert("Your account created successfully !!!");
        return true;
    }else{
        return false;
    }

}

function setFormMessage(formElement, type, message) {
const messageElement = formElement.querySelector(".form_message");
messageElement.textContent = message;
messageElement.classList.remove("form_message_success", "form_message_error");
messageElement.classList.add(`form_message_${type}`);
}


function setInputError(inputElement, message) {
    inputElement.classList.add("form_input_error");
    inputElement.parentElement.querySelector(".form_input_error_message").textContent = message;
}

function clearInputError(inputElement) {
    inputElement.classList.remove("form_input_error");
    inputElement.parentElement.querySelector(".form_input_error_message").textContent = "";
}

document.addEventListener("DOMContentLoaded", () => {
    const loginForm = document.querySelector("#login");
    const createAccountForm = document.querySelector("#createAccount");


    document.querySelectorAll(".form_input").forEach(inputElement => {
        inputElement.addEventListener("input", e => {
            clearInputError(inputElement);
        });

    });

    document.querySelector("#linkCreateAccount").addEventListener("click", e => {
        e.preventDefault();
        loginForm.classList.add("form_hidden");
        createAccountForm.classList.remove("form_hidden");
    });

    document.querySelector("#linkLogin").addEventListener("click", e => {
        e.preventDefault();
        loginForm.classList.remove("form_hidden");
        createAccountForm.classList.add("form_hidden");
    });

    loginForm.addEventListener("submit", e => {
        e.preventDefault();
        setFormMessage(loginForm, "error", "Invalid Username/Password");
    });
});
console.log(loginUsername);
console.log(loginPass);
console.log(signupUsername);
console.log(emailAdd);
console.log(telephone);
console.log(createPass);
console.log(confirmPass);