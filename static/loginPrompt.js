S
Copy

// ═══════════════════════════════════════════════════════════
//  loginPrompt.js  –  Modal open/close & step transitions
// ═══════════════════════════════════════════════════════════

// ─── Internal helper: animate two panels ────────────────────
//  direction: 'left'  → current slides left, next comes from right
//             'right' → current slides right, next comes from left
function _transition(hideId, showId, direction) {
    const hideEl = document.getElementById(hideId);
    const showEl = document.getElementById(showId);
    if (!hideEl || !showEl) return;

    const outAnim = direction === 'left'  ? 'fadeOutToLeft'  : 'fadeOutToRight';
    const inAnim  = direction === 'left'  ? 'fadeInFromRight' : 'fadeInFromLeft';

    hideEl.style.animation = `${outAnim} 0.35s ease-out forwards`;
    setTimeout(() => { hideEl.hidden = true; hideEl.style.animation = ''; }, 350);

    setTimeout(() => {
        showEl.hidden = false;
        showEl.style.animation = `${inAnim} 0.35s ease-out forwards`;
    }, 350);
}

// ─── Login step transitions ──────────────────────────────────
function transitionToLoginOTP() {
    _transition('login-options', 'login-otp', 'left');
}
function transitionToLoginOptions() {
    _transition('login-otp', 'login-options', 'right');
}

// ─── Signup step transitions ─────────────────────────────────
// (transitionToSignupEmailPopup is defined in loginProcessor.js
//  because it needs to validate first — but it calls _transition)
function transitionToSignupOptions() {
    // Hide whichever step is visible, show step 1
    ['signup-by-email', 'email-verify-otp'].forEach(id => {
        const el = document.getElementById(id);
        if (el && !el.hidden) {
            el.style.animation = 'fadeOutToRight 0.35s ease-out forwards';
            setTimeout(() => { el.hidden = true; el.style.animation = ''; }, 350);
        }
    });
    setTimeout(() => {
        const opts = document.getElementById('signup-options');
        opts.hidden = false;
        opts.style.animation = 'fadeInFromLeft 0.35s ease-out forwards';
    }, 350);
}
function transitionToVerifyOTPPopup() {
    _transition('signup-by-email', 'email-verify-otp', 'left');
}

// ─── Show / hide the whole overlay ──────────────────────────
function _showOverlay() {
    const overlay = document.getElementById('auth-overlay');
    if (!overlay) return;
    overlay.hidden = false;
    overlay.style.animation = 'blurBackground 0.3s linear forwards';
}

function showLoginPrompt() {
    _showOverlay();
    const signupForm = document.getElementById('signup-form');
    const loginForm  = document.getElementById('login-form');

    if (signupForm && !signupForm.hidden) {
        // Cross-fade from signup → login
        signupForm.style.animation = 'fadeOutToTop 0.25s ease-out forwards';
        setTimeout(() => { signupForm.hidden = true; }, 260);
        setTimeout(() => {
            loginForm.hidden = false;
            loginForm.style.animation = 'fadeInFromTop 0.25s ease-out forwards';
        }, 300);
    } else if (loginForm) {
        loginForm.hidden = false;
        loginForm.style.animation = 'fadeInFromTop 0.25s ease-out forwards';
    }
}

function showSignupPrompt() {
    _showOverlay();
    const loginForm  = document.getElementById('login-form');
    const signupForm = document.getElementById('signup-form');

    if (loginForm && !loginForm.hidden) {
        loginForm.style.animation = 'fadeOutToTop 0.25s ease-out forwards';
        setTimeout(() => { loginForm.hidden = true; }, 260);
        setTimeout(() => {
            signupForm.hidden = false;
            signupForm.style.animation = 'fadeInFromTop 0.25s ease-out forwards';
        }, 300);
    } else if (signupForm) {
        signupForm.hidden = false;
        signupForm.style.animation = 'fadeInFromTop 0.25s ease-out forwards';
    }
}

function dismissPrompt() {
    const overlay    = document.getElementById('auth-overlay');
    const loginForm  = document.getElementById('login-form');
    const signupForm = document.getElementById('signup-form');

    [loginForm, signupForm].forEach(f => {
        if (f && !f.hidden) {
            f.style.animation = 'fadeOutToTop 0.25s ease-out forwards';
            setTimeout(() => { f.hidden = true; f.style.animation = ''; }, 260);
        }
    });

    if (overlay) {
        overlay.style.animation = 'unblurBackground 0.3s linear forwards';
        setTimeout(() => { overlay.hidden = true; }, 320);
    }
}

// ─── Keyboard: Escape closes modal ──────────────────────────
document.addEventListener('keydown', e => {
    if (e.key === 'Escape') dismissPrompt();
});