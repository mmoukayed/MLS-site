const dismissBtn = `<button onclick="this.parentElement.className='message';this.parentElement.style.display='none';" 
    style="float:right;background:none;border:none;cursor:pointer;font-size:18px;line-height:1;opacity:.7;" 
    aria-label="Dismiss">×</button>`;

function showMessage(type, text) {
    const el = document.getElementById('msg');
    if (!el) return;
    el.className = `message ${type}`;
    el.innerHTML = text + dismissBtn;
    el.style.display = 'block';
    clearTimeout(el._timeout);
    el._timeout = setTimeout(() => {
        el.className = 'message';
        el.style.display = 'none';
    }, 6000);
}
function showError(msg)   { showMessage('error',   msg); }
function showSuccess(msg) { showMessage('success', msg); }
function showInfo(msg)    { showMessage('info',    msg); }
function showWarning(msg) { showMessage('warning', msg); }