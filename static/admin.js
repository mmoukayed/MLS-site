const CFG = window.DASHBOARD_CONFIG;
const CSRF = () => document.querySelector('[name=csrfmiddlewaretoken]').value;

/* ─────────────────────────────────────────────────────────────────
   TAB SWITCHING
───────────────────────────────────────────────────────────────── */
function showAdminTab(tab, e) {
    ['overview', 'users', 'teams', 'events', 'content', 'cms'].forEach(t => {
        const el = document.getElementById(t + '-tab');
        if (el) el.style.display = 'none';
    });
    const target = document.getElementById(tab + '-tab');
    if (target) target.style.display = 'block';
    if (e && e.target && e.target.classList.contains('tab')) {
        document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
        e.target.classList.add('active');
    }
}

/* ─────────────────────────────────────────────────────────────────
   USER SEARCH
───────────────────────────────────────────────────────────────── */
document.getElementById("user-search").addEventListener("keyup", function () {
    const value = this.value.toLowerCase();
    document.querySelectorAll("#users-tab .item").forEach(item => {
        item.style.display = item.innerText.toLowerCase().includes(value) ? "block" : "none";
    });
});

/* ─────────────────────────────────────────────────────────────────
   ROLE POPUP
───────────────────────────────────────────────────────────────── */
function openRolePopup(email, currentRole, firstName) {
    document.getElementById("role-popup-bg").hidden = false;
    document.getElementById("role-popup").hidden = false;
    document.getElementById("role-user-email").value = email;
    document.getElementById("role-select").value = currentRole ? "True" : "False";
    document.getElementById("role-user-name").textContent = firstName;
}

function closeRolePopup() {
    document.getElementById("role-popup-bg").hidden = true;
    document.getElementById("role-popup").hidden = true;
}

function submitRoleChange(event) {
    event.preventDefault();
    fetch(CFG.urls.editRole, {
        method: "POST",
        headers: {"X-CSRFToken": CSRF(), "Content-Type": "application/x-www-form-urlencoded"},
        body: `email=${document.getElementById("role-user-email").value}&is_staff=${document.getElementById("role-select").value}`
    }).then(res => {
        if (res.ok) {
            closeRolePopup();
            location.reload();
        }
    });
}

/* ─────────────────────────────────────────────────────────────────
   DELETE USER POPUP
───────────────────────────────────────────────────────────────── */
function openDeletePopup(email, firstName) {
    document.getElementById("delete-popup-bg").hidden = false;
    document.getElementById("delete-popup").hidden = false;
    document.getElementById("delete-user-email").value = email;
    document.getElementById("delete-user-name").textContent = firstName;
}

function closeDeletePopup() {
    document.getElementById("delete-popup-bg").hidden = true;
    document.getElementById("delete-popup").hidden = true;
}

function submitDelete(event) {
    event.preventDefault();
    fetch(CFG.urls.deleteMember, {
        method: "POST",
        headers: {"X-CSRFToken": CSRF(), "Content-Type": "application/x-www-form-urlencoded"},
        body: `email=${document.getElementById("delete-user-email").value}`
    }).then(res => {
        if (res.ok) {
            closeDeletePopup();
            location.reload();
        }
    });
}

/* ─────────────────────────────────────────────────────────────────
   EVENT POPUPS
───────────────────────────────────────────────────────────────── */
function openEventPopup() {
    document.getElementById("create-event-bg").hidden = false;
    document.getElementById("create-event-popup").hidden = false;
}

function closeEventPopup() {
    document.getElementById("create-event-bg").hidden = true;
    document.getElementById("create-event-popup").hidden = true;
}

function openViewEvent(title, details, date, start, end, location, image) {
    document.getElementById("view-title").textContent = title;
    document.getElementById("view-details").textContent = details;
    document.getElementById("view-date").textContent = date;
    document.getElementById("view-start").textContent = start;
    document.getElementById("view-end").textContent = end;
    document.getElementById("view-location").textContent = location;
    document.getElementById("view-event-bg").hidden = false;
    document.getElementById("view-event-popup").hidden = false;
    const img = document.getElementById("view-image");
    if (image) {
        img.src = image;
        img.style.display = "block";
    } else {
        img.src = "";
        img.style.display = "none";
    }
}

function closeViewEvent() {
    document.getElementById("view-event-bg").hidden = true;
    document.getElementById("view-event-popup").hidden = true;
}

function openEditEvent(id, title, details, start, end, date, location) {
    document.getElementById("edit-event-id").value = id;
    const form = document.getElementById("edit-event-popup");
    form.querySelector('[name="title"]').value = title;
    form.querySelector('[name="details"]').value = details;
    form.querySelector('[name="start_time"]').value = start;
    form.querySelector('[name="end_time"]').value = end;
    form.querySelector('[name="date"]').value = date;
    form.querySelector('[name="location"]').value = location;
    document.getElementById("edit-event-bg").hidden = false;
    document.getElementById("edit-event-popup").hidden = false;
}

function closeEditEvent() {
    document.getElementById("edit-event-bg").hidden = true;
    document.getElementById("edit-event-popup").hidden = true;
}

function openDeleteEvent(id, title) {
    document.getElementById("delete-event-id").value = id;
    document.getElementById("delete-event-title").textContent = title;
    document.getElementById("delete-event-bg").hidden = false;
    document.getElementById("delete-event-popup").hidden = false;
}

function closeDeleteEvent() {
    document.getElementById("delete-event-bg").hidden = true;
    document.getElementById("delete-event-popup").hidden = true;
}

function submitDeleteEvent(e) {
    e.preventDefault();
    fetch(CFG.urls.deleteEvent, {
        method: "POST",
        headers: {"X-CSRFToken": CSRF(), "Content-Type": "application/x-www-form-urlencoded"},
        body: `event_id=${document.getElementById("delete-event-id").value}`
    }).then(res => {
        if (res.ok) {
            closeDeleteEvent();
            location.reload();
        }
    });
}

function filterEvents(filter, btn) {
    document.querySelectorAll('.event-filter').forEach(b => b.classList.remove('active-event-filter'));
    btn.classList.add('active-event-filter');
    const today = new Date().toISOString().split('T')[0];
    document.querySelectorAll('#events-tab .item[data-date]').forEach(item => {
        const date = item.dataset.date;
        let show = true;
        if (filter === 'upcoming') show = date >= today;
        if (filter === 'past') show = date < today;
        item.style.display = show ? 'block' : 'none';
    });
}

/* ─────────────────────────────────────────────────────────────────
   TEAM SEARCH + FILTER
───────────────────────────────────────────────────────────────── */
function filterTeams() {
    const query = document.getElementById("team-search").value.toLowerCase();
    document.querySelectorAll("#teams-tab .team-item").forEach(item => {
        item.style.display = item.dataset.search.includes(query) ? "block" : "none";
    });
}

function filterTeamStatus(filter, btn) {
    document.querySelectorAll('.team-filter').forEach(b => b.classList.remove('active-team-filter'));
    btn.classList.add('active-team-filter');
    document.querySelectorAll("#teams-tab .team-item").forEach(item => {
        const count = parseInt(item.dataset.members);
        let show = true;
        if (filter === 'active') show = count > 0;
        if (filter === 'empty') show = count === 0;
        item.style.display = show ? "block" : "none";
    });
}

/* ─────────────────────────────────────────────────────────────────
   VIEW TEAM
───────────────────────────────────────────────────────────────── */
function openViewTeam(name, description, memberCount, leaderCount, leadersStr, leadersList, membersList) {
    document.getElementById("vt-name").textContent = name;
    document.getElementById("vt-description").textContent = description || "No description provided.";
    document.getElementById("vt-members").textContent = memberCount;
    document.getElementById("vt-leader-count").textContent = leaderCount;
    document.getElementById("vt-leaders").textContent = "Led by: " + (leadersStr || "None");

    document.getElementById("vt-members-list").innerHTML = membersList.length
        ? membersList.map(m => `<li style="background:var(--card-bg);padding:0.4rem 0.75rem;border-radius:8px;font-size:0.9rem;color:var(--text-primary);">${m}</li>`).join("")
        : `<li style="color:var(--text-secondary);font-size:0.85rem;">No members yet</li>`;

    document.getElementById("vt-leaders-list").innerHTML = leadersList.length
        ? leadersList.map(l => `<li style="background:var(--card-bg);padding:0.4rem 0.75rem;border-radius:8px;font-size:0.9rem;color:var(--accent);">${l}</li>`).join("")
        : `<li style="color:var(--text-secondary);font-size:0.85rem;">No leaders assigned</li>`;

    document.getElementById("view-team-bg").hidden = false;
    document.getElementById("view-team-popup").hidden = false;
}

function closeViewTeam() {
    document.getElementById("view-team-bg").hidden = true;
    document.getElementById("view-team-popup").hidden = true;
}

/* ─────────────────────────────────────────────────────────────────
   EDIT TEAM
───────────────────────────────────────────────────────────────── */
const editTeamState = {member: {}, leader: {}};
let searchTimeout = null;

function openEditTeam(id, name, description, membersJson , leadersJson ) {
    membersJson = typeof membersJson === "string" ? JSON.parse(membersJson) : membersJson;
    leadersJson = typeof leadersJson === "string" ? JSON.parse(leadersJson) : leadersJson;

    document.getElementById("edit-team-id").value = id;
    document.getElementById("edit-team-name").value = name;
    document.getElementById("edit-team-desc").value = description;
    editTeamState.member = {};
    editTeamState.leader = {};
    membersJson.forEach(m => addPerson('member', m.id, m.name, m.email));
    leadersJson.forEach(l => addPerson('leader', l.id, l.name, l.email));
    document.getElementById("edit-team-bg").hidden = false;
    document.getElementById("edit-team-popup").hidden = false;
}

function closeEditTeam() {
    document.getElementById("edit-team-bg").hidden = true;
    document.getElementById("edit-team-popup").hidden = true;
    document.getElementById("member-search-input").value = "";
    document.getElementById("leader-search-input").value = "";
    document.getElementById("member-search-results").style.display = "none";
    document.getElementById("leader-search-results").style.display = "none";
}

function liveSearch(role) {
    clearTimeout(searchTimeout);
    const query = document.getElementById(`${role}-search-input`).value.trim();
    const resultsList = document.getElementById(`${role}-search-results`);
    if (query.length < 1) {
        resultsList.style.display = "none";
        return;
    }

    searchTimeout = setTimeout(() => {
        fetch(`${CFG.urls.searchMembers}?q=${encodeURIComponent(query)}`, {
            headers: {"X-CSRFToken": CSRF()}
        }).then(r => r.json()).then(data => {
            resultsList.innerHTML = "";
            if (!data.members.length) {
                resultsList.innerHTML = `<li style="padding:0.6rem 1rem;color:var(--text-secondary);font-size:0.85rem;">No results</li>`;
                resultsList.style.display = "block";
                return;
            }
            data.members.forEach(m => {
                if (editTeamState[role][m.id]) return;
                const li = document.createElement("li");
                li.style.cssText = `padding:0.6rem 1rem;cursor:pointer;font-size:0.9rem;color:var(--text-primary);border-bottom:1px solid var(--neural-line);transition:background 0.15s;`;
                li.innerHTML = `<strong>${m.name}</strong><span style="color:var(--text-secondary);margin-left:0.5rem;font-size:0.8rem;">${m.email}</span>`;
                li.onmouseenter = () => li.style.background = "var(--hover-bg, rgba(255,255,255,0.05))";
                li.onmouseleave = () => li.style.background = "";
                li.onclick = () => {
                    addPerson(role, m.id, m.name, m.email);
                    document.getElementById(`${role}-search-input`).value = "";
                    resultsList.style.display = "none";
                };
                resultsList.appendChild(li);
            });
            resultsList.style.display = "block";
        });
    }, 250);
}

function addPerson(role, id, name, email) {
    if (editTeamState[role][id]) return;
    editTeamState[role][id] = {name, email};
    renderSelected(role);
}

function removePerson(role, id) {
    delete editTeamState[role][id];
    renderSelected(role);
}

function renderSelected(role) {
    const container = document.getElementById(`selected-${role}s`);
    const hiddenInputs = document.getElementById(`${role}-hidden-inputs`);
    const fieldName = role === 'member' ? 'member_ids' : 'leader_ids';
    container.innerHTML = "";
    hiddenInputs.innerHTML = "";
    Object.entries(editTeamState[role]).forEach(([id, person]) => {
        const pill = document.createElement("div");
        pill.style.cssText = `display:flex;align-items:center;gap:0.4rem;background:var(--card-bg);border:1px solid var(--neural-line);border-radius:20px;padding:0.3rem 0.75rem;font-size:0.85rem;color:${role === 'leader' ? 'var(--accent)' : 'var(--text-primary)'};`;
        pill.innerHTML = `${person.name}<span onclick="removePerson('${role}','${id}')" style="cursor:pointer;color:var(--text-secondary);font-size:1rem;line-height:1;">&times;</span>`;
        container.appendChild(pill);
        const input = document.createElement("input");
        input.type = "hidden";
        input.name = fieldName;
        input.value = id;
        hiddenInputs.appendChild(input);
    });
}

document.addEventListener("click", function (e) {
    if (!e.target.closest("#edit-team-popup")) {
        document.getElementById("member-search-results").style.display = "none";
        document.getElementById("leader-search-results").style.display = "none";
    }
});

/* ─────────────────────────────────────────────────────────────────
   DELETE TEAM
───────────────────────────────────────────────────────────────── */
function openDeleteTeam(id, title) {
    document.getElementById("delete-team-id").value = id;
    document.getElementById("delete-team-title").textContent = title;
    document.getElementById("delete-team-bg").hidden = false;
    document.getElementById("delete-team-popup").hidden = false;
}

function closeDeleteTeam() {
    document.getElementById("delete-team-bg").hidden = true;
    document.getElementById("delete-team-popup").hidden = true;
}

function submitDeleteTeam(e) {
    e.preventDefault();
    fetch(CFG.urls.deleteTeam, {
        method: "POST",
        headers: {"X-CSRFToken": CSRF(), "Content-Type": "application/x-www-form-urlencoded"},
        body: `team_id=${document.getElementById("delete-team-id").value}`
    }).then(res => {
        if (res.ok) {
            closeDeleteTeam();
            location.reload();
        }
    });
}

/* ═════════════════════════════════════════════════════════════════
   CONTENT TAB — inject scoped CSS once
═════════════════════════════════════════════════════════════════ */
(function () {
    const css = `
    .active-content-filter { background: var(--accent) !important; color: #fff !important; border-color: var(--accent) !important; }
    .active-content-sort   { border-color: var(--accent) !important; color: var(--accent) !important; }
    .content-upload-zone   { display:flex; align-items:center; gap:8px; padding:10px 12px; border:1px dashed var(--neural-line); border-radius:8px; cursor:pointer; transition:border-color .2s, background .2s; }
    .content-upload-zone:hover { border-color:var(--accent); background:rgba(249,115,22,.04); }
    .content-upload-area   { display:flex; align-items:center; gap:10px; padding:12px; background:var(--bg-secondary); border:1px dashed var(--neural-line); border-radius:10px; cursor:pointer; margin-bottom:8px; width:100%; transition:border-color .2s; }
    .content-upload-area:hover { border-color:var(--accent); }
    .content-file-list     { display:flex; flex-direction:column; gap:5px; margin-bottom:8px; }
    .content-file-row      { display:flex; align-items:center; gap:8px; background:var(--bg-secondary); border:1px solid var(--neural-line); border-radius:8px; padding:7px 10px; animation:cfSlide .2s ease; }
    @keyframes cfSlide     { from{opacity:0;transform:translateY(-4px);}to{opacity:1;transform:translateY(0);} }
    .content-file-name     { font-size:11px; font-weight:600; flex:1; min-width:0; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }
    .content-file-size     { font-size:10px; color:var(--text-secondary); flex-shrink:0; }
    .content-file-new      { font-size:9px; font-weight:700; background:rgba(16,185,129,.15); color:#10b981; border-radius:4px; padding:2px 5px; flex-shrink:0; }
    .content-file-rm       { background:none; border:none; color:var(--text-secondary); cursor:pointer; font-size:12px; padding:2px 5px; border-radius:4px; flex-shrink:0; transition:all .15s; }
    .content-file-rm:hover { background:rgba(239,68,68,.15); color:#ef4444; }
    .content-prog          { height:2px; background:var(--neural-line); border-radius:2px; margin-top:3px; overflow:hidden; }
    .content-prog-bar      { height:100%; background:var(--accent); animation:cfProg 1s ease forwards; }
    @keyframes cfProg      { from{width:0;}to{width:100%;} }
    .content-ver-item      { display:flex; align-items:center; gap:8px; font-size:11px; color:var(--text-secondary); }
    .content-ver-num       { background:rgba(249,115,22,.12); color:var(--accent); border-radius:4px; padding:2px 7px; font-size:10px; border:1px solid var(--accent); flex-shrink:0; }
    .content-status-dot    { width:7px; height:7px; border-radius:50%; flex-shrink:0; display:inline-block; }
    .content-status-dot.published { background:#10b981; box-shadow:0 0 5px #10b981; }
    .content-status-dot.draft     { background:#f59e0b; }
    .content-status-dot.archived  { background:var(--text-secondary); }
    .content-view-section  { margin-top:1rem; }
    .content-view-section h4 { font-size:9px; font-weight:700; color:var(--accent); text-transform:uppercase; letter-spacing:1.5px; margin-bottom:8px; }
    .content-file-pill     { display:flex; align-items:center; gap:10px; padding:8px 12px; border-radius:10px; background:var(--bg-secondary); border:1px solid var(--neural-line); margin-bottom:6px; }
    .content-pill-name     { font-size:.82rem; font-weight:600; flex:1; }
    .content-pill-size     { font-size:10px; color:var(--text-secondary); }
    .content-pill-dl       { padding:4px 10px; border-radius:50px; border:1px solid var(--neural-line); background:none; font-size:10px; font-weight:700; color:var(--text-secondary); cursor:pointer; transition:all .2s; }
    .content-pill-dl:hover { border-color:var(--accent); color:var(--accent); }
    .content-toast         { display:flex; align-items:center; gap:9px; padding:11px 16px; background:var(--card-bg); border:1px solid var(--neural-line); border-radius:12px; min-width:220px; font-size:.82rem; font-weight:600; box-shadow:0 8px 32px rgba(0,0,0,.45); animation:cfToast .3s cubic-bezier(.16,1,.3,1); pointer-events:all; }
    @keyframes cfToast     { from{transform:translateX(110%);opacity:0;}to{transform:translateX(0);opacity:1;} }
    .content-toast.ok      { border-left:3px solid #10b981; }
    .content-toast.warn    { border-left:3px solid #f59e0b; }
    .content-toast.err     { border-left:3px solid #ef4444; }
    `;
    const s = document.createElement('style');
    s.textContent = css;
    document.head.appendChild(s);
})();

/* ═════════════════════════════════════════════════════════════════
   CONTENT TAB JS
═════════════════════════════════════════════════════════════════ */
const currentUserId = CFG.currentUserId;
let posts = Array.isArray(CFG.workshops) ? CFG.workshops : [];

let c_tab = 'published', c_sort = 'date', c_q = '', c_type = '';
let c_sel = new Set(), c_editing = null, c_deleting = null, c_viewing = null;
let c_newFiles = {documents: [], presentations: [], videos: [], resources: []};
let c_editFiles = [];
let c_removeFileIds = [];
const C_LIMITS = {doc: 50, ppt: 100, vid: 500, res: 50};

function cIsOwner(p) {
    return p.creator_id === currentUserId;
}

function cToast(msg, type = 'ok') {
    const el = document.createElement('div');
    el.className = 'content-toast ' + type;
    el.textContent = ({ok: '✓', warn: '⚠', err: '✕'})[type] + ' ' + msg;
    document.getElementById('cmsToasts').appendChild(el);
    setTimeout(() => el.remove(), 3200);
}

function cDate(d) {
    return new Date(d).toLocaleDateString('en-US', {month: 'short', day: 'numeric', year: 'numeric'});
}

function cBytes(b) {
    if (!b) return '0 B';
    const k = 1024, s = ['B', 'KB', 'MB', 'GB'], i = Math.floor(Math.log(b) / Math.log(k));
    return parseFloat((b / k ** i).toFixed(1)) + ' ' + s[i];
}

function cFiltered() {
    return posts
        .filter(p => p.status === c_tab)
        .filter(p => !c_type || p.type === c_type)
        .filter(p => {
            if (!c_q) return true;
            const q = c_q.toLowerCase();
            return [p.title, p.module, p.desc, ...(p.tags || [])].some(s => s && s.toLowerCase().includes(q));
        })
        .filter(p => c_sort === 'mine' ? cIsOwner(p) : true)
        .sort((a, b) => {
            if (c_sort === 'title') return a.title.localeCompare(b.title);
            return new Date(b.date) - new Date(a.date);
        });
}

function cRender() {
    const list = cFiltered(), ul = document.getElementById('contentItemList');
    document.getElementById('contentResultCount').textContent = list.length + ' result' + (list.length !== 1 ? 's' : '');

    if (!list.length) {
        const msgs = {
            published: ['No published workshops yet', 'Upload and publish materials.'],
            draft: ['No drafts', 'Start a new draft above.'],
            archived: ['Nothing archived', 'Archived content appears here.'],
        };
        ul.innerHTML = '<li class="item"><div class="item-header"><div>'
            + '<span class="item-title">' + msgs[c_tab][0] + '</span>'
            + '<div class="item-meta">' + msgs[c_tab][1] + '</div>'
            + '</div></div></li>';
        return;
    }

    ul.innerHTML = list.map(p => {
        const mine = cIsOwner(p);
        const meta = cDate(p.date) + ' · v' + p.version
            + (p.module ? ' · ' + p.module : '')
            + (mine ? '' : ' · <em style="color:var(--text-secondary);font-style:normal;">by ' + p.creator_name + '</em>');

        let actions = '<button class="btn btn-small btn-secondary" onclick="cOpenView(' + p.id + ')">View</button>';
        if (mine) {
            actions += '<button class="btn btn-small btn-secondary" onclick="cOpenEdit(' + p.id + ')">Edit</button>';
            if (p.status === 'draft') actions += '<button class="btn btn-small btn-secondary" onclick="cPublish(' + p.id + ')">Publish</button>';
            else if (p.status === 'published') actions += '<button class="btn btn-small btn-secondary" onclick="cArchive(' + p.id + ')">Archive</button>';
            else actions += '<button class="btn btn-small btn-secondary" onclick="cUnarchive(' + p.id + ')">Unarchive</button>';
            actions += '<button class="btn btn-small btn-danger" onclick="cOpenDel(' + p.id + ')">Delete</button>';
        }

        return '<li class="item" data-id="' + p.id + '">'
            + '<div class="item-header">'
            + '<div style="display:flex;align-items:center;gap:0.75rem;flex:1;min-width:0;">'
            + (mine ? '<input type="checkbox" class="content-cb" data-id="' + p.id + '" style="accent-color:var(--accent);width:15px;height:15px;cursor:pointer;flex-shrink:0;"' + (c_sel.has(p.id) ? ' checked' : '') + '>' : '<span style="width:15px;flex-shrink:0;"></span>')
            + '<div style="min-width:0;">'
            + '<div class="item-title" style="display:flex;align-items:center;gap:8px;">'
            + '<span class="content-status-dot ' + p.status + '"></span>' + p.title
            + (mine ? '' : '<span style="font-size:9px;color:var(--text-secondary);border:1px solid var(--neural-line);border-radius:4px;padding:1px 6px;">' + p.creator_name + '</span>')
            + '</div>'
            + '<div class="item-meta">' + meta + '</div>'
            + '</div></div>'
            + '<div class="item-actions" style="flex-shrink:0;">' + actions + '</div>'
            + '</div></li>';
    }).join('');

    ul.querySelectorAll('.content-cb').forEach(cb => {
        cb.addEventListener('change', e => {
            e.target.checked ? c_sel.add(+e.target.dataset.id) : c_sel.delete(+e.target.dataset.id);
            cUpdateBulk();
        });
    });
    cUpdateBulk();
}

function setContentTab(tab, btn) {
    document.querySelectorAll('.content-filter').forEach(b => b.classList.remove('active-content-filter'));
    btn.classList.add('active-content-filter');
    c_tab = tab;
    c_sel.clear();
    cRender();
}

document.querySelectorAll('.content-sort').forEach(chip => chip.addEventListener('click', () => {
    document.querySelectorAll('.content-sort').forEach(c => c.classList.remove('active-content-sort'));
    chip.classList.add('active-content-sort');
    c_sort = chip.dataset.sort;
    cRender();
}));

document.getElementById('contentSearch').addEventListener('input', e => {
    c_q = e.target.value.trim();
    cRender();
});
document.getElementById('contentFilterType').addEventListener('change', e => {
    c_type = e.target.value;
    cRender();
});

/* ── STATUS CHANGES ── */
function cSetStatus(id, status) {
    fetch(CFG.urls.setWorkshopStatus, {
        method: 'POST',
        headers: {'X-CSRFToken': CSRF(), 'Content-Type': 'application/x-www-form-urlencoded'},
        body: new URLSearchParams({workshop_ids: id, status}),
    }).then(r => r.json()).then(d => {
        if (d.ok) {
            const p = posts.find(x => x.id === id);
            if (p) p.status = status;
            cRender();
        } else cToast('Error updating status', 'err');
    });
}

function cPublish(id) {
    const p = posts.find(x => x.id === id);
    if (p && cIsOwner(p)) {
        cSetStatus(id, 'published');
        cToast('"' + p.title + '" published!');
    }
}

function cArchive(id) {
    const p = posts.find(x => x.id === id);
    if (p && cIsOwner(p)) {
        cSetStatus(id, 'archived');
        cToast('"' + p.title + '" archived', 'warn');
    }
}

function cUnarchive(id) {
    const p = posts.find(x => x.id === id);
    if (p && cIsOwner(p)) {
        cSetStatus(id, 'draft');
        cToast('"' + p.title + '" moved to Drafts');
    }
}

/* ── FILE ROW HELPERS ── */
function cMakeFileRow(name, sizeStr, isNew = false) {
    const d = document.createElement('div');
    d.className = 'content-file-row';
    d.innerHTML = '<span class="content-file-name">' + name + '</span>'
        + '<span class="content-file-size">' + sizeStr + '</span>'
        + (isNew ? '<span class="content-file-new">NEW</span><div class="content-prog"><div class="content-prog-bar"></div></div>' : '')
        + '<button class="content-file-rm" type="button">✕</button>';
    return d;
}

/* ── EDIT POPUP ── */
function openContentEdit() {
    document.getElementById('content-edit-bg').hidden = false;
    document.getElementById('content-edit-popup').hidden = false;
}

function closeContentEdit() {
    document.getElementById('content-edit-bg').hidden = true;
    document.getElementById('content-edit-popup').hidden = true;
    c_editing = null;
    c_editFiles = [];
    c_removeFileIds = [];
}

function cRenderEditFiles() {
    const list = document.getElementById('eFileList');
    if (!c_editFiles.length) {
        list.innerHTML = '<p style="font-size:12px;color:var(--text-secondary);">No files attached.</p>';
        return;
    }
    list.innerHTML = '';
    c_editFiles.forEach((f, idx) => {
        const row = cMakeFileRow(f.name, f.size, f.isNew);
        row.querySelector('.content-file-rm').onclick = () => {
            if (f.id) c_removeFileIds.push(f.id);
            c_editFiles.splice(idx, 1);
            cRenderEditFiles();
            cToast('"' + f.name + '" removed', 'warn');
        };
        list.appendChild(row);
    });
}

function cHandleEditUpload(zoneKey, files) {
    const maxMB = C_LIMITS[zoneKey];
    let added = 0;
    Array.from(files).forEach(file => {
        if (file.size > maxMB * 1024 * 1024) {
            cToast(file.name + ' exceeds ' + maxMB + ' MB', 'warn');
            return;
        }
        c_editFiles.push({name: file.name, size: cBytes(file.size), isNew: true, file, zoneKey});
        added++;
    });
    if (added) {
        cRenderEditFiles();
        cToast(added + ' file' + (added > 1 ? 's' : '') + ' added');
    }
}

['doc', 'ppt', 'vid', 'res'].forEach(key => {
    const inp = document.getElementById('eUpload_' + key);
    inp.addEventListener('change', e => {
        cHandleEditUpload(key, e.target.files);
        inp.value = '';
    });
    inp.closest('label').addEventListener('dragover', e => {
        e.preventDefault();
        e.currentTarget.style.borderColor = 'var(--accent)';
    });
    inp.closest('label').addEventListener('dragleave', e => {
        e.currentTarget.style.borderColor = '';
    });
    inp.closest('label').addEventListener('drop', e => {
        e.preventDefault();
        e.currentTarget.style.borderColor = '';
        cHandleEditUpload(key, e.dataTransfer.files);
    });
});

function cOpenEdit(id) {
    const p = posts.find(x => x.id === id);
    if (!p) return;
    if (!cIsOwner(p)) {
        cToast('You can only edit your own workshops', 'warn');
        return;
    }
    c_editing = id;
    c_removeFileIds = [];
    document.getElementById('contentEditTitle').textContent = p.status === 'draft' ? 'Edit Draft' : 'Edit Workshop';
    document.getElementById('eField_status').value = p.status;
    document.getElementById('eField_title').value = p.title;
    document.getElementById('eField_module').value = p.module || '';
    document.getElementById('eField_desc').value = p.desc || '';
    document.getElementById('eField_tags').value = (p.tags || []).join(', ');
    document.getElementById('eField_version').value = p.version;
    document.getElementById('verList').innerHTML = (p.history || []).map(h =>
        '<div class="content-ver-item"><span class="content-ver-num">v' + h.v + '</span><span>' + h.date + '</span></div>'
    ).join('');
    c_editFiles = (p.files || []).map(f => ({id: f.id, name: f.name, size: f.size, isNew: false}));
    cRenderEditFiles();
    openContentEdit();
}

document.getElementById('contentEditCancel').onclick = closeContentEdit;
document.getElementById('content-edit-bg').addEventListener('click', e => {
    if (e.target === document.getElementById('content-edit-bg')) closeContentEdit();
});

document.getElementById('contentEditSave').addEventListener('click', () => {
    const p = posts.find(x => x.id === c_editing);
    if (!p) return;
    const fd = new FormData();
    fd.append('workshop_id', c_editing);
    fd.append('status', document.getElementById('eField_status').value);
    fd.append('title', document.getElementById('eField_title').value.trim());
    fd.append('module', document.getElementById('eField_module').value.trim());
    fd.append('desc', document.getElementById('eField_desc').value.trim());
    fd.append('tags', document.getElementById('eField_tags').value);
    fd.append('version', document.getElementById('eField_version').value.trim() || p.version);
    c_removeFileIds.forEach(rid => fd.append('remove_file_ids', rid));
    const typeMap = {doc: 'documents', ppt: 'presentations', vid: 'videos', res: 'resources'};
    c_editFiles.filter(f => f.isNew && f.file).forEach(f => fd.append(typeMap[f.zoneKey] || 'resources', f.file));

    fetch(CFG.urls.editWorkshop, {method: 'POST', headers: {'X-CSRFToken': CSRF()}, body: fd})
        .then(r => r.json()).then(d => {
        if (d.ok) {
            Object.assign(p, {
                status: fd.get('status'), title: fd.get('title') || p.title,
                module: fd.get('module'), desc: fd.get('desc'),
                tags: fd.get('tags').split(',').map(t => t.trim()).filter(Boolean),
                version: fd.get('version'),
                files: c_editFiles.filter(f => !f.isNew).map(({id, name, size}) => ({id, name, size})),
            });
            closeContentEdit();
            cRender();
            cToast('Changes saved!');
        } else {
            cToast(d.error === 'Forbidden' ? 'You can only edit your own workshops' : 'Save failed', 'err');
        }
    });
});

/* ── VIEW POPUP ── */
function cOpenView(id) {
    c_viewing = id;
    const p = posts.find(x => x.id === id);
    if (!p) return;
    const pills = (p.files || []).map(f =>
        '<div class="content-file-pill"><span class="content-pill-name">' + f.name + '</span>'
        + '<span class="content-pill-size">' + f.size + '</span>'
        + '<a className="content-pill-dl" href="/workshops/file/' + f.id + '/" download>Download</a>'
    ).join('');
    document.getElementById('contentViewBody').innerHTML =
        '<p style="font-weight:800;font-size:1rem;margin-bottom:8px;">' + p.title + '</p>'
        + '<div style="display:flex;align-items:center;gap:8px;margin-bottom:10px;flex-wrap:wrap;">'
        + '<span class="badge" style="background:rgba(255,255,255,.07);color:var(--text-secondary);">' + p.type + '</span>'
        + '<span class="badge" style="background:rgba(255,255,255,.07);color:var(--text-secondary);">v' + p.version + '</span>'
        + '</div>'
        + '<p style="font-size:.85rem;color:var(--text-secondary);line-height:1.7;">' + (p.desc || 'No description.') + '</p>'
        + (p.module ? '<div class="content-view-section"><h4>Module</h4><p style="font-size:.85rem;color:var(--text-secondary)">' + p.module + '</p></div>' : '')
        + '<div class="content-view-section"><h4>Attachments</h4>' + (pills || '<p style="font-size:.85rem;color:var(--text-secondary)">No files attached.</p>') + '</div>'
        + '<div class="content-view-section"><h4>Date</h4><p style="font-size:.85rem;color:var(--text-secondary)">' + cDate(p.date) + '</p></div>';
    document.getElementById('contentViewEditBtn').style.display = cIsOwner(p) ? '' : 'none';
    document.getElementById('content-view-bg').hidden = false;
    document.getElementById('content-view-popup').hidden = false;
}

function closeContentView() {
    document.getElementById('content-view-bg').hidden = true;
    document.getElementById('content-view-popup').hidden = true;
    c_viewing = null;
}

document.getElementById('content-view-bg').addEventListener('click', e => {
    if (e.target === document.getElementById('content-view-bg')) closeContentView();
});
document.getElementById('contentViewEditBtn').onclick = () => {
    const id = c_viewing;
    closeContentView();
    if (id) cOpenEdit(id);
};

/* ── DELETE POPUP ── */
function cOpenDel(id) {
    const p = posts.find(x => x.id === id);
    if (!p || !cIsOwner(p)) {
        cToast('You can only delete your own workshops', 'warn');
        return;
    }
    c_deleting = id;
    document.getElementById('contentDeleteName').textContent = p.title;
    document.getElementById('content-delete-bg').hidden = false;
    document.getElementById('content-delete-popup').hidden = false;
}

function closeContentDelete() {
    document.getElementById('content-delete-bg').hidden = true;
    document.getElementById('content-delete-popup').hidden = true;
    c_deleting = null;
}

document.getElementById('content-delete-bg').addEventListener('click', e => {
    if (e.target === document.getElementById('content-delete-bg')) closeContentDelete();
});
document.getElementById('contentDeleteConfirm').addEventListener('click', () => {
    const p = posts.find(x => x.id === c_deleting);
    fetch(CFG.urls.deleteWorkshop, {
        method: 'POST',
        headers: {'X-CSRFToken': CSRF(), 'Content-Type': 'application/x-www-form-urlencoded'},
        body: new URLSearchParams({workshop_id: c_deleting}),
    }).then(r => r.json()).then(d => {
        if (d.ok) {
            posts = posts.filter(x => x.id !== c_deleting);
            c_sel.delete(c_deleting);
            closeContentDelete();
            cRender();
            cToast('"' + (p ? p.title : 'item') + '" deleted', 'err');
        } else {
            cToast(d.error === 'Forbidden' ? 'You can only delete your own workshops' : 'Delete failed', 'err');
        }
    });
});

/* ── NEW DRAFT POPUP ── */
function cSetupNewFileInput(inputId, listId, storeKey) {
    document.getElementById(inputId).addEventListener('change', function () {
        Array.from(this.files).forEach(file => {
            if (c_newFiles[storeKey].find(f => f.name === file.name && f.size === file.size)) return;
            c_newFiles[storeKey].push(file);
            const row = cMakeFileRow(file.name, cBytes(file.size), true);
            row.querySelector('.content-file-rm').onclick = () => {
                c_newFiles[storeKey] = c_newFiles[storeKey].filter(f => !(f.name === file.name && f.size === file.size));
                row.remove();
            };
            document.getElementById(listId).appendChild(row);
        });
        this.value = '';
    });
}

cSetupNewFileInput('documentUpload', 'documentList', 'documents');
cSetupNewFileInput('presentationUpload', 'presentationList', 'presentations');
cSetupNewFileInput('videoUpload', 'videoList', 'videos');
cSetupNewFileInput('resourceUpload', 'resourceList', 'resources');

document.getElementById('addVideoLink').addEventListener('click', () => {
    const inp = document.getElementById('videoLink'), url = inp.value.trim();
    if (!url) return;
    if (!url.startsWith('http')) {
        cToast('Enter a valid URL', 'warn');
        return;
    }
    const row = cMakeFileRow(url, 'Video Link', false);
    row.querySelector('.content-file-rm').onclick = () => row.remove();
    document.getElementById('videoLinkList').appendChild(row);
    inp.value = '';
    cToast('Link added!');
});

function openNewDraft() {
    ['nField_title', 'nField_module', 'nField_desc', 'nField_tags'].forEach(id => document.getElementById(id).value = '');
    document.getElementById('nField_version').value = '1.0';
    c_newFiles = {documents: [], presentations: [], videos: [], resources: []};
    ['documentList', 'presentationList', 'videoList', 'videoLinkList', 'resourceList'].forEach(id => {
        const el = document.getElementById(id);
        if (el) el.innerHTML = '';
    });
    document.getElementById('content-newdraft-bg').hidden = false;
    document.getElementById('content-newdraft-popup').hidden = false;
    setTimeout(() => document.getElementById('nField_title').focus(), 100);
}

function closeNewDraft() {
    document.getElementById('content-newdraft-bg').hidden = true;
    document.getElementById('content-newdraft-popup').hidden = true;
}

document.getElementById('content-newdraft-bg').addEventListener('click', e => {
    if (e.target === document.getElementById('content-newdraft-bg')) closeNewDraft();
});

document.getElementById('contentNewDraftSave').addEventListener('click', () => {
    const title = document.getElementById('nField_title').value.trim();
    if (!title) {
        cToast('Title is required', 'warn');
        return;
    }
    const fd = new FormData();
    fd.append('title', title);
    fd.append('type', document.getElementById('nField_type').value);
    fd.append('module', document.getElementById('nField_module').value.trim());
    fd.append('desc', document.getElementById('nField_desc').value.trim());
    fd.append('tags', document.getElementById('nField_tags').value);
    fd.append('version', document.getElementById('nField_version').value.trim() || '1.0');
    c_newFiles.documents.forEach(f => fd.append('documents', f));
    c_newFiles.presentations.forEach(f => fd.append('presentations', f));
    c_newFiles.videos.forEach(f => fd.append('videos', f));
    c_newFiles.resources.forEach(f => fd.append('resources', f));

    fetch(CFG.urls.createWorkshop, {method: 'POST', headers: {'X-CSRFToken': CSRF()}, body: fd})
        .then(r => r.json()).then(d => {
        if (d.ok) {
            const allFiles = [...c_newFiles.documents, ...c_newFiles.presentations, ...c_newFiles.videos, ...c_newFiles.resources]
                .map(f => ({name: f.name, size: cBytes(f.size)}));
            posts.unshift({
                id: d.id, type: fd.get('type'), title,
                module: fd.get('module'), desc: fd.get('desc'),
                tags: fd.get('tags').split(',').map(t => t.trim()).filter(Boolean),
                version: fd.get('version'), status: 'draft',
                date: new Date().toISOString().split('T')[0],
                creator_id: currentUserId, files: allFiles,
                history: [{v: '1.0', date: 'Today'}],
            });
            closeNewDraft();
            c_tab = 'draft';
            document.querySelectorAll('.content-filter').forEach(b => {
                b.classList.toggle('active-content-filter', b.textContent.trim() === 'Drafts');
            });
            cRender();
            cToast('Draft "' + title + '" created' + (allFiles.length ? ' with ' + allFiles.length + ' file(s)' : '') + '!');
        } else {
            cToast('Failed to create draft', 'err');
        }
    });
});

/* ── BULK BAR ── */
function cUpdateBulk() {
    const bar = document.getElementById('contentBulkBar');
    bar.style.display = c_sel.size ? 'flex' : 'none';
    document.getElementById('contentBulkCount').textContent = c_sel.size + ' selected';
}

function cBulkStatus(status, label) {
    const ids = [...c_sel];
    const body = new URLSearchParams({status});
    ids.forEach(id => body.append('workshop_ids', id));
    fetch(CFG.urls.setWorkshopStatus, {
        method: 'POST',
        headers: {'X-CSRFToken': CSRF(), 'Content-Type': 'application/x-www-form-urlencoded'},
        body,
    }).then(r => r.json()).then(d => {
        if (d.ok) {
            ids.forEach(id => {
                const p = posts.find(x => x.id === id);
                if (p && cIsOwner(p)) p.status = status;
            });
            c_sel.clear();
            cRender();
            cToast(d.updated + ' item(s) ' + label, status === 'archived' ? 'warn' : 'ok');
        } else cToast('Bulk action failed', 'err');
    });
}

document.getElementById('bulkPublish').addEventListener('click', () => cBulkStatus('published', 'published!'));
document.getElementById('bulkArchive').addEventListener('click', () => cBulkStatus('archived', 'archived'));
document.getElementById('bulkDelete').addEventListener('click', () => {
    const ids = [...c_sel];
    Promise.all(ids.map(id =>
        fetch(CFG.urls.deleteWorkshop, {
            method: 'POST',
            headers: {'X-CSRFToken': CSRF(), 'Content-Type': 'application/x-www-form-urlencoded'},
            body: new URLSearchParams({workshop_id: id}),
        }).then(r => r.json())
    )).then(results => {
        const ok = results.filter(r => r.ok).length;
        posts = posts.filter((p, i) => !ids.includes(p.id) || !results[ids.indexOf(p.id)]?.ok);
        c_sel.clear();
        cRender();
        cToast(ok + ' item(s) deleted', 'err');
    });
});
document.getElementById('bulkClear').addEventListener('click', () => {
    c_sel.clear();
    cRender();
});

/* ── KEYBOARD SHORTCUTS ── */
document.addEventListener('keydown', e => {
    if (e.key === 'Escape') {
        closeContentEdit();
        closeContentView();
        closeContentDelete();
        closeNewDraft();
    }
    if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
        e.preventDefault();
        document.getElementById('contentSearch').focus();
    }
});

cRender();