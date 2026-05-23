console.log("Attendance JS loaded successfully");

// ===============================
// Global State
// ===============================
let children = [];              // Raw data from API for current date
let attendanceState = [];       // Editable state (what we will save)
let originalAttendanceState = [];// Snapshot for dirty detection (if needed)
let renderedChildren = [];      // Last rendered subset (for saving by room/filter)

let activeEducatorId = null;
let activeRoomId = null;

// ===============================
// Helpers
// ===============================
function initials(name) {
    return (name || "")
        .split(" ")
        .map(x => x[0])
        .join("")
        .substring(0, 2)
        .toUpperCase();
}

function currentTime() {
    const d = new Date();
    const hh = String(d.getHours()).padStart(2, "0");
    const mm = String(d.getMinutes()).padStart(2, "0");
    return `${hh}:${mm}`;
}

// ===============================
// State Updaters
// ===============================
function updateStatus(childId, value) {
    const child = attendanceState.find(c => c.child_id == childId);
    if (child) {
        child.status = value;
    }
}

function updateField(childId, field, value) {
    const child = attendanceState.find(c => c.child_id == childId);
    if (!child) return;
    child[field] = value;
}

function updateNotes(childId, value) {
    updateField(childId, "notes", value);
}

// ===============================
// Educator Lock (read-only vs editable)
// ===============================
function applyEducatorLock() {
    const locked = !activeEducatorId;

    document.querySelectorAll(
        ".attendance-status, .time-input, .pickup-input, .notes-input"
    ).forEach(el => {
        el.disabled = locked;
    });

    const btn = document.getElementById("saveRegisterBtn");
    if (btn) btn.disabled = locked;
}

// ===============================
// Load Attendance from API
// ===============================
async function loadAttendance() {
    const dateInput = document.getElementById("attendanceDate");
    if (!dateInput) return;

    const date = dateInput.value;
    if (!date) return;

    try {
        const res = await fetch(`/api/attendance?date=${date}`);
        const data = await res.json();

        children = (data || []).map(c => ({
            ...c,
            status: c.status ?? "Present",
            parents: c.parents ?? []
        }));

        attendanceState = structuredClone(children);
        originalAttendanceState = structuredClone(children);

        // Respect current room filter if any
        renderTable("", activeRoomId);
    } catch (err) {
        console.error("Error loading attendance:", err);
    }
}

// ===============================
// Render Table (filter + search)
// ===============================
function renderTable(filter = "", roomId = null) {

    if (!Array.isArray(children)) {
        children = [];
    }

    let filtered = [...children];

    // Room filter
    if (roomId) {
        filtered = filtered.filter(c => c.room_id == roomId);
    }

    // Search filter
    if (typeof filter === "string" && filter.trim()) {
        const term = filter.toLowerCase();
        filtered = filtered.filter(child =>
            (child.child_name || "").toLowerCase().includes(term)
        );
    }

    renderChildren(filtered);
    updateStats(filtered);
}

// ===============================
// Render Attendance Rows
// ===============================
function renderChildren(list) {
    renderedChildren = [...list];

    const tbody = document.getElementById("attendanceTable");
    if (!tbody) return;

    if (!list || !list.length) {
        tbody.innerHTML = `
            <tr>
                <td colspan="7" class="empty-row">
                    No Children Found
                </td>
            </tr>
        `;
        applyEducatorLock();
        return;
    }

    tbody.innerHTML = list.map(child => `
        <tr>
            <td>
                <div class="child-cell">
                    <div class="child-avatar">
                        ${(child.child_name || "?").charAt(0).toUpperCase()}
                    </div>
                    <div>
                        <div class="child-name">${child.child_name || "-"}</div>
                        <small class="text-muted">${child.age_group || ""}</small>
                    </div>
                </div>
            </td>

            <td>${child.room_name || "-"}</td>

            <td>
                <select
                    class="attendance-status"
                    onchange="updateStatus(${child.child_id}, this.value)">
                    <option value="Present"  ${child.status === "Present" ? "selected" : ""}>Present</option>
                    <option value="Absent"   ${child.status === "Absent" ? "selected" : ""}>Absent</option>
                    <option value="Late"     ${child.status === "Late" ? "selected" : ""}>Late</option>
                </select>
            </td>

            <td>
                <input
                    type="time"
                    class="time-input"
                    value="${child.check_in_time || ""}"
                    onchange="updateField(${child.child_id}, 'check_in_time', this.value)">
            </td>

            <td>
                <input
                    type="time"
                    class="time-input"
                    value="${child.check_out_time || ""}"
                    onchange="updateField(${child.child_id}, 'check_out_time', this.value)">
            </td>

            <td>
                <select
                    class="pickup-input"
                    onchange="updateField(${child.child_id}, 'pickup_by_parent_id', this.value)">
                    <option value="">...</option>
                    ${(child.parents || []).map(p => `
                        <option
                            value="${p.parent_id}"
                            ${child.pickup_by_parent_id == p.parent_id ? "selected" : ""}>
                            ${p.name}
                        </option>
                    `).join("")}
                </select>
            </td>

            <td>
                <input
                    type="text"
                    class="notes-input"
                    placeholder="Notes"
                    value="${child.notes || ""}"
                    onchange="updateNotes(${child.child_id}, this.value)">
            </td>
        </tr>
    `).join("");

    applyEducatorLock();
}

// ===============================
// Optional: Local Check-In / Check-Out Helpers
// (All changes are persisted through save-register)
// ===============================
function checkInChild(childId) {
    const child = attendanceState.find(c => c.child_id == childId);
    if (!child) return;
    child.status = "Present";
    if (!child.check_in_time) {
        child.check_in_time = currentTime();
    }
    renderTable("", activeRoomId);
}

function checkOutChild(childId) {
    const child = attendanceState.find(c => c.child_id == childId);
    if (!child) return;
    child.check_out_time = currentTime();
    child.status = "Picked Up";
    renderTable("", activeRoomId);
}

// ===============================
// Dirty Row Detection (if you want it)
// ===============================
function isRowDirty(index) {
    const original = originalAttendanceState[index];
    const current = attendanceState[index];
    return JSON.stringify(original) !== JSON.stringify(current);
}

function getDirtyRows() {
    return attendanceState.filter((row, i) => isRowDirty(i));
}

// ===============================
// Stats
// ===============================
function updateStats(filteredList = []) {

    const total = filteredList.length;

    const checkedIn = filteredList.filter(c =>
        c.check_in_time &&
        c.check_in_time.toString().trim() !== ""
    ).length;

    const checkedOut = filteredList.filter(c =>
        c.check_out_time &&
        c.check_out_time.toString().trim() !== ""
    ).length;

    const totalEl =
        document.getElementById("totalChildren");

    const inEl =
        document.getElementById("checkedInCount");

    const outEl =
        document.getElementById("checkedOutCount");

    if (totalEl) {
        totalEl.textContent = total;
    }

    if (inEl) {
        inEl.textContent = checkedIn;
    }

    if (outEl) {
        outEl.textContent = checkedOut;
    }
}

// ===============================
// DOM Ready
// ===============================
document.addEventListener("DOMContentLoaded", () => {

    const today = new Date().toISOString().split("T")[0];
    const dateInput = document.getElementById("attendanceDate");
    if (dateInput) {
        dateInput.value = today;
        dateInput.addEventListener("change", loadAttendance);
    }

    // Initial load
    loadAttendance();
    loadEducators();
    loadSessionEducators();

    // Search
    const searchInput = document.getElementById("searchInput");
    if (searchInput) {
        searchInput.addEventListener("input", function () {
            renderTable(this.value, activeRoomId);
        });
    }

    // Modal open
    document.addEventListener("click", function (e) {
        const btn = e.target.closest("[data-modal]");
        if (!btn) return;

        const modalId = btn.getAttribute("data-modal");
        const modal = document.getElementById(modalId);

        if (modal) {
            modal.classList.remove("hidden");
        }
    });

    // Modal close (click outside)
    document.addEventListener("click", function (e) {
        if (e.target.classList.contains("modal")) {
            e.target.classList.add("hidden");
        }
    });

    // Date display
    const currentDateEl = document.getElementById("currentDate");
    if (currentDateEl) {
        currentDateEl.textContent = new Date().toLocaleDateString("en-IE", {
            weekday: "long",
            day: "numeric",
            month: "long",
            year: "numeric"
        });
    }

    // Session form (modal)
    const form = document.getElementById("sessionForm");
    if (form) {
        form.addEventListener("submit", async function (e) {
            e.preventDefault();

            const payload = {
                room_id: document.getElementById("sessionRoomId").value,
                educator_id: document.getElementById("sessionEducator").value,
                session_type: document.getElementById("sessionType").value,
                start_time: document.getElementById("startTime").value,
                end_time: document.getElementById("endTime").value
            };

            try {
                const res = await fetch("/api/attendance/sessions", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify(payload)
                });

                const data = await res.json();

                if (data.success) {
                    alert("Session saved successfully");
                    if (typeof closeModal === "function") {
                        closeModal("sessionsModal");
                    }
                } else {
                    alert(data.message || "Failed to save session");
                }
            } catch (err) {
                console.error("Session save failed:", err);
                alert("Failed to save session");
            }
        });
    }

    // Load Register Button
    const loadAttendanceBtn = document.getElementById("loadAttendanceBtn");
    if (loadAttendanceBtn) {
        loadAttendanceBtn.addEventListener("click", function () {
            const roomId = document.getElementById("attendanceRoomId")?.value || null;
            activeRoomId = roomId || null;
            renderTable("", activeRoomId);
        });
    }

    // Clear Button
    const clearBtn = document.getElementById("clearAttendanceBtn");
    if (clearBtn) {
        clearBtn.addEventListener("click", function () {

            activeEducatorId = null;
            activeRoomId = null;

            const ids = [
                "attendanceEducator",
                "attendanceRoom",
                "attendanceRoomId",
                "attendanceSession",
                "sessionId"
            ];
            ids.forEach(id => {
                const el = document.getElementById(id);
                if (el) el.value = "";
            });

            renderTable("", null);
            applyEducatorLock();
            loadAttendance();  // refresh data
        });
    }

    // Save Register Button
    const saveBtn = document.getElementById("saveRegisterBtn");
    if (saveBtn) {
        saveBtn.addEventListener("click", async () => {

            const cleanedChildren = renderedChildren
                .map(child => {
                    const state = attendanceState.find(a => a.child_id == child.child_id);
                    if (!state) return null;

                    return {
                        child_id: state.child_id,
                        status: state.status || "Present",
                        check_in_time: state.check_in_time || null,
                        check_out_time: state.check_out_time || null,
                        notes: state.notes || null,
                        pickup_by_parent_id: state.pickup_by_parent_id
                            ? parseInt(state.pickup_by_parent_id)
                            : null
                    };
                })
                .filter(Boolean);

            const payload = {
                attendance_date: document.getElementById("attendanceDate").value,
                room_id: document.getElementById("attendanceRoomId").value,
                educator_id: document.getElementById("attendanceEducator")?.value || null,
                session_id: document.getElementById("sessionId")?.value || null,
                children: cleanedChildren
            };

            console.log("Saving register:", payload);

            try {
                const res = await fetch("/api/attendance/save-register", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify(payload)
                });

                const data = await res.json();

                if (data.success) {
                    const now = new Date().toLocaleString();
                    const lastSavedEl = document.getElementById("lastSavedAt");
                    if (lastSavedEl) {
                        lastSavedEl.textContent = `Last saved at: ${now}`;
                    }

                    alert("Register saved successfully");

                    await loadAttendance();
                    renderTable("", activeRoomId);
                    requestAnimationFrame(applyEducatorLock);
                } else {
                    alert(data.message || "Save failed");
                }

            } catch (err) {
                console.error("Save register error:", err);
                alert("Server error while saving");
            }
        });
    }

    // Initial lock
    applyEducatorLock();
});

// ===============================
// Load Educators (main screen)
// ===============================
async function loadEducators() {
    try {
        const response = await fetch("/api/attendance/educators");
        const data = await response.json();

        const dropdown = document.getElementById("attendanceEducator");
        if (!dropdown) return;

        dropdown.innerHTML =
            `<option value="">Select Educator</option>` +
            data.map(e => `
                <option value="${e.id}">
                    ${e.name}
                </option>
            `).join("");
    } catch (error) {
        console.error("Educator load failed:", error);
    }
}

// ===============================
// Educator change: load room + session, filter + lock
// ===============================
document.getElementById("attendanceEducator")
    .addEventListener("change", async function () {

        activeEducatorId = this.value || null;
        activeRoomId = null;

        const roomField = document.getElementById("attendanceRoom");
        const roomIdField = document.getElementById("attendanceRoomId");
        const sessionField = document.getElementById("attendanceSession");
        const sessionIdField = document.getElementById("sessionId");

        if (!activeEducatorId) {
            if (roomField) roomField.value = "";
            if (roomIdField) roomIdField.value = "";
            if (sessionField) sessionField.value = "";
            if (sessionIdField) sessionIdField.value = "";

            renderTable("", null);
            applyEducatorLock();
            return;
        }

        try {
            // load room + session in parallel
            const [roomRes, sessionRes] = await Promise.all([
                fetch(`/api/attendance/room/${activeEducatorId}`),
                fetch(`/api/attendance/session/${activeEducatorId}`)
            ]);

            const roomText = await roomRes.text();
            const sessionText = await sessionRes.text();
            console.log("ROOM RAW:", roomText);
            console.log("SESSION RAW:", sessionText);
            
            const room = JSON.parse(roomText);
            const session = JSON.parse(sessionText);
            // const room = await roomRes.json();
            // const session = await sessionRes.json();

            if (room) {
                activeRoomId = room.id;
                if (roomField) roomField.value = room.name;
                if (roomIdField) roomIdField.value = room.id;
            }

            if (session) {
                if (sessionField) sessionField.value = session.session_type;
                if (sessionIdField) sessionIdField.value = session.session_id;
            }

            renderTable("", activeRoomId);
            requestAnimationFrame(applyEducatorLock);

        } catch (error) {
            console.error("Educator change failed:", error);
            renderTable("", null);
            applyEducatorLock();
        }
    });

// ===============================
// Load Session Educators (modal)
// ===============================
async function loadSessionEducators() {
    try {
        const res = await fetch("/management/api/educators");
        const data = await res.json();

        const dropdown = document.getElementById("sessionEducator");
        if (!dropdown) return;

        dropdown.innerHTML =
            `<option value="">Select Educator</option>` +
            data.map(e => `
                <option value="${e.id}">
                    ${e.name}
                </option>
            `).join("");
    } catch (error) {
        console.error("loadSessionEducators failed:", error);
    }
}

// ===============================
// Load Session Rooms (modal)
// ===============================
async function loadSessionRooms() {
    console.log("loadSessionRooms() called");

    try {
        const response = await fetch("/api/attendance/rooms");
        const text = await response.text();
        const data = JSON.parse(text);

        const dropdown = document.getElementById("sessionRoom");
        if (!dropdown) return;

        dropdown.innerHTML =
            `<option value="">Select Room</option>` +
            data.map(r => `
                <option value="${r.id}">
                    ${r.name}
                </option>
            `).join("");

    } catch (error) {
        console.error("loadSessionRooms failed:", error);
    }
}

// ===============================
// Modal Educator -> Room (modal)
// ===============================
document.getElementById("sessionEducator")
    .addEventListener("change", async function () {

        const educatorId = this.value;

        const roomField = document.getElementById("sessionRoom");
        const roomIdField = document.getElementById("sessionRoomId");

        if (roomField) roomField.value = "";
        if (roomIdField) roomIdField.value = "";

        if (!educatorId) return;

        try {
            const response = await fetch(`/api/attendance/room/${educatorId}`);
            const data = await response.json();

            if (data) {
                if (roomField) roomField.value = data.name;
                if (roomIdField) roomIdField.value = data.id;
            } else {
                if (roomField) roomField.value = "No room assigned";
            }

        } catch (error) {
            console.error("Room load failed:", error);
            if (roomField) roomField.value = "Error loading room";
        }
    });
