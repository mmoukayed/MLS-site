// ═══════════════════════════════════════════════════════════
//  loginProcessor.js  –  All auth API calls & OTP logic
//  Works with the unified base.html modal system
// ═══════════════════════════════════════════════════════════

// ─── State ──────────────────────────────────────────────────
let loginEmail = '';
let signupEmail = '';
const timerState = { login: null, signup: null };

// ─── Utility: CSRF ──────────────────────────────────────────
function getCookie(name) {
    let val = null;
    document.cookie.split(';').forEach(c => {
        if (c.trim().startsWith(name + '=')) val = decodeURIComponent(c.split('=')[1]);
    });
    return val;
}

function getCSRF(formId) {
    const form = document.getElementById(formId);
    if (form) {
        const tok = form.querySelector('[name=csrfmiddlewaretoken]');
        if (tok) return tok.value;
    }
    return getCookie('csrftoken');
}

// ─── Utility: Button loading state ──────────────────────────
function setButtonLoading(btn, loading, defaultText = null) {
    if (!btn) return;
    const spinner = btn.querySelector('.spinner');
    const textEl  = btn.querySelector('.btn-text');
    btn.disabled = loading;
    if (spinner) spinner.hidden = !loading;
    if (textEl && defaultText && !loading) textEl.textContent = defaultText;
}

// ─── OTP input wiring ───────────────────────────────────────
function wireOTPInputs(containerId) {
    const container = document.getElementById(containerId);
    if (!container) return;
    const inputs = container.querySelectorAll('.otp-digit');

    inputs.forEach((input, i) => {
        // Only digits
        input.addEventListener('input', e => {
            e.target.value = e.target.value.replace(/\D/, '');
            if (e.target.value && i < inputs.length - 1) inputs[i + 1].focus();
        });
        // Backspace moves back
        input.addEventListener('keydown', e => {
            if (e.key === 'Backspace' && !e.target.value && i > 0) inputs[i - 1].focus();
        });
        // Paste full code
        input.addEventListener('paste', e => {
            e.preventDefault();
            const pasted = e.clipboardData.getData('text').replace(/\D/g, '');
            if (pasted.length === 6) {
                inputs.forEach((inp, j) => inp.value = pasted[j] || '');
                inputs[5].focus();
            }
        });
    });
}

function readOTP(containerId) {
    const container = document.getElementById(containerId);
    if (!container) return '';
    return Array.from(container.querySelectorAll('.otp-digit')).map(i => i.value).join('');
}

function clearOTP(containerId) {
    const container = document.getElementById(containerId);
    if (!container) return;
    const inputs = container.querySelectorAll('.otp-digit');
    inputs.forEach(i => i.value = '');
    inputs[0]?.focus();
}

// ─── Timer ──────────────────────────────────────────────────
function startTimer(flow) {
    const countdownEl  = document.getElementById(`${flow}-countdown`);
    const containerEl  = document.getElementById(`${flow}-timer`);
    if (!countdownEl || !containerEl) return;

    if (timerState[flow]) clearInterval(timerState[flow]);
    containerEl.classList.remove('expired');
    let timeLeft = 300;

    timerState[flow] = setInterval(() => {
        timeLeft--;
        const m = Math.floor(timeLeft / 60);
        const s = timeLeft % 60;
        countdownEl.textContent = `${m}:${s.toString().padStart(2, '0')}`;
        if (timeLeft <= 0) {
            clearInterval(timerState[flow]);
            containerEl.classList.add('expired');
            countdownEl.textContent = 'EXPIRED';
        }
    }, 1000);
}

// ─── Google Auth (placeholder) ──────────────────────────────
//function handleGoogleAuth(mode) {
//    showInfo('Google auth coming soon! Please use email for now.');
//}

// ════════════════════════════════════════════════════════════
//  LOGIN FLOW
// ════════════════════════════════════════════════════════════

async function requestLogin(event) {
    event.preventDefault();

    const emailInput = document.getElementById('login-email');
    const btn        = document.getElementById('loginSubmitBtn');
    const email      = emailInput?.value?.trim();

    if (!email) { showError('Please enter your email.'); return; }

    setButtonLoading(btn, true);

    try {
        const res  = await fetch('/auth/request-login/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', 'X-CSRFToken': getCSRF('login-form') },
            body: JSON.stringify({ email })
        });
        const data = await res.json();

        if (res.ok) {
            loginEmail = email;
            document.getElementById('emailDisplayLogin').textContent = email;
            showSuccess(data.message || 'Check your email!');
            setTimeout(() => {
                transitionToLoginOTP();
                startTimer('login');
                wireOTPInputs('login-otp-inputs');
            }, 800);
        } else {
            showError(data.error || 'Something went wrong.');
        }
    } catch {
        showError('Network error. Please check your connection.');
    } finally {
        setButtonLoading(btn, false, 'Send Login Code');
    }
}

// ════════════════════════════════════════════════════════════
//  SIGNUP FLOW
// ════════════════════════════════════════════════════════════

function transitionToSignupEmailPopup() {
    // Validate email before proceeding
    const emailInput = document.getElementById('signup-email');
    if (!emailInput || !emailInput.checkValidity()) {
        emailInput?.reportValidity();
        return;
    }
    // Store email for later
    signupEmail = emailInput.value.trim();
    _transition('signup-options', 'signup-by-email', 'left');
}

async function requestSignup(event) {
    event.preventDefault();

    const form = document.getElementById('signup-form');
    const btn  = document.getElementById('signupSubmitBtn');

    // Basic HTML5 validation
    if (!form.checkValidity()) { form.reportValidity(); return; }

    setButtonLoading(btn, true);

    const formData = new FormData(form);
    // Make sure email field (in step 1) is included – it's in a hidden step
    if (!formData.get('email')) formData.set('email', signupEmail);

    try {
        const res  = await fetch('/auth/signup/', {
            method: 'POST',
            headers: { 'X-CSRFToken': getCSRF('signup-form') },
            body: formData
        });
        const data = await res.json();

        if (data.success) {
            signupEmail = data.email || signupEmail;
            document.getElementById('emailDisplaySignup').textContent = signupEmail;
            showSuccess(data.message || 'Account created! Please verify your email.');
            setTimeout(() => {
                transitionToVerifyOTPPopup();
                startTimer('signup');
                wireOTPInputs('signup-otp-inputs');
            }, 800);
        } else {
            showError(data.error || 'Signup failed.');
        }
    } catch {
        showError('Network error. Please try again.');
    } finally {
        setButtonLoading(btn, false, 'Send Verification Code');
    }
}

// ════════════════════════════════════════════════════════════
//  OTP VERIFY  (shared for both login & signup flows)
// ════════════════════════════════════════════════════════════

async function loginOTP(event, flow) {
    event.preventDefault();

    const inputContainerId = flow === 'login' ? 'login-otp-inputs' : 'signup-otp-inputs';
    const otp   = readOTP(inputContainerId);
    const email = flow === 'login' ? loginEmail : signupEmail;

    if (otp.length !== 6) { showError('Please enter all 6 digits.'); return; }
    if (!email)           { showError('Session expired. Please start again.'); return; }

    // Find the verify button inside the active step
    const activePanel = flow === 'login'
        ? document.getElementById('login-otp')
        : document.getElementById('email-verify-otp');
    const btn = activePanel?.querySelector('.primary-btn');

    setButtonLoading(btn, true);

    try {
        const res  = await fetch('/auth/otp-login/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', 'X-CSRFToken': getCookie('csrftoken') },
            body: JSON.stringify({ email, otp })
        });
        const data = await res.json();

        if (res.ok) {
            showSuccess('Login successful! Redirecting…');
            setTimeout(() => { window.location.href = data.redirect || '/'; }, 1000);
        } else {
            showError(data.error || 'Invalid code. Please try again.');
            clearOTP(inputContainerId);
            setButtonLoading(btn, false, 'Verify & Login');
        }
    } catch {
        showError('Network error. Please try again.');
        setButtonLoading(btn, false, 'Verify & Login');
    }
}

// ─── Resend OTP (works for both flows) ──────────────────────
async function resendCode(flow) {
    const email = flow === 'login' ? loginEmail : signupEmail;
    const btnId = flow === 'login' ? 'loginResendBtn' : 'signupResendBtn';
    const btn = document.getElementById(btnId);

    if (!email) {
        showError('Session expired.');
        return;
    }

    if (btn) {
        btn.disabled = true;
        btn.textContent = 'Sending…';
    }

    try {
        const res = await fetch('/auth/resend-otp/', {
            method: 'POST',
            headers: {'Content-Type': 'application/json', 'X-CSRFToken': getCookie('csrftoken')},
            body: JSON.stringify({email})
        });
        const data = await res.json();

        if (res.ok) {
            showSuccess(data.message || 'New code sent!');
            startTimer(flow);
            setTimeout(() => {
                if (btn) {
                    btn.disabled = false;
                    btn.textContent = 'Resend';
                }
            }, 30000);
        } else {
            showError(data.error || 'Failed to resend.');
            if (btn) {
                btn.disabled = false;
                btn.textContent = 'Resend';
            }
        }
    } catch {
        showError('Network error.');
        if (btn) {
            btn.disabled = false;
            btn.textContent = 'Resend';
        }
    }
}