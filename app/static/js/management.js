console.log("management.js production loaded");

function currentTime() {
    return new Date().toLocaleTimeString([], {
        hour: "2-digit",
        minute: "2-digit"
    });
}

/* ================= API LAYER ================= */
const API = {
    branches: "/management/api/branches",
    rooms: "/management/api/rooms",
    educators: "/management/api/educators",
    assign: "/management/api/assign",
    attendance: "/management/api/attendance",
    children: "/management/api/children",
    childAssign: "/management/api/child-assign"
};

/* ================= STATE ================= */
const STATE = {
    branches: [],
    rooms: [],
    educators: [],
    assignments: [],
    children: []
};

/* ================= INIT ================= */
document.addEventListener("DOMContentLoaded", async () => {

    bindUI();

    await refreshAll();

    setInterval(loadEducators, 10000);

    const currentDate = document.getElementById("currentDate");

    if (currentDate) {
        currentDate.textContent =
            new Date().toLocaleDateString("en-IE", {
                weekday: "long",
                day: "numeric",
                month: "long",
                year: "numeric"
            });
    }
});

document.addEventListener("click", (e) => {

    const modal = e.target.closest(".modal");

    if (modal && e.target === modal) {
        closeAllModals();
    }
});

document.addEventListener("keydown", (e) => {

    if (e.key === "Escape") {
        closeAllModals();
    }
});

/* ================= MODAL SYSTEM ================= */
function openModal(id) {

    const modal = document.getElementById(id);

    if (modal) {
        modal.classList.remove("hidden");
    }
}

function closeAllModals() {

    document.querySelectorAll(".modal").forEach(m => {
        m.classList.add("hidden");
    });
}

/* ================= UI BINDINGS ================= */
function bindUI() {

    document.querySelectorAll("[data-modal]").forEach(btn => {

        btn.addEventListener("click", () => {

            closeAllModals();

            const modalId = btn.dataset.modal;

            if (modalId === "educatorModal") {
                resetEducatorForm();
            }

            openModal(modalId);
        });
    });
    document.getElementById("assignBranch").addEventListener("change", onBranchChange);

    const childAssignBranch =
        document.getElementById("childAssignBranch");

    if (childAssignBranch) {
        childAssignBranch.addEventListener(
            "change",
            filterChildRoomsByBranch
        );
    }

    const branchForm = document.getElementById("branchForm");

    if (branchForm) {
        branchForm.addEventListener("submit", saveBranch);
    }

    const roomForm = document.getElementById("roomForm");

    if (roomForm) {
        roomForm.addEventListener("submit", saveRoom);
    }

    const educatorForm =
        document.getElementById("educatorForm");

    if (educatorForm) {
        educatorForm.addEventListener(
            "submit",
            saveEducator
        );
    }

    const btnSaveAttendance =
        document.getElementById("btnSaveAttendance");

    if (btnSaveAttendance) {
        btnSaveAttendance.addEventListener(
            "click",
            saveAttendance
        );
    }

    const btnSaveAssignment =
        document.getElementById("btnSaveAssignment");

    if (btnSaveAssignment) {
        btnSaveAssignment.addEventListener(
            "click",
            saveAssignment
        );
    }

    const btnSaveChildRooms =
        document.getElementById("btnSaveChildRooms");

    if (btnSaveChildRooms) {
        btnSaveChildRooms.addEventListener(
            "click",
            saveChildAssignment
        );
    }

    const showChildrenBtn =
        document.getElementById("showChildrenBtn");

    if (showChildrenBtn) {
        showChildrenBtn.addEventListener(
            "click",
            showChildrenTable
        );
    }

    const showPersonnelBtn =
        document.getElementById("showPersonnelBtn");

    if (showPersonnelBtn) {
        showPersonnelBtn.addEventListener(
            "click",
            showPersonnelTable
        );
    }
}

/* ================= REFRESH ================= */
async function refreshAll() {

    await Promise.allSettled([
        loadBranches(),
        loadRooms(),
        loadEducators(),
        loadChildren()
    ]);

    renderBranches();
    renderRooms();
    renderEducators();
    renderChildren();

    fillDropdowns();
    renderStats();
}

/* ================= BRANCH ================= */

function getRoomsByBranch(branchId) {

    if (!branchId) return [];

    return STATE.rooms.filter(r =>
        String(r.branch_id) === String(branchId)
    );
}
async function loadBranches() {

    STATE.branches =
        await fetch(API.branches).then(r => r.json());
}

async function saveBranch(e) {

    e.preventDefault();

    const res = await fetch(API.branches, {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            name: document.getElementById("branchName").value
        })
    });

    const result = await res.json();

    if (!res.ok || !result.success) {
        alert("Failed to save branch");
        return;
    }

    e.target.reset();

    closeAllModals();

    await refreshAll();
}

/* ================= ROOM ================= */
// async function loadRooms() {

//     const data =
//         await fetch(API.rooms).then(r => r.json());

//     STATE.rooms = data.map(r => ({
//         id: r.room_id || r.id,
//         name: r.name || r.room_name,
//         branch_id: r.branch_id
//     }));
// }
// async function loadRooms() {
//     const res = await fetch(API.rooms);
//     const text = await res.text();
//     console.log("ROOMS RAW:", text);
    
//     try {
//         const data = JSON.parse(text);
//         STATE.rooms = data.map(r => ({
//             id: r.room_id || r.id,
//             name: r.name || r.room_name,
//             branch_id: r.branch_id
//         }));
//     } catch (e) {
//         console.error("Rooms parse failed:", e);
//     }
// }
async function loadRooms() {
    const res = await fetch(API.rooms);
    const text = await res.text();
    console.log("ROOMS RAW:", text);

    if (!res.ok) {
        console.error("Rooms API failed with status", res.status);
        // optional: show alert or toast here using the JSON message if present
        try {
            const err = JSON.parse(text);
            console.error("Rooms API error:", err.message);
        } catch (_) {
            // text was HTML or something else
        }
        STATE.rooms = [];
        return;
    }

    try {
        const data = JSON.parse(text);
        STATE.rooms = data.map(r => ({
            id: r.room_id || r.id,
            name: r.name || r.room_name,
            branch_id: r.branch_id
        }));
    } catch (e) {
        console.error("Rooms parse failed:", e);
        STATE.rooms = [];
    }
}

async function saveRoom(e) {

    e.preventDefault();

    await fetch(API.rooms, {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            branch_id:
                document.getElementById("roomBranch").value,
            name:
                document.getElementById("roomName").value,
            capacity:
                document.getElementById("roomCapacity").value,
            type: 
                document.getElementById("roomType").value
        })
    });

    e.target.reset();

    closeAllModals();

    await refreshAll();
}

/* ================= EDUCATORS ================= */
async function loadEducators() {

    STATE.educators =
        await fetch(API.educators).then(r => r.json());
}

function renderEducators() {

    const table =
        document.getElementById("educatorTable");

    if (!table) return;

    table.innerHTML = STATE.educators.map(e => `
        <tr>
            <td>${e.name || "-"}</td>
            <td>${e.role || "-"}</td>
            <td>${e.status || "-"}</td>
            <td>${e.rooms || "-"}</td>
            <td>${e.start_date || "-"}</td>
            <td>${e.end_date || "-"}</td>

            <td>
                <button
                    class="btn-primary btn-sm"
                    onclick="editEducator(${e.id})">

                    Edit

                </button>

                <button
                    class="btn-secondary btn-sm"
                    onclick="editAssignment(${e.id})">

                    Rooms

                </button>
            </td>
        </tr>
    `).join("");
}

function editEducator(id) {

    const educator =
        STATE.educators.find(e => e.id == id);

    if (!educator) return;

    document.getElementById("educatorId").value =
        educator.id;

    document.getElementById("educatorName").value =
        educator.name || "";

    document.getElementById("educatorPhone").value =
        educator.phone || "";

    document.getElementById("educatorEmail").value =
        educator.email || "";

    document.getElementById("educatorRole").value =
        educator.role || "educator";

    document.getElementById("educatorStartDate").value =
        educator.start_date || "";

    document.getElementById("educatorEndDate").value =
        educator.end_date || "";

    openModal("educatorModal");
}

function editAssignment(educatorId) {

    const educator =
        STATE.educators.find(e => e.id == educatorId);

    if (!educator) return;

    // SET EDUCATOR
    document.getElementById("assignEducator").value =
        educator.id;

    const branchSelect =
        document.getElementById("assignBranch");

    const roomSelect =
        document.getElementById("assignRoom");

    // RESET DEFAULTS
    branchSelect.value = "";

    roomSelect.innerHTML = `
        <option value="">
            Select Room
        </option>
    `;

    // OPEN MODAL
    openModal("assignroomModal");

    // NO EXISTING ROOM ASSIGNMENTS
    if (
        !educator.room_ids ||
        educator.room_ids.length === 0
    ) {
        return;
    }

    // FIND FIRST ACTIVE ROOM
    const firstRoom = STATE.rooms.find(r =>
        educator.room_ids.includes(r.id)
    );

    if (!firstRoom) return;

    // AUTO-SELECT BRANCH
    branchSelect.value = firstRoom.branch_id;

    // LOAD ROOMS FOR THAT BRANCH
    const filteredRooms = STATE.rooms.filter(r =>
        String(r.branch_id) === String(firstRoom.branch_id)
    );

    // BUILD ROOM OPTIONS
    roomSelect.innerHTML = filteredRooms.map(r => `

        <option
            value="${r.id}"
            ${educator.room_ids.includes(r.id)
                ? "selected"
                : ""}>

            ${r.name}

        </option>

    `).join("");
}

async function saveEducator(e) {

    e.preventDefault();

    const id =
        document.getElementById("educatorId").value;

    const payload = {
        name:
            document.getElementById("educatorName").value,
        phone:
            document.getElementById("educatorPhone").value,
        email:
            document.getElementById("educatorEmail").value,
        role:
            document.getElementById("educatorRole").value,
        start_date:
            document.getElementById("educatorStartDate").value,
        end_date:
            document.getElementById("educatorEndDate").value
    };

    const method = id ? "PUT" : "POST";

    if (id) {
        payload.id = id;
    }

    await fetch(API.educators, {
        method,
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify(payload)
    });

    e.target.reset();

    document.getElementById("educatorId").value = "";

    closeAllModals();

    await refreshAll();
}

function resetEducatorForm() {

    const form =
        document.getElementById("educatorForm");

    if (form) {
        form.reset();
    }

    document.getElementById("educatorId").value = "";
}

/* ================= CHILDREN ================= */
async function loadChildren() {

    try {

        const res = await fetch(API.children);

        if (!res.ok) {

            console.warn(
                "Children API failed:",
                res.status
            );

            STATE.children = [];

            return;
        }

        STATE.children = await res.json();

    } catch (err) {

        console.error(
            "Children load error:",
            err
        );

        STATE.children = [];
    }
}

function renderChildren() {

    const table = document.getElementById("childTable");
    if (!table) return;

    table.innerHTML = STATE.children.map(c => {

        // 🔥 NORMALISE ID (CRITICAL FIX)
        const childId = c.child_id ?? c.id ?? null;

        return `
        <tr>
            <td>${c.first_name || "-"}</td>
            <td>${c.last_name || "-"}</td>
            <td>${c.assigned_room || "-"}</td>
            <td>${c.contract_type || "-"}</td>
            <td>${c.contract_status || "-"}</td>
            <td>${c.date_of_birth || "-"}</td>
            <td>${c.household || "-"}</td>
            <td>${c.parent || "-"}</td>
            <td>${c.phone || "-"}</td>

            <td>
                <button
                    class="btn-primary btn-sm"
                    ${childId ? `onclick="openChildRoomModal(${childId})"` : "disabled"}
                >
                    Room
                </button>
            </td>
        </tr>`;
    }).join("");
}

/* ================= CHILD ROOM ASSIGNMENT ================= */

function openChildRoomModal(childId) {

    if (!childId) {
        console.error(
            "openChildRoomModal received invalid childId:",
            childId
        );
        return;
    }

    const child = STATE.children.find(c =>
        (c.child_id ?? c.id) == childId
    );

    if (!child) {
        console.error("Child not found:", childId);
        return;
    }

    // =========================
    // STORE CHILD ID
    // =========================
    document.getElementById("childAssignChild").value =
        childId;

    // =========================
    // LABEL
    // =========================
    document.getElementById(
        "childRoomNameLabel"
    ).innerText =
        `${child.first_name} ${child.last_name}`;

    // =========================
    // ELEMENTS
    // =========================
    const branchSelect =
        document.getElementById("childAssignBranch");

    const roomSelect =
        document.getElementById("childAssignRoom");

    // =========================
    // RESET DROPDOWNS
    // =========================
    branchSelect.innerHTML =
        `<option value="">Select Branch</option>` +
        STATE.branches.map(b => `
            <option value="${b.id}">
                ${b.name}
            </option>
        `).join("");

    roomSelect.innerHTML =
        `<option value="">Select Branch First</option>`;

    // =========================
    // OPEN MODAL
    // =========================
    openModal("childRoomModal");

    // =========================
    // LOAD CURRENT ROOM
    // =========================
    fetch(`/management/api/child-assign/${childId}`)
        .then(r => r.json())
        .then(data => {

            console.log("CHILD ROOM DATA:", data);

            // NO ROOM ASSIGNED
            if (!data || data.length === 0) {
                return;
            }

            // LATEST ROOM
            const latestRoomId =
                data[0].room_id;

            // FIND ROOM
            const room = STATE.rooms.find(r =>
                String(r.id) === String(latestRoomId)
            );

            if (!room) {
                console.warn(
                    "Room not found in STATE.rooms"
                );
                return;
            }

            // =========================
            // SELECT BRANCH
            // =========================
            branchSelect.value =
                room.branch_id;

            // =========================
            // LOAD ROOMS FOR BRANCH
            // =========================
            const filteredRooms =
                STATE.rooms.filter(r =>
                    String(r.branch_id) ===
                    String(room.branch_id)
                );

            roomSelect.innerHTML =
                filteredRooms.map(r => `
                    <option value="${r.id}">
                        ${r.name}
                    </option>
                `).join("");

            // =========================
            // SELECT ROOM
            // =========================
            roomSelect.value =
                latestRoomId;

        })
        .catch(err => {

            console.error(
                "Failed loading child rooms:",
                err
            );

        });
}

function filterChildRoomsByBranch() {

    const branchId =
        document.getElementById("childAssignBranch").value;

    const roomDropdown =
        document.getElementById("childAssignRoom");

    const filtered = STATE.rooms.filter(r =>
        String(r.branch_id) === String(branchId)
    );

    roomDropdown.innerHTML = filtered.map(r => `
        <option value="${r.id}">
            ${r.name}
        </option>
    `).join("");
}

async function saveChildAssignment() {

    const childId = document.getElementById("childAssignChild")?.value;

    if (!childId || childId === "undefined") {
        console.error("Invalid childId - aborting save");
        return;
    }

    const roomIds = Array.from(
        document.getElementById("childAssignRoom").selectedOptions
    ).map(o => parseInt(o.value));

    await fetch("/management/api/child-assign", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            child_id: parseInt(childId),
            room_ids: roomIds
        })
    });

    closeAllModals();
    await refreshAll();
}

/* ================= ATTENDANCE ================= */
async function saveAttendance() {

    await fetch(API.attendance, {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            educator_id:
                document.getElementById("attEducator").value,
            date:
                document.getElementById("attDate").value,
            clock_in:
                document.getElementById("attIn").value,
            clock_out:
                document.getElementById("attOut").value
        })
    });

    closeAllModals();
}

/* ================= ASSIGNMENT ================= */
async function saveAssignment() {

    const educatorId = parseInt(document.getElementById("assignEducator").value);
    const roomIds = Array.from(
        document.getElementById("assignRoom").selectedOptions
    ).map(o => parseInt(o.value));

    console.log("educator_id:", educatorId);
    console.log("room_ids:", roomIds);

    if (!educatorId) {
        alert("No educator selected");
        return;
    }

    if (roomIds.length === 0) {
        alert("No room selected");
        return;
    }

    const res = await fetch(API.assign, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            educator_id: educatorId,
            room_ids: roomIds
        })
    });
    
    // guard against non-JSON error responses
    const result = res.headers.get("content-type")?.includes("application/json")
        ? await res.json()
        : { success: false, message: await res.text() };
    
    console.log("assign result:", result);
    
    if (!result.success) {
        alert("Failed to assign room: " + result.message);
        return;
    }
    // const res = await fetch(API.assign, {
    //     method: "POST",
    //     headers: { "Content-Type": "application/json" },
    //     body: JSON.stringify({
    //         educator_id: educatorId,
    //         room_ids: roomIds
    //     })
    // });

    // const result = await res.json();
    // console.log("assign result:", result);

    closeAllModals();
    await refreshAll();
}
// async function saveAssignment() {

//     await fetch(API.assign, {
//         method: "POST",
//         headers: {
//             "Content-Type": "application/json"
//         },
//         body: JSON.stringify({
//             educator_id:
//                 // document.getElementById("assignEducator").value,
//                 parseInt(document.getElementById("assignEducator").value),

//             room_ids: Array.from(
//                 document.getElementById("assignRoom")
//                     .selectedOptions
//             ).map(o => parseInt(o.value))
//         })
//     });

//     closeAllModals();

//     await refreshAll();
// }

/* ================= DROPDOWNS ================= */
function fillDropdowns() {

    const assignBranch =
        document.getElementById("assignBranch");

    if (assignBranch) {

        assignBranch.innerHTML =
            `<option value="">Select Branch</option>` +
            STATE.branches.map(b => `
                <option value="${b.id}">
                    ${b.name}
                </option>
            `).join("");
    }

    const roomBranch =
        document.getElementById("roomBranch");

    if (roomBranch) {

        roomBranch.innerHTML =
            STATE.branches.map(b => `
                <option value="${b.id}">
                    ${b.name}
                </option>
            `).join("");
    }

    const attEducator =
        document.getElementById("attEducator");

    if (attEducator) {

        attEducator.innerHTML =
            STATE.educators.map(e => `
                <option value="${e.id}">
                    ${e.name}
                </option>
            `).join("");
    }

    const assignEducator =
        document.getElementById("assignEducator");

    if (assignEducator) {

        assignEducator.innerHTML =
            STATE.educators.map(e => `
                <option value="${e.id}">
                    ${e.name}
                </option>
            `).join("");
    }

    const assignRoom =
        document.getElementById("assignRoom");

    if (assignRoom) {

        assignRoom.innerHTML =
            // `<option>Select Branch First</option>`;
            '<option value="">Select Room</option>';
    }

    const childAssignBranch =
        document.getElementById("childAssignBranch");

    if (childAssignBranch) {

        childAssignBranch.innerHTML =
            `<option value="">Select Branch</option>` +
            STATE.branches.map(b => `
                <option value="${b.id}">
                    ${b.name}
                </option>
            `).join("");
    }
}

/* ================= TABLES ================= */
function renderBranches() {

    const branchList =
        document.getElementById("branchList");

    if (!branchList) return;

    branchList.innerHTML =
        STATE.branches.map(b => `
            <option value="${b.id}">
                ${b.name}
            </option>
        `).join("");
}

// function renderRoomsByBranch(branchId) {

//     const roomList = document.getElementById("roomList");

//     if (!branchId) {
//         roomList.innerHTML = `<option value="">Select Branch First</option>`;
//         return;
//     }

//     const filtered = STATE.rooms.filter(r =>
//         String(r.branch_id) === String(branchId)
//     );

//     roomList.innerHTML = filtered.length
//         ? filtered.map(r => `
//             <option value="${r.id}">
//                 ${r.name}
//             </option>
//         `).join("")
//         : `<option value="">No rooms in this branch</option>`;
// }

function onBranchChange(e) {

    const branchId = e.target.value;

    const roomSelect =
        document.getElementById("assignRoom");

    if (!roomSelect) return;

    if (!branchId) {
        roomSelect.innerHTML = `<option value="">Select Room</option>`;
        return;
    }

    const filteredRooms = STATE.rooms.filter(r =>
        String(r.branch_id) === String(branchId)
    );

    roomSelect.innerHTML = filteredRooms.length
        ? filteredRooms.map(r => `
            <option value="${r.id}">
                ${r.name}
            </option>
        `).join("")
        : `<option value="">No Rooms Found</option>`;
}
// function onBranchChange(e) {

//     const branchId = e.target.value;

//     const roomSelect =
//         document.getElementById("assignRoom");

//     if (!roomSelect) return;

//     // RESET
//     if (!branchId) {

//         roomSelect.innerHTML = `
//             <option value="">
//                 Select Room
//             </option>
//         `;

//         return;
//     }

//     // FILTER ROOMS
//     const filteredRooms = STATE.rooms.filter(r =>
//         String(r.branch_id) === String(branchId)
//     );

//     roomSelect.innerHTML = filteredRooms.length
//         ? filteredRooms.map(r => `
//             <option value="${r.id}">
//                 ${r.name}
//             </option>
//         `).join("")
//         : `
//             <option value="">
//                 No Rooms Found
//             </option>
//         `;
//     renderRoomsByBranch(branchId);
// }

function renderRooms() {

    const roomList =
        document.getElementById("roomList");

    if (!roomList) return;

    roomList.innerHTML =
        STATE.rooms.map(r => `
            <option value="${r.id}">
                ${r.name}
            </option>
        `).join("");
}

/* ================= STATS ================= */
function renderStats() {

    const branchCount =
        document.getElementById("branchCount");

    if (branchCount) {
        branchCount.innerText =
            STATE.branches.length;
    }

    const roomCount =
        document.getElementById("roomCount");

    if (roomCount) {
        roomCount.innerText =
            STATE.rooms.length;
    }

    const educatorCount =
        document.getElementById("educatorCount");

    if (educatorCount) {
        educatorCount.innerText =
            STATE.educators.length;
    }
    
    const childCount = document.getElementById("childCount");
    if (childCount) {
        childCount.innerText = STATE.children.length;
    }
}

/* ================= VIEW TOGGLES ================= */
function showChildrenTable() {

    const personnel =
        document.getElementById("personnelTableCard");

    const children =
        document.getElementById("childTableCard");

    if (personnel) {
        personnel.classList.add("hidden");
    }

    if (children) {
        children.classList.remove("hidden");
    }
}

function showPersonnelTable() {

    const personnel =
        document.getElementById("personnelTableCard");

    const children =
        document.getElementById("childTableCard");

    if (children) {
        children.classList.add("hidden");
    }

    if (personnel) {
        personnel.classList.remove("hidden");
    }
}

// === BRANCH ↔ ROOM LINK ===
// when user changes branch in visible Branches dropdown, update Room list accordingly
document.addEventListener("DOMContentLoaded", () => {
    const branchList = document.getElementById("branchList");
    if (branchList) {
        branchList.addEventListener("change", (e) => {
            const branchId = e.target.value;
            const roomList = document.getElementById("roomList");
            if (!roomList || !STATE.rooms.length) return;

            const filtered = STATE.rooms.filter(
                r => String(r.branch_id) === String(branchId)
            );

            roomList.innerHTML = filtered.length
                ? filtered.map(r => `<option value="${r.id}">${r.name}</option>`).join("")
                : `<option value="">No rooms in this branch</option>`;
        });
    }
});
