var dismissButton = `<span style="float: right; cursor: pointer;" onclick="this.parentElement.className = 'message'; this.parentElement.innerHTML = '';">X</span>`;
const msgDiv = document.getElementById("msg");
msgDiv.className = 'message';
msgDiv.style.display = 'none';
function showError(message) {
    msgDiv.className = 'message error';
    msgDiv.innerHTML = message + dismissButton;
    msgDiv.style.display = 'block';
    setTimeout(function () {
        msgDiv.className = 'message'; msgDiv.innerHTML = '';
    }, 5000);
}
function showInfo(message) {
    msgDiv.className = 'message info';
    msgDiv.innerHTML = message + dismissButton;
    msgDiv.style.display = 'block';
    setTimeout(function () {
        msgDiv.className = 'message'; msgDiv.innerHTML = '';
    }, 5000);
}
function showSuccess(message) {
    msgDiv.className = 'message success';
    msgDiv.innerHTML = message + dismissButton;
    msgDiv.style.display = 'block';
    setTimeout(function () {
        msgDiv.className = 'message'; msgDiv.innerHTML = '';
    }, 5000);
}
function showWarning(message) {
    msgDiv.className = 'message warning';
    msgDiv.innerHTML = message + dismissButton;
    msgDiv.style.display = 'block';
    setTimeout(function () {
        msgDiv.className = 'message'; msgDiv.innerHTML = '';
    }, 5000);
}

async function requestLogin(event) {
    event.preventDefault();

    const emailval = document.getElementById("login-email").value;
    const submitBtn = document.getElementById("submitBtn");
    const csrftoken = document.getElementsByName('csrfmiddlewaretoken')[0].value;
    console.log(emailval);
    // Show loading state
    submitBtn.disabled = true;

    try {
        const response = await fetch("/auth/request-login/", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": csrftoken
            },
            body: JSON.stringify({ email: emailval })
        });

        const data = await response.json();

        if (response.ok) {
            // Success - redirect to OTP page
            showSuccess(data.message)

            // Redirect to OTP page after 1 second
            setTimeout(() => {
                submitBtn.disabled = false;
                document.getElementById('emailDisplayLogin').textContent = emailval;
                email = emailval;
                transitionToLoginOTP();
                startTimer();
                // window.location.href = `/auth/otp/?email=${encodeURIComponent(email)}`;
            }, 1000);
        } else {
            // Error
            console.error(data);
            showError((data.error || 'An error occurred'))
            submitBtn.disabled = false;
            submitBtn.classList.remove('loading');
        }
    } catch (error) {
        showError("Network error. Please check your connection.");
        submitBtn.disabled = false;
        submitBtn.classList.remove('loading');
    }
}
function requestSignup(e) {
    e.preventDefault();
    document.getElementById("email-otp-btn").disabled = true;
    document.getElementById("email-otp-btn").children[0].hidden = false;
    document.getElementById("email-otp-btn").children[1].innerText = 'Sending...';
    const form = e.target;
    const formData = new FormData(form);
    fetch("/auth/signup/", {
        method: "POST",
        headers: {
            "X-CSRFToken": form.querySelector('[name=csrfmiddlewaretoken]').value,
        },
        body: formData
    })
        .then(response => response.json())
        .catch(error => {
            console.error(error);
            document.getElementById("email-otp-btn").disabled = false;
            document.getElementById("email-otp-btn").children[0].hidden = true;
            document.getElementById("email-otp-btn").children[1].innerText = 'Email OTP';
        })
        .then(data => {
            if (data.success) {
                showSuccess(data.message);
                document.getElementById("emailDisplay").innerText = data.email;
                email = data.email
                startTimer();
                transitionToVerifyOTPPopup();
            } else {
                showError((data.error || 'An error occurred'))
            }
            document.getElementById("email-otp-btn").disabled = false;
            document.getElementById("email-otp-btn").children[0].hidden = true;
            document.getElementById("email-otp-btn").children[1].innerText = 'Email OTP';
        })
}

// Get email from URL parameter
const urlParams = new URLSearchParams(window.location.search);
var email = urlParams.get('email');
document.getElementById('emailDisplay').textContent = email;

// OTP input handling
const otpInputs = document.querySelectorAll('.otp-digit');

otpInputs.forEach((input, index) => {
    input.addEventListener('input', (e) => {
        const value = e.target.value;

        // Only allow numbers
        if (value && !/^\d$/.test(value)) {
            e.target.value = '';
            return;
        }

        // Move to next input
        if (value && index < otpInputs.length - 1) {
            otpInputs[index + 1].focus();
        }
    });

    input.addEventListener('keydown', (e) => {
        // Move to previous input on backspace
        if (e.key === 'Backspace' && !e.target.value && index > 0) {
            otpInputs[index - 1].focus();
        }
    });

    // Allow pasting full OTP
    input.addEventListener('paste', (e) => {
        e.preventDefault();
        const pastedData = e.clipboardData.getData('text').replace(/\D/g, '');

        if (pastedData.length === 6) {
            otpInputs.forEach((input, i) => {
                input.value = pastedData[i] || '';
            });
            otpInputs[5].focus();
        }
    });
});

// Focus first input on load
otpInputs[0].focus();

// Timer countdown
function startTimer() {
    let timeLeft = 300; // 5 minutes in seconds
    const timerElement = document.getElementById('countdown');
    const timerContainer = document.getElementById('timer');
    try {
        clearInterval(timerInterval);
    }
    catch(e){console.info("Timer doesnt already exist")}
    timerContainer.classList.remove('expired');

    const timerInterval = setInterval(() => {
        timeLeft--;
        const minutes = Math.floor(timeLeft / 60);
        const seconds = timeLeft % 60;
        timerElement.textContent = `${minutes}:${seconds.toString().padStart(2, '0')}`;

        if (timeLeft <= 0) {
            clearInterval(timerInterval);
            timerContainer.classList.add('expired');
            timerElement.textContent = 'EXPIRED';
        }
    }, 1000);
}

async function loginOTP(event) {
    event.preventDefault();

    const otp = Array.from(otpInputs).map(input => input.value).join('');

    if (otp.length !== 6) {
        showError('Please enter all 6 digits', 'error');
        return;
    }

    const submitBtn = document.getElementById('submitBtn');
    submitBtn.disabled = true;
    submitBtn.classList.add('loading');

    try {
        const response = await fetch("/auth/otp-login/", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": getCookie("csrftoken")
            },
            body: JSON.stringify({ email, otp })
        });

        const data = await response.json();

        if (response.ok) {
            showSuccess('Login successful! Redirecting...');
            setTimeout(() => {
                window.location.href = data.redirect || '/';
            }, 1000);
        } else {
            showError(data.error || 'Invalid code. Please try again.');
            submitBtn.disabled = false;
            submitBtn.classList.remove('loading');

            // Clear inputs on error
            otpInputs.forEach(input => input.value = '');
            otpInputs[0].focus();
        }
    } catch (error) {
        console.log(error);
        showError('Network error. Please try again.');
        submitBtn.disabled = false;
        submitBtn.classList.remove('loading');
    }
}

async function resendCode() {
    const resendBtn = document.getElementById('resendBtn');
    resendBtn.disabled = true;
    resendBtn.children[0].hidden = false;
    resendBtn.children[1].innerText = 'Sending...';

    try {
        const response = await fetch("/auth/resend-otp/", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": getCookie("csrftoken")
            },
            body: JSON.stringify({ email })
        });

        const data = await response.json();

        if (response.ok) {
            showSuccess(data.message);

            // Re-enable button after 30 seconds
            setTimeout(() => {
                resendBtn.disabled = false;
                resendBtn.children[0].hidden = true;
                resendBtn.children[1].innerText = 'Resend Code';
            }, 30000);
        } else {
            showError(data.error || 'Failed to resend code');
            resendBtn.disabled = false;
            resendBtn.children[0].hidden = true;
            resendBtn.children[1].innerText = 'Resend Code';
        }
    } catch (error) {
        console.log(error);
        showError('Network error. Please try again.');
        resendBtn.disabled = false;
        resendBtn.children[0].hidden = true;
        resendBtn.children[1].innerText = 'Resend Code';
    }
}
function getCookie(name) {
    let cookieValue = null;
    document.cookie.split(';').forEach(cookie => {
        if (cookie.trim().startsWith(name + '=')) {
            cookieValue = cookie.split('=')[1];
        }
    });
    return cookieValue;
}