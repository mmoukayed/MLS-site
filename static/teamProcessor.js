async function leaveTeam(id) {
    if (!confirm('Are you sure you want to leave this team?')) return;
    // POST to /team/<id>/leave/
    const res = await fetch('/team/' + id + '/leave/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'X-CSRFToken': getCSRF('login-form') }
    });
    const data = await res.json();
    if (res.ok) {
        window.location.href = "/teams";
    }
    else {
        console.error(data);
        showError(data.message || "Something went wrong!");
    }
}

async function deleteTeam(id) {
    if (!confirm('Permanently delete this team? This cannot be undone.')) return;
    // DELETE to /team/<id>/delete/
    const res = await fetch('/team/' + id + '/delete/', {
        method: 'DELETE',
        headers: { 'Content-Type': 'application/json', 'X-CSRFToken': getCSRF('login-form') }
    });
    const data = await res.json();

    if (res.ok) {
        window.location.href = "/teams";
    }
    else {
        console.error(data);
        showError(data.message || "Something went wrong!");
    }
}

async function requestToJoinTeam(id) {
    // POST to /team/<id>/delete/
    const res = await fetch('/team/' + id + '/join/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'X-CSRFToken': getCSRF('login-form') }
    });
    const data = await res.json();

    if (res.ok) {
        showSuccess("Request Sent!");
        setTimeout(function() {location.reload()},1000);
    }
    else {
        console.error(data);
        showError(data.message || "Something went wrong!");
    }
}

async function cancelJoinRequest(id) {
    // POST to /team/<id>/delete/
    const res = await fetch('/team/' + id + '/cancel/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'X-CSRFToken': getCSRF('login-form') }
    });
    const data = await res.json();

    if (res.ok) {
        showSuccess("Request Cancelled!");
        setTimeout(function() {location.reload()},1000);
    }
    else {
        console.error(data);
        showError(data.message || "Something went wrong!");
    }
}

async function acceptInvite(id) {
    // POST to /team/<id>/delete/
    const res = await fetch('/team/' + id + '/invite/accept/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'X-CSRFToken': getCSRF('login-form') }
    });
    const data = await res.json();

    if (res.ok) {
        showSuccess("Invitation Accepted!");
        setTimeout(function() {location.reload()},1000);
    }
    else {
        console.error(data);
        showError(data.message || "Something went wrong!");
    }
}

async function rejectInvite(id) {
    // POST to /team/<id>/delete/
    const res = await fetch('/team/' + id + '/invite/reject/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'X-CSRFToken': getCSRF('login-form') }
    });
    const data = await res.json();

    if (res.ok) {
        showSuccess("Invitation Rejected!");
        setTimeout(function() {location.reload()},1000);
    }
    else {
        console.error(data);
        showError(data.message || "Something went wrong!");
    }
}


async function acceptJoinRequest(id, user, el) {
    // POST to /team/<id>/delete/
    const res = await fetch('/team/' + id + '/accept/' + user + '/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'X-CSRFToken': getCSRF('login-form') }
    });
    const data = await res.json();

    if (res.ok) {
        showSuccess("Request Accepted!");
        if(el.parentElement.parentElement.parentElement.parentElement.children.length <= 1) {
            el.parentElement.parentElement.parentElement.parentElement.innerHTML =  `<div class="empty-state">
            <div class="empty-state-icon">📭</div>
            <h3>No pending requests</h3>
            <p>New join requests will appear here.</p>
            </div>`;
        }
        else {
            el.parentElement.parentElement.parentElement.remove();
        }
    }
    else {
        console.error(data);
        console.error(data.message);
        showError(data.message || "Something went wrong!");
    }
}


async function rejectJoinRequest(id, user, el) {
    // POST to /team/<id>/delete/
    const res = await fetch('/team/' + id + '/reject/' + user + '/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'X-CSRFToken': getCSRF('login-form') }
    });
    const data = await res.json();

    if (res.ok) {
        showSuccess("Request Rejected!");
        if(el.parentElement.parentElement.parentElement.parentElement.children.length <= 1) {
            el.parentElement.parentElement.parentElement.parentElement.innerHTML =  `<div class="empty-state">
            <div class="empty-state-icon">📭</div>
            <h3>No pending requests</h3>
            <p>New join requests will appear here.</p>
            </div>`;
        }
        else {
            el.parentElement.parentElement.parentElement.remove();
        }
    }
    else {
        console.error(data);
        // console.warn(data["message"]);
        showError(data.message || "Something went wrong!");
    }
}

async function inviteMember(id, user, el) {
    // POST to /team/<id>/delete/
    const res = await fetch('/team/' + id + '/invite/' + user + '/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'X-CSRFToken': getCSRF('login-form') }
    });
    const data = await res.json();

    if (res.ok) {
        showSuccess("Invite Sent Successfully!");
        el.classList.remove("btn-primary");
        el.classList.add("btn-secondary");
        el.disabled = true;
        el.textContent = "Sent!";
    }
    else {
        console.error(data);
        showError(data.message || "Something went wrong!");
        el.classList.add("btn-primary");
        el.classList.remove("btn-secondary");
        el.disabled = false;
        el.textContent = "Invite";
    }
}

async function removeMember(id, user) {
    // POST to /team/<id>/delete/
    const res = await fetch('/team/' + id + '/remove/' + user + '/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'X-CSRFToken': getCSRF('login-form') }
    });
    const data = await res.json();

    if (res.ok) {
        showSuccess("Member Removed From Team Successfully!");
        setTimeout(function() {location.reload()},1000);
    }
    else {
        console.error(data);
        showError(data.message || "Something went wrong!");
    }
}

async function promoteMember(id, user) {
    // POST to /team/<id>/delete/
    const res = await fetch('/team/' + id + '/promote/' + user + '/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'X-CSRFToken': getCSRF('login-form') }
    });
    const data = await res.json();

    if (res.ok) {
        showSuccess("Member Promoted to Leader!");
        setTimeout(function() {location.reload()},1000);
    }
    else {
        console.error(data);
        showError(data.message || "Something went wrong!");
    }
}

async function demoteMember(id, user) {
    // POST to /team/<id>/delete/
    const res = await fetch('/team/' + id + '/demote/' + user + '/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'X-CSRFToken': getCSRF('login-form') }
    });
    const data = await res.json();

    if (res.ok) {
        showSuccess("Leader Demoted to Member!");
        setTimeout(function() {location.reload()},1000);
    }
    else {
        console.error(data);
        showError(data.message || "Something went wrong!");
    }
}

