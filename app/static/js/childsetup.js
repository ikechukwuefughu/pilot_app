console.log("child.js loaded");

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
    function buildPayload() {

        const children = [...childContainer.querySelectorAll(".child-card")].map(card => ({

            child_id: card.querySelector('[name="child_id[]"]')?.value || null,

            first_name: card.querySelector('[name="child_first_name[]"]').value,
            last_name: card.querySelector('[name="child_last_name[]"]').value,
            date_of_birth: card.querySelector('[name="date_of_birth[]"]').value,
            ppsn: card.querySelector('[name="ppsn[]"]').value,
            chick_code: card.querySelector('[name="chick_code[]"]').value,
            start_date: card.querySelector('[name="child_start_date[]"]').value,
            ecce_eligible: card.querySelector('[name="ecce_eligible[]"]').checked,

            contract: {
                contract_id: card.querySelector('[name="contract_id[]"]')?.value || null,
                type: card.querySelector('[name="contract_type[]"]').value,
                start_date: card.querySelector('[name="contract_start_date[]"]').value,
                end_date: card.querySelector('[name="contract_end_date[]"]').value,
                hours_per_week: card.querySelector('[name="agreed_hours_per_week[]"]').value,
                hourly_rate: card.querySelector('[name="hourly_rate[]"]').value,
                subsidy_rate: card.querySelector('[name="subsidy_rate[]"]').value
            }
        }));

        return { household_id: currentHouseholdId, children };
    }

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
        return JSON.parse(localStorage.getItem(`child_draft_${id}`));
    }

    // ======================================================
    function addChild(prefill = {}) {
        const card = childTemplate.content.cloneNode(true).querySelector(".child-card");

        card.querySelector('[name="child_id[]"]').value =
            prefill.child_id || "";

        // Hidden Contract ID
        const hidden = document.createElement("input");
        hidden.type = "hidden";
        hidden.name = "contract_id[]";
        hidden.value = prefill.contract?.contract_id || "";
        card.appendChild(hidden);

        card.querySelector('[name="child_first_name[]"]').value = prefill.first_name || "";
        card.querySelector('[name="child_last_name[]"]').value = prefill.last_name || "";
        card.querySelector('[name="date_of_birth[]"]').value = prefill.date_of_birth || "";
        card.querySelector('[name="ppsn[]"]').value = prefill.ppsn || "";
        card.querySelector('[name="chick_code[]"]').value = prefill.chick_code || "";
        card.querySelector('[name="child_start_date[]"]').value = prefill.start_date || "";
        card.querySelector('[name="ecce_eligible[]"]').checked = !!prefill.ecce_eligible;

        const c = prefill.contract || {};
        card.querySelector('[name="contract_type[]"]').value = c.type || "";
        card.querySelector('[name="contract_start_date[]"]').value = c.start_date || "";
        card.querySelector('[name="contract_end_date[]"]').value = c.end_date || "";
        card.querySelector('[name="agreed_hours_per_week[]"]').value = c.hours_per_week || "";
        card.querySelector('[name="hourly_rate[]"]').value = c.hourly_rate || "";
        card.querySelector('[name="subsidy_rate[]"]').value = c.subsidy_rate || "";

        // REMOVE BUTTON
        card.querySelector(".remove-child").addEventListener("click", function () {
            if (!confirm("Remove this child?")) return;

            const allCards = childContainer.querySelectorAll(".child-card");

            // Prevent removing the final remaining card
            if (allCards.length === 1) {
                alert("At least one child card must remain.");
                return;
            }

            card.remove();
            scheduleSave();
        });

        childContainer.appendChild(card);
    }

    // ======================================================
    async function loadHousehold(id) {

        const res = await fetch(`${API}/household/${id}`);
        const data = await res.json();

        parentPreviewContainer.innerHTML = data.parents.length
            ? data.parents.map(p =>
                `<div><b>${p.first_name} ${p.last_name}</b></div>`
            ).join("")
            : "No parents";

        // GROUP CHILDREN (EDIT MODE CORE)
        const grouped = {};

        data.children.forEach(row => {

            if (!grouped[row.child_id]) {
                grouped[row.child_id] = {
                    child_id: row.child_id,
                    first_name: row.first_name,
                    last_name: row.last_name,
                    date_of_birth: row.date_of_birth,
                    ppsn: row.ppsn,
                    chick_code: row.chick_code,
                    ecce_eligible: row.ecce_eligible,
                    start_date: row.start_date,
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
    householdSelect.onchange = async (e) => {

        const id = e.target.value;

        if (!id) return resetUI();

        currentHouseholdId = id;

        const children = await loadHousehold(id);

        console.log("Loaded children from DB:", children);

        enableUI();

        childContainer.innerHTML = "";

        // Load saved draft
        const draft = loadDraft(id);

        // Use draft ONLY if it actually contains child data
        const hasDraftChildren =
            draft &&
            Array.isArray(draft.children) &&
            draft.children.length > 0 &&
            draft.children.some(c =>
                c.first_name ||
                c.last_name ||
                c.date_of_birth
            );

        if (hasDraftChildren) {

            draft.children.forEach(c => addChild(c));

        } else if (children.length) {

            children.forEach(c => addChild(c));

        } else {

            addChild();
        }
    };

    // ======================================================
    childContainer.addEventListener("input", scheduleSave);
    childContainer.addEventListener("change", scheduleSave);

    addChildBtn.onclick = () => addChild();

    // ======================================================
    form.onsubmit = async (e) => {

        e.preventDefault();

        const res = await fetch(`${API}/child/setup`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(buildPayload())
        });

        const data = await res.json();

        if (!res.ok) {
            alert(data.error);
            return;
        }

        alert("Saved successfully!");
        localStorage.removeItem(`child_draft_${currentHouseholdId}`);

        // childContainer.innerHTML = "";
        // addChild();
        await householdSelect.onchange({
    target: { value: currentHouseholdId }
        });
    };

    // ======================================================
    // REFRESH
    refreshChildrenBtn?.addEventListener("click", async () => {

        // Reset household dropdown
        householdSelect.value = "";

        // Clear current UI
        resetUI();

        // Reload households
        const res = await fetch(`${API}/households`);
        const data = await res.json();

        householdSelect.innerHTML =
            `<option value="">Select</option>` +
            data.map(h =>
                `<option value="${h.household_id}">${h.household_name}</option>`
            ).join("");
    });

    // ======================================================
    // CLEAR FORM
    clearFormBtn?.addEventListener("click", () => {

        childContainer.innerHTML = "";

        if (currentHouseholdId) {
            addChild();
        }

        scheduleSave();
    });

    // INIT
    resetUI();
    fetch(`${API}/households`)
        .then(r => r.json())
        .then(data => {
            householdSelect.innerHTML =
                `<option value="">Select</option>` +
                data.map(h =>
                    `<option value="${h.household_id}">${h.household_name}</option>`
                ).join("");
        });
});