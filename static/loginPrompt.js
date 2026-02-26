function transitionToSignupEmailPopup() {
    document.getElementById("signup-options").style.animation = "fadeOutToLeft 0.5s ease-out forwards";
    document.getElementById("email-verify-otp").style.animation = "fadeOutToLeft 0.5s ease-out forwards";
    setTimeout(function() {
        document.getElementById("signup-options").hidden = true;
        document.getElementById("email-verify-otp").hidden = true;
    },500);
    setTimeout(function() {
        document.getElementById("signup-by-email").hidden = false;
        document.getElementById("signup-by-email").style.animation = "fadeInFromRight 0.5s ease-out forwards";
    },500);
}
function transitionToSignupOptions() {
    setTimeout(function() {
        document.getElementById("signup-options").style.animation = "fadeInFromLeft 0.5s ease-out forwards";
        document.getElementById("signup-options").hidden = false;
    },500);
    document.getElementById("signup-by-email").style.animation = "fadeOutToRight 0.5s ease-out forwards";
    document.getElementById("email-verify-otp").style.animation = "fadeOutToRight 0.5s ease-out forwards";
    setTimeout(function() {
        document.getElementById("signup-by-email").hidden = true;
        document.getElementById("email-verify-otp").hidden = true;
    },500);
}
function transitionToVerifyOTPPopup() {
    setTimeout(function() {
        document.getElementById("email-verify-otp").style.animation = "fadeInFromRight 0.5s ease-out forwards";
        document.getElementById("email-verify-otp").hidden = false;
    },500);
    document.getElementById("signup-by-email").style.animation = "fadeOutToLeft 0.5s ease-out forwards";
    document.getElementById("signup-options").style.animation = "fadeOutToLeft 0.5s ease-out forwards";
    setTimeout(function() {
        document.getElementById("signup-by-email").hidden = true;
        document.getElementById("signup-options").hidden = true;
    },500);
}

function transitionToLoginOTP() {
    setTimeout(function() {
        document.getElementById("login-otp").style.animation = "fadeInFromRight 0.5s ease-out forwards";
        document.getElementById("login-otp").hidden = false;
    },500);
    document.getElementById("login-options").style.animation = "fadeOutToLeft 0.5s ease-out forwards";
    setTimeout(function() {
        document.getElementById("login-options").hidden = true;
    },500);
}
function transitionToLoginOptions() {
    setTimeout(function() {
        document.getElementById("login-options").style.animation = "fadeInFromLeft 0.5s ease-out forwards";
        document.getElementById("login-options").hidden = false;
    },500);
    document.getElementById("login-otp").style.animation = "fadeOutToRight 0.5s ease-out forwards";
    setTimeout(function() {
        document.getElementById("login-otp").hidden = true;
    },500);
}

function showLoginPrompt() {
    if(document.getElementById("signup-form").hidden == false) {
        document.getElementById("signup-form").style.animation = "fadeOutToTop 0.3s ease-out forwards";
        setTimeout(function() {
            document.getElementById("signup-form").hidden = true;
        },400);
        setTimeout(function() {
            document.getElementById("login-form").hidden = false;
            document.getElementById("login-form").style.animation = "fadeInFromTop 0.3s ease-out forwards";
        },500)
    }
    else {
        document.getElementsByClassName("account-popup-bg")[0].hidden = false;
        document.getElementsByClassName("account-popup-bg")[0].style.animation = "blurBackground 0.3s linear forwards";
        document.getElementById("login-form").hidden = false;
        document.getElementById("login-form").style.animation = "fadeInFromTop 0.3s ease-out forwards";
    }
}
function showSignupPrompt() {
    if(document.getElementById("login-form").hidden == false) {
        document.getElementById("login-form").style.animation = "fadeOutToTop 0.3s ease-out forwards";
        setTimeout(function() {
            document.getElementById("login-form").hidden = true;
        },400);
        setTimeout(function() {
            document.getElementById("signup-form").hidden = false;
            document.getElementById("signup-form").style.animation = "fadeInFromTop 0.3s ease-out forwards";
        },500)
    }
    else {
        document.getElementsByClassName("account-popup-bg")[0].hidden = false;
        document.getElementsByClassName("account-popup-bg")[0].style.animation = "blurBackground 0.3s linear forwards";
        document.getElementById("signup-form").hidden = false;
        document.getElementById("signup-form").style.animation = "fadeInFromTop 0.3s ease-out forwards";
    }
}
function dismissPrompt() {
    document.getElementById("login-form").style.animation = "fadeOutToTop 0.3s ease-out forwards";
    document.getElementById("signup-form").style.animation = "fadeOutToTop 0.3s ease-out forwards";
    setTimeout(function() {
        document.getElementById("login-form").hidden = true;
        document.getElementById("signup-form").hidden = true;
    },400);
    document.getElementsByClassName("account-popup-bg")[0].style.animation = "unblurBackground 0.3s linear forwards";
    setTimeout(function() {
        document.getElementsByClassName("account-popup-bg")[0].hidden = true;
    }, 400);
}