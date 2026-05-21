console.log("childsetup.js loaded");

document.addEventListener("DOMContentLoaded", () => {

    const API = "/children/api";

    const form = document.getElementById("childForm");
    const householdSelect = document.getElementById("householdSelect");
    const childContainer = document.getElementById("childContainer");
    const childTemplate = document.getElementById("childTemplate");
    const addChildBtn = document.getElementById("addChildBtn");
    const parentPreviewContainer = document.getElementById("parentPreviewContainer");
    const refreshChildrenBtn = document.getElementById("refreshChildrenBtn");
    const clearFormBtn = document.getElementById("clearFormBtn");

    let currentHouseholdId = null;
    let draftTimer = null;
    let householdParents = [];

    // ======================================================
    // RESET UI
    // ======================================================
    function resetUI() {

        currentHouseholdId = null;

        childContainer.innerHTML = "";

        addChildBtn.disabled = true;

        parentPreviewContainer.innerHTML =
            `<p class="text-muted">Select household...</p>`;

        householdSelect.value = "";
    }

    function enableUI() {
        addChildBtn.disabled = false;
    }

    // ======================================================
    // BUILD PAYLOAD
    // ======================================================
    function buildPayload() {

        const children = [
            ...childContainer.querySelectorAll(".child-card")
        ].map(card => ({

            // ==================================================
            // CHILD
            // ==================================================
            child_id:
                card.querySelector('[name="child_id[]"]')?.value || null,

            first_name:
                card.querySelector('[name="child_first_name[]"]')?.value || "",

            last_name:
                card.querySelector('[name="child_last_name[]"]')?.value || "",

            date_of_birth:
                card.querySelector('[name="date_of_birth[]"]')?.value || "",

            ppsn:
                card.querySelector('[name="ppsn[]"]')?.value || "",

            chick_code:
                card.querySelector('[name="chick_code[]"]')?.value || "",

            start_date:
                card.querySelector('[name="child_start_date[]"]')?.value || "",

            ecce_eligible:
                card.querySelector('[name="ecce_eligible[]"]')?.checked || false,

            // ==================================================
            // MEDICAL
            // ==================================================
            medical: {

                allergies:
                    card.querySelector('[name="allergies[]"]')?.value || "",

                medical_notes:
                    card.querySelector('[name="medical_notes[]"]')?.value || ""
            },

            // ==================================================
            // CONTRACT
            // ==================================================
            contract: {

                contract_id:
                    card.querySelector('[name="contract_id[]"]')?.value || null,

                type:
                    card.querySelector('[name="contract_type[]"]')?.value || "",

                start_date:
                    card.querySelector('[name="contract_start_date[]"]')?.value || "",

                end_date:
                    card.querySelector('[name="contract_end_date[]"]')?.value || "",

                hours_per_week:
                    card.querySelector('[name="agreed_hours_per_week[]"]')?.value || "",

                hourly_rate:
                    card.querySelector('[name="hourly_rate[]"]')?.value || "",

                subsidy_rate:
                    card.querySelector('[name="subsidy_rate[]"]')?.value || ""
            },

            // ==================================================
            // EMERGENCY CONTACTS
            // ==================================================
            emergency_contacts: [

                ...card.querySelectorAll(".emergency-card")

            ].map(ec => ({

                first_name:
                    ec.querySelector(".emergency-first-name")?.value || "",

                last_name:
                    ec.querySelector(".emergency-last-name")?.value || "",

                relationship:
                    ec.querySelector(".emergency-relationship")?.value || "",

                phone:
                    ec.querySelector(".emergency-phone")?.value || "",

                authorized_pickup:
                    ec.querySelector(".authorizedpickup")?.checked || false
            })),

            // ==================================================
            // RELATIONSHIPS
            // ==================================================
            relationships: [

                ...card.querySelectorAll(".relationship-card")

            ].map(rel => ({

                parent_id:
                    rel.querySelector(".relationship-parent")?.value || null,

                relationship:
                    rel.querySelector(".relationship-type")?.value || "",

                is_legal_guardian:
                    rel.querySelector(".legal-guardian")?.checked || false
            }))
        }));

        return {
            household_id: currentHouseholdId,
            children
        };
    }

    // ======================================================
    // AUTO SAVE
    // ======================================================
    function scheduleSave() {

        clearTimeout(draftTimer);

        draftTimer = setTimeout(saveDraft, 400);
    }

    function saveDraft() {

        if (!currentHouseholdId) return;

        localStorage.setItem(
            `child_draft_${currentHouseholdId}`,
            JSON.stringify(buildPayload())
        );
    }

    function loadDraft(id) {

        try {
            return JSON.parse(
                localStorage.getItem(`child_draft_${id}`)
            );
        }
        catch {
            return null;
        }
    }

    // ======================================================
    // ADD CHILD CARD
    // ======================================================
    function addChild(prefill = {}) {

        const card =
            childTemplate.content
                .cloneNode(true)
                .querySelector(".child-card");

        if (!card) return;

        // ==================================================
        // DEBUG
        // ==================================================
        console.log("Rendering child card");

        // ==================================================
        // IDS
        // ==================================================
        card.querySelector('[name="child_id[]"]').value =
            prefill.child_id || "";

        // ==================================================
        // HIDDEN CONTRACT ID
        // ==================================================
        const hidden = document.createElement("input");

        hidden.type = "hidden";
        hidden.name = "contract_id[]";
        hidden.value = prefill.contract?.contract_id || "";

        card.appendChild(hidden);

        // ==================================================
        // BASIC CHILD FIELDS
        // ==================================================
        card.querySelector('[name="child_first_name[]"]').value =
            prefill.first_name || "";

        card.querySelector('[name="child_last_name[]"]').value =
            prefill.last_name || "";

        card.querySelector('[name="date_of_birth[]"]').value =
            prefill.date_of_birth || "";

        card.querySelector('[name="ppsn[]"]').value =
            prefill.ppsn || "";

        card.querySelector('[name="chick_code[]"]').value =
            prefill.chick_code || "";

        card.querySelector('[name="child_start_date[]"]').value =
            prefill.start_date || "";

        card.querySelector('[name="ecce_eligible[]"]').checked =
            !!prefill.ecce_eligible;

        // ==================================================
        // MEDICAL
        // ==================================================
        card.querySelector('[name="allergies[]"]').value =
            prefill.medical?.allergies || "";

        card.querySelector('[name="medical_notes[]"]').value =
            prefill.medical?.medical_notes || "";

        // ==================================================
        // CONTRACT
        // ==================================================
        const c = prefill.contract || {};

        card.querySelector('[name="contract_type[]"]').value =
            c.type || "";

        card.querySelector('[name="contract_start_date[]"]').value =
            c.start_date || "";

        card.querySelector('[name="contract_end_date[]"]').value =
            c.end_date || "";

        card.querySelector('[name="agreed_hours_per_week[]"]').value =
            c.hours_per_week || "";

        card.querySelector('[name="hourly_rate[]"]').value =
            c.hourly_rate || "";

        card.querySelector('[name="subsidy_rate[]"]').value =
            c.subsidy_rate || "";

        // ==================================================
        // RELATIONSHIPS
        // ==================================================
        const relationshipContainer =
            card.querySelector(".parent-relationship-container");

        const relationshipTemplate =
            document.getElementById("relationshipTemplate");

        if (relationshipContainer && relationshipTemplate) {

            householdParents.forEach(parent => {

                const rel =
                    relationshipTemplate.content.cloneNode(true);

                const select =
                    rel.querySelector(".relationship-parent");

                select.innerHTML = `
                    <option value="${parent.parent_id}">
                        ${parent.first_name} ${parent.last_name}
                    </option>
                `;

                relationshipContainer.appendChild(rel);
            });
        }

        // ==================================================
        // EMERGENCY CONTACTS
        // ==================================================
        const emergencyContainer =
            card.querySelector(".emergency-contact-container");

        const emergencyTemplate =
            document.getElementById("emergencyContactTemplate");

        const addEmergencyBtn =
            card.querySelector(".add-emergency-contact");

        // PREFILL EXISTING EMERGENCY CONTACTS
        if (prefill.emergency_contacts?.length) {

            prefill.emergency_contacts.forEach(contact => {

                const clone =
                    emergencyTemplate.content.cloneNode(true);

                clone.querySelector(".emergency-first-name").value =
                    contact.first_name || "";

                clone.querySelector(".emergency-last-name").value =
                    contact.last_name || "";

                clone.querySelector(".emergency-relationship").value =
                    contact.relationship || "";

                clone.querySelector(".emergency-phone").value =
                    contact.phone || "";

                const pickup =
                    clone.querySelector(".authorizedpickup");

                if (pickup) {
                    pickup.checked =
                        !!contact.authorized_pickup;
                }

                clone.querySelector(".remove-emergency-contact")
                    ?.addEventListener("click", function () {

                        this.closest(".emergency-card")?.remove();

                        scheduleSave();
                    });

                emergencyContainer.appendChild(clone);
            });
        }

        // ADD EMERGENCY CONTACT
        addEmergencyBtn?.addEventListener("click", () => {

            if (!emergencyContainer || !emergencyTemplate) return;

            const count =
                emergencyContainer.querySelectorAll(".emergency-card").length;

            if (count >= 4) {

                alert("Maximum 4 emergency contacts allowed");

                return;
            }

            const clone =
                emergencyTemplate.content.cloneNode(true);

            clone.querySelector(".remove-emergency-contact")
                ?.addEventListener("click", function () {

                    this.closest(".emergency-card")?.remove();

                    scheduleSave();
                });

            emergencyContainer.appendChild(clone);

            scheduleSave();
        });

        // ==================================================
        // REMOVE CHILD
        // ==================================================
        card.querySelector(".remove-child")
            ?.addEventListener("click", () => {

                if (!confirm("Remove this child?")) return;

                if (
                    childContainer.querySelectorAll(".child-card").length === 1
                ) {
                    alert("At least one child required.");
                    return;
                }

                card.remove();

                scheduleSave();
            });

        // ==================================================
        // APPEND CARD
        // ==================================================
        childContainer.appendChild(card);
    }

    // ======================================================
    // LOAD HOUSEHOLD
    // ======================================================
    async function loadHousehold(id) {

        const res =
            await fetch(`${API}/household/${id}`);

        const data =
            await res.json();

        householdParents =
            data.parents || [];

        parentPreviewContainer.innerHTML =
            householdParents.length
                ? householdParents.map(p => `
                    <div>
                        <b>${p.first_name} ${p.last_name}</b>
                    </div>
                `).join("")
                : "No parents";

        const grouped = {};

        data.children.forEach(row => {

            if (!grouped[row.child_id]) {

                grouped[row.child_id] = {

                    ...row,

                    // medical: {
                    //     allergies: row.allergies || "",
                    //     medical_notes: row.medical_notes || ""
                    // },

                    medical: row.medical || {},
                        
                    contract: null
                };
            }

            if (row.contract_id) {

                grouped[row.child_id].contract = {

                    contract_id: row.contract_id,
                    type: row.contract_type,
                    start_date: row.contract_start_date,
                    end_date: row.end_date,
                    hours_per_week: row.agreed_hours_per_week,
                    hourly_rate: row.hourly_rate,
                    subsidy_rate: row.subsidy_rate
                };
            }
        });

        return Object.values(grouped);
    }

    // ======================================================
    // HOUSEHOLD CHANGE
    // ======================================================
    householdSelect.onchange = async (e) => {

        const id = e.target.value;

        if (!id) return resetUI();

        currentHouseholdId = id;

        enableUI();

        childContainer.innerHTML = "";

        const children =
            await loadHousehold(id);

        const draft =
            loadDraft(id);

        const hasDraft =
            draft?.children?.length;

        if (hasDraft) {

            draft.children.forEach(c => addChild(c));

        } else if (children.length) {

            children.forEach(c => addChild(c));

        } else {

            addChild();
        }
    };

    // ======================================================
    // EVENTS
    // ======================================================
    childContainer.addEventListener("input", scheduleSave);

    childContainer.addEventListener("change", scheduleSave);

    addChildBtn.onclick = () => addChild();

    // ======================================================
    // CLEAR FORM
    // ======================================================
    clearFormBtn?.addEventListener("click", () => {

        childContainer.innerHTML = "";

        if (currentHouseholdId) {
            addChild();
        }

        scheduleSave();
    });

    // ======================================================
    // REFRESH
    // ======================================================
    refreshChildrenBtn?.addEventListener("click", async () => {

        resetUI();

        const res =
            await fetch(`${API}/households`);

        const data =
            await res.json();

        householdSelect.innerHTML =
            `<option value="">Select</option>` +
            data.map(h => `
                <option value="${h.household_id}">
                    ${h.household_name}
                </option>
            `).join("");
    });

    // ======================================================
    // SAVE
    // ======================================================
    form.onsubmit = async (e) => {

        e.preventDefault();

        const res =
            await fetch(`${API}/child/setup`, {

                method: "POST",

                headers: {
                    "Content-Type": "application/json"
                },

                body: JSON.stringify(buildPayload())
            });

        const data =
            await res.json();

        if (!res.ok) {

            console.error("SERVER ERROR:", data);
            alert(data.error || "Save failed");

            return;
        }

        alert("Saved successfully!");

        localStorage.removeItem(
            `child_draft_${currentHouseholdId}`
        );

        householdSelect.dispatchEvent(
            new Event("change")
        );
    };

    // ======================================================
    // INIT
    // ======================================================
    resetUI();

    fetch(`${API}/households`)
        .then(r => r.json())
        .then(data => {

            householdSelect.innerHTML =
                `<option value="">Select</option>` +

                data.map(h => `
                    <option value="${h.household_id}">
                        ${h.household_name}
                    </option>
                `).join("");
        });
});

// console.log("childsetup.js loaded");

// document.addEventListener("DOMContentLoaded", () => {

//     const API = "/children/api";

//     const form = document.getElementById("childForm");
//     const householdSelect = document.getElementById("householdSelect");
//     const childContainer = document.getElementById("childContainer");
//     const childTemplate = document.getElementById("childTemplate");
//     const addChildBtn = document.getElementById("addChildBtn");
//     const parentPreviewContainer = document.getElementById("parentPreviewContainer");
//     const refreshChildrenBtn = document.getElementById("refreshChildrenBtn");
//     const clearFormBtn = document.getElementById("clearFormBtn");

//     let currentHouseholdId = null;
//     let draftTimer = null;
//     let householdParents = [];

//     // ======================================================
//     function resetUI() {
//         currentHouseholdId = null;
//         childContainer.innerHTML = "";
//         addChildBtn.disabled = true;
//         parentPreviewContainer.innerHTML = `<p class="text-muted">Select household...</p>`;
//         householdSelect.value = "";
//     }

//     function enableUI() {
//         addChildBtn.disabled = false;
//     }

//     // ======================================================
//     function buildPayload() {

//         const children = [...childContainer.querySelectorAll(".child-card")].map(card => ({

//             child_id: card.querySelector('[name="child_id[]"]')?.value || null,

//             first_name: card.querySelector('[name="child_first_name[]"]').value,
//             last_name: card.querySelector('[name="child_last_name[]"]').value,
//             date_of_birth: card.querySelector('[name="date_of_birth[]"]').value,
//             ppsn: card.querySelector('[name="ppsn[]"]').value,
//             chick_code: card.querySelector('[name="chick_code[]"]').value,
//             start_date: card.querySelector('[name="child_start_date[]"]').value,
//             ecce_eligible: card.querySelector('[name="ecce_eligible[]"]').checked,

//             // NEW: contracts
//             contract: {
//                 contract_id: card.querySelector('[name="contract_id[]"]')?.value || null,
//                 type: card.querySelector('[name="contract_type[]"]').value,
//                 start_date: card.querySelector('[name="contract_start_date[]"]').value,
//                 end_date: card.querySelector('[name="contract_end_date[]"]').value,
//                 hours_per_week: card.querySelector('[name="agreed_hours_per_week[]"]').value,
//                 hourly_rate: card.querySelector('[name="hourly_rate[]"]').value,
//                 subsidy_rate: card.querySelector('[name="subsidy_rate[]"]').value
//             },

//             // NEW: medical & safety
//             medical: {
//                 allergies: med.querySelector(".allergies")?.value || "",
//                 medical_note: med.querySelector(".medical-notes")?.value || "",
//             },

//             // NEW: emergency contacts
//             emergency_contacts: [...card.querySelectorAll(".emergency-card")].map(ec => ({
//                 first_name: ec.querySelector(".emergency-first-name")?.value || "",
//                 last_name: ec.querySelector(".emergency-last-name")?.value || "",
//                 relationship: ec.querySelector(".emergency-relationship")?.value || "",
//                 phone: ec.querySelector(".emergency-phone")?.value || "",
//                 authorized_pickup: ec.querySelector(".authorizedpickup")?.value || ""
//             })),

//             // NEW: relationships
//             relationships: [...card.querySelectorAll(".relationship-card")].map(rel => ({
//                 parent_id: rel.querySelector(".relationship-parent")?.value || null,
//                 relationship: rel.querySelector(".relationship-type")?.value || "",
//                 is_legal_guardian: rel.querySelector(".legal-guardian")?.checked || false
//             }))
//         }));

//         return { household_id: currentHouseholdId, children };
//     }

//     // ======================================================
//     function scheduleSave() {
//         clearTimeout(draftTimer);
//         draftTimer = setTimeout(saveDraft, 400);
//     }

//     function saveDraft() {
//         if (!currentHouseholdId) return;
//         localStorage.setItem(
//             `child_draft_${currentHouseholdId}`,
//             JSON.stringify(buildPayload())
//         );
//     }

//     function loadDraft(id) {
//         try {
//             return JSON.parse(localStorage.getItem(`child_draft_${id}`));
//         } catch {
//             return null;
//         }
//     }

//     // ======================================================
//     function addChild(prefill = {}) {
        
//         const card = childTemplate.content.cloneNode(true).querySelector(".child-card");

//         if (!card) return;

//         console.log("Template check:", {
//             relationship: !!card.querySelector(".parent-relationship-container"),
//             emergency: !!card.querySelector(".emergency-contact-container"),
//             addBtn: !!card.querySelector(".add-emergency-contact")
//         });

//         card.querySelector('[name="child_id[]"]').value = prefill.child_id || "";

//         // contract id
//         const hidden = document.createElement("input");
//         hidden.type = "hidden";
//         hidden.name = "contract_id[]";
//         hidden.value = prefill.contract?.contract_id || "";
//         card.appendChild(hidden);

//         // basic fields
//         card.querySelector('[name="child_first_name[]"]').value = prefill.first_name || "";
//         card.querySelector('[name="child_last_name[]"]').value = prefill.last_name || "";
//         card.querySelector('[name="date_of_birth[]"]').value = prefill.date_of_birth || "";
//         card.querySelector('[name="ppsn[]"]').value = prefill.ppsn || "";
//         card.querySelector('[name="chick_code[]"]').value = prefill.chick_code || "";
//         card.querySelector('[name="child_start_date[]"]').value = prefill.start_date || "";
//         card.querySelector('[name="ecce_eligible[]"]').checked = !!prefill.ecce_eligible;

//         // contract
//         const c = prefill.contract || {};
//         card.querySelector('[name="contract_type[]"]').value = c.type || "";
//         card.querySelector('[name="contract_start_date[]"]').value = c.start_date || "";
//         card.querySelector('[name="contract_end_date[]"]').value = c.end_date || "";
//         card.querySelector('[name="agreed_hours_per_week[]"]').value = c.hours_per_week || "";
//         card.querySelector('[name="hourly_rate[]"]').value = c.hourly_rate || "";
//         card.querySelector('[name="subsidy_rate[]"]').value = c.subsidy_rate || "";

//         // ======================================================
//         // RELATIONSHIPS (SAFE)
//         // ======================================================
//         const relationshipContainer = card.querySelector(".parent-relationship-container");
//         const relationshipTemplate = document.getElementById("relationshipTemplate");

//         if (relationshipContainer && relationshipTemplate) {

//             householdParents.forEach(parent => {
//                 const rel = relationshipTemplate.content.cloneNode(true);

//                 const select = rel.querySelector(".relationship-parent");

//                 select.innerHTML = `
//                     <option value="${parent.parent_id}">
//                         ${parent.first_name} ${parent.last_name}
//                     </option>
//                 `;

//                 relationshipContainer.appendChild(rel);
//             });
//         }

//         // ======================================================
//         // EMERGENCY CONTACTS (SAFE + LIMIT 4)
//         // ======================================================
//         const emergencyContainer = card.querySelector(".emergency-contact-container");
//         const emergencyTemplate = document.getElementById("emergencyContactTemplate");

//         const addEmergencyBtn = card.querySelector(".add-emergency-contact");

//         addEmergencyBtn?.addEventListener("click", () => {

//             if (!emergencyContainer || !emergencyTemplate) return;

//             const count = emergencyContainer.querySelectorAll(".emergency-card").length;

//             if (count >= 4) {
//                 alert("Maximum 4 emergency contacts allowed");
//                 return;
//             }

//             const clone = emergencyTemplate.content.cloneNode(true);

//             const removeBtn = clone.querySelector(".remove-emergency-contact");

//             removeBtn?.addEventListener("click", function () {
//                 this.closest(".emergency-card")?.remove();
//                 scheduleSave();
//             });

//             emergencyContainer.appendChild(clone);
//             scheduleSave();
//         });

//         // REMOVE CHILD
//         const removeBtn = card.querySelector(".remove-child");
//         removeBtn?.addEventListener("click", () => {
//             if (!confirm("Remove this child?")) return;
//             if (childContainer.querySelectorAll(".child-card").length === 1) {
//                 alert("At least one child required.");
//                 return;
//             }
//             card.remove();
//             scheduleSave();
//         });

//         childContainer.appendChild(card);
//     }

//     // ======================================================
//     async function loadHousehold(id) {

//         const res = await fetch(`${API}/household/${id}`);
//         const data = await res.json();

//         householdParents = data.parents || [];

//         parentPreviewContainer.innerHTML = householdParents.length
//             ? householdParents.map(p =>
//                 `<div><b>${p.first_name} ${p.last_name}</b></div>`
//             ).join("")
//             : "No parents";

//         const grouped = {};

//         data.children.forEach(row => {

//             if (!grouped[row.child_id]) {
//                 grouped[row.child_id] = {
//                     ...row,
//                     contract: null
//                 };
//             }

//             if (row.contract_id) {
//                 grouped[row.child_id].contract = {
//                     contract_id: row.contract_id,
//                     type: row.contract_type,
//                     start_date: row.contract_start_date,
//                     end_date: row.end_date,
//                     hours_per_week: row.agreed_hours_per_week,
//                     hourly_rate: row.hourly_rate,
//                     subsidy_rate: row.subsidy_rate
//                 };
//             }
//         });

//         return Object.values(grouped);
//     }

//     // ======================================================
//     householdSelect.onchange = async (e) => {

//         const id = e.target.value;

//         if (!id) return resetUI();

//         currentHouseholdId = id;

//         const children = await loadHousehold(id);

//         enableUI();
//         childContainer.innerHTML = "";

//         const draft = loadDraft(id);

//         const hasDraft = draft?.children?.length;

//         if (hasDraft) {
//             draft.children.forEach(c => addChild(c));
//         } else if (children.length) {
//             children.forEach(c => addChild(c));
//         } else {
//             addChild();
//         }
//     };

//     // ======================================================
//     childContainer.addEventListener("input", scheduleSave);
//     childContainer.addEventListener("change", scheduleSave);
//     addChildBtn.onclick = () => addChild();

//     // ======================================================
//     form.onsubmit = async (e) => {

//         e.preventDefault();

//         const res = await fetch(`${API}/child/setup`, {
//             method: "POST",
//             headers: { "Content-Type": "application/json" },
//             body: JSON.stringify(buildPayload())
//         });

//         const data = await res.json();

//         if (!res.ok) {
//             alert(data.error);
//             return;
//         }

//         alert("Saved successfully!");
//         localStorage.removeItem(`child_draft_${currentHouseholdId}`);

//         householdSelect.dispatchEvent(new Event("change"));
//     };

//     // INIT
//     resetUI();

//     fetch(`${API}/households`)
//         .then(r => r.json())
//         .then(data => {
//             householdSelect.innerHTML =
//                 `<option value="">Select</option>` +
//                 data.map(h =>
//                     `<option value="${h.household_id}">${h.household_name}</option>`
//                 ).join("");
//         });
// });
// console.log("child.js loaded");

// document.addEventListener("DOMContentLoaded", () => {

//     const API = "/children/api";

//     const form = document.getElementById("childForm");
//     const householdSelect = document.getElementById("householdSelect");
//     const childContainer = document.getElementById("childContainer");
//     const childTemplate = document.getElementById("childTemplate");
//     const addChildBtn = document.getElementById("addChildBtn");
//     const parentPreviewContainer = document.getElementById("parentPreviewContainer");
//     const refreshChildrenBtn = document.getElementById("refreshChildrenBtn");
//     const clearFormBtn = document.getElementById("clearFormBtn");

//     let currentHouseholdId = null;
//     let draftTimer = null;

//     // ======================================================
//     function resetUI() {
//         currentHouseholdId = null;
//         childContainer.innerHTML = "";
//         addChildBtn.disabled = true;
//         parentPreviewContainer.innerHTML =
//             `<p class="text-muted">Select household...</p>`;
//         householdSelect.value = "";
//     }

//     function enableUI() {
//         addChildBtn.disabled = false;
//     }

//     // ======================================================
//     function buildPayload() {

//         const children = [...childContainer.querySelectorAll(".child-card")].map(card => ({

//             child_id: card.querySelector('[name="child_id[]"]')?.value || null,

//             first_name: card.querySelector('[name="child_first_name[]"]').value,
//             last_name: card.querySelector('[name="child_last_name[]"]').value,
//             date_of_birth: card.querySelector('[name="date_of_birth[]"]').value,
//             ppsn: card.querySelector('[name="ppsn[]"]').value,
//             chick_code: card.querySelector('[name="chick_code[]"]').value,
//             start_date: card.querySelector('[name="child_start_date[]"]').value,
//             ecce_eligible: card.querySelector('[name="ecce_eligible[]"]').checked,

//             contract: {
//                 contract_id: card.querySelector('[name="contract_id[]"]')?.value || null,
//                 type: card.querySelector('[name="contract_type[]"]').value,
//                 start_date: card.querySelector('[name="contract_start_date[]"]').value,
//                 end_date: card.querySelector('[name="contract_end_date[]"]').value,
//                 hours_per_week: card.querySelector('[name="agreed_hours_per_week[]"]').value,
//                 hourly_rate: card.querySelector('[name="hourly_rate[]"]').value,
//                 subsidy_rate: card.querySelector('[name="subsidy_rate[]"]').value
//             }
//         }));

//         return { household_id: currentHouseholdId, children };
//     }

//     // ======================================================
//     function scheduleSave() {
//         clearTimeout(draftTimer);
//         draftTimer = setTimeout(saveDraft, 400);
//     }

//     function saveDraft() {
//         if (!currentHouseholdId) return;
//         localStorage.setItem(
//             `child_draft_${currentHouseholdId}`,
//             JSON.stringify(buildPayload())
//         );
//     }

//     function loadDraft(id) {
//         return JSON.parse(localStorage.getItem(`child_draft_${id}`));
//     }

//     // ======================================================
//     function addChild(prefill = {}) {
//         const card = childTemplate.content.cloneNode(true).querySelector(".child-card");

//         card.querySelector('[name="child_id[]"]').value =
//             prefill.child_id || "";

//         // Hidden Contract ID
//         const hidden = document.createElement("input");
//         hidden.type = "hidden";
//         hidden.name = "contract_id[]";
//         hidden.value = prefill.contract?.contract_id || "";
//         card.appendChild(hidden);

//         card.querySelector('[name="child_first_name[]"]').value = prefill.first_name || "";
//         card.querySelector('[name="child_last_name[]"]').value = prefill.last_name || "";
//         card.querySelector('[name="date_of_birth[]"]').value = prefill.date_of_birth || "";
//         card.querySelector('[name="ppsn[]"]').value = prefill.ppsn || "";
//         card.querySelector('[name="chick_code[]"]').value = prefill.chick_code || "";
//         card.querySelector('[name="child_start_date[]"]').value = prefill.start_date || "";
//         card.querySelector('[name="ecce_eligible[]"]').checked = !!prefill.ecce_eligible;

//         const c = prefill.contract || {};
//         card.querySelector('[name="contract_type[]"]').value = c.type || "";
//         card.querySelector('[name="contract_start_date[]"]').value = c.start_date || "";
//         card.querySelector('[name="contract_end_date[]"]').value = c.end_date || "";
//         card.querySelector('[name="agreed_hours_per_week[]"]').value = c.hours_per_week || "";
//         card.querySelector('[name="hourly_rate[]"]').value = c.hourly_rate || "";
//         card.querySelector('[name="subsidy_rate[]"]').value = c.subsidy_rate || "";

//         // REMOVE BUTTON
//         card.querySelector(".remove-child").addEventListener("click", function () {
//             if (!confirm("Remove this child?")) return;

//             const allCards = childContainer.querySelectorAll(".child-card");

//             // Prevent removing the final remaining card
//             if (allCards.length === 1) {
//                 alert("At least one child card must remain.");
//                 return;
//             }

//             card.remove();
//             scheduleSave();
//         });

//         childContainer.appendChild(card);
//     }

//     // ======================================================
//     async function loadHousehold(id) {

//         const res = await fetch(`${API}/household/${id}`);
//         const data = await res.json();

//         parentPreviewContainer.innerHTML = data.parents.length
//             ? data.parents.map(p =>
//                 `<div><b>${p.first_name} ${p.last_name}</b></div>`
//             ).join("")
//             : "No parents";

//         // GROUP CHILDREN (EDIT MODE CORE)
//         const grouped = {};

//         data.children.forEach(row => {

//             if (!grouped[row.child_id]) {
//                 grouped[row.child_id] = {
//                     child_id: row.child_id,
//                     first_name: row.first_name,
//                     last_name: row.last_name,
//                     date_of_birth: row.date_of_birth,
//                     ppsn: row.ppsn,
//                     chick_code: row.chick_code,
//                     ecce_eligible: row.ecce_eligible,
//                     start_date: row.start_date,
//                     contract: null
//                 };
//             }

//             if (row.contract_id) {
//                 grouped[row.child_id].contract = {
//                     contract_id: row.contract_id,
//                     type: row.contract_type,
//                     start_date: row.contract_start_date,
//                     end_date: row.end_date,
//                     hours_per_week: row.agreed_hours_per_week,
//                     hourly_rate: row.hourly_rate,
//                     subsidy_rate: row.subsidy_rate
//                 };
//             }
//         });

//         return Object.values(grouped);
//     }

//     // ======================================================
//     householdSelect.onchange = async (e) => {

//         const id = e.target.value;

//         if (!id) return resetUI();

//         currentHouseholdId = id;

//         const children = await loadHousehold(id);

//         console.log("Loaded children from DB:", children);

//         enableUI();

//         childContainer.innerHTML = "";

//         // Load saved draft
//         const draft = loadDraft(id);

//         // Use draft ONLY if it actually contains child data
//         const hasDraftChildren =
//             draft &&
//             Array.isArray(draft.children) &&
//             draft.children.length > 0 &&
//             draft.children.some(c =>
//                 c.first_name ||
//                 c.last_name ||
//                 c.date_of_birth
//             );

//         if (hasDraftChildren) {

//             draft.children.forEach(c => addChild(c));

//         } else if (children.length) {

//             children.forEach(c => addChild(c));

//         } else {

//             addChild();
//         }
//     };

//     // ======================================================
//     childContainer.addEventListener("input", scheduleSave);
//     childContainer.addEventListener("change", scheduleSave);

//     addChildBtn.onclick = () => addChild();

//     // ======================================================
//     form.onsubmit = async (e) => {

//         e.preventDefault();

//         const res = await fetch(`${API}/child/setup`, {
//             method: "POST",
//             headers: { "Content-Type": "application/json" },
//             body: JSON.stringify(buildPayload())
//         });

//         const data = await res.json();

//         if (!res.ok) {
//             alert(data.error);
//             return;
//         }

//         alert("Saved successfully!");
//         localStorage.removeItem(`child_draft_${currentHouseholdId}`);

//         // childContainer.innerHTML = "";
//         // addChild();
//         await householdSelect.onchange({
//     target: { value: currentHouseholdId }
//         });
//     };

//     // ======================================================
//     // REFRESH
//     refreshChildrenBtn?.addEventListener("click", async () => {

//         // Reset household dropdown
//         householdSelect.value = "";

//         // Clear current UI
//         resetUI();

//         // Reload households
//         const res = await fetch(`${API}/households`);
//         const data = await res.json();

//         householdSelect.innerHTML =
//             `<option value="">Select</option>` +
//             data.map(h =>
//                 `<option value="${h.household_id}">${h.household_name}</option>`
//             ).join("");
//     });

//     // ======================================================
//     // CLEAR FORM
//     clearFormBtn?.addEventListener("click", () => {

//         childContainer.innerHTML = "";

//         if (currentHouseholdId) {
//             addChild();
//         }

//         scheduleSave();
//     });

//     // INIT
//     resetUI();
//     fetch(`${API}/households`)
//         .then(r => r.json())
//         .then(data => {
//             householdSelect.innerHTML =
//                 `<option value="">Select</option>` +
//                 data.map(h =>
//                     `<option value="${h.household_id}">${h.household_name}</option>`
//                 ).join("");
//         });
// });
