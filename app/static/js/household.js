// ==========================================================
// HOUSEHOLD MANAGEMENT with BOOTSTRAP TOASTS
// ==========================================================
document.addEventListener("DOMContentLoaded", () => {
    const householdSelect = document.getElementById("householdSelect");
    const householdIdInput = document.getElementById("household_id");
    const form = document.getElementById("householdForm");
    const parentsContainer = document.getElementById("parentsContainer");
    const parentTemplate = document.getElementById("parentTemplate");

    const addParentBtn = document.getElementById("addParentBtn");
    const removeParentBtn = document.getElementById("removeParentBtn");
    const clearFormBtn = document.getElementById("clearFormBtn");
    const newHouseholdBtn = document.getElementById("newHouseholdBtn");
    const refreshHouseholdsBtn = document.getElementById("refreshHouseholdsBtn");

    const toastEl = document.getElementById("toast");
    const toastBody = toastEl.querySelector(".toast-body");
    const toast = new bootstrap.Toast(toastEl);

    let currentHouseholdId = null;

    // ------------------------------- TOAST HANDLER -------------------------------
    function showToast(message, type = "info") {
        toastBody.textContent = message;
        toastEl.className = `toast align-items-center text-bg-${type}`;
        toast.show();
    }

    // --------------------------- PRIMARY CONTACT HANDLING ------------------------
    function setPrimary(card) {
        parentsContainer.querySelectorAll(".parent-card").forEach(c => {
            c.querySelector(".primary-contact-input").value = "0";
            const btn = c.querySelector(".primary-contact-btn");
            btn.classList.remove("btn-warning");
            btn.classList.add("btn-outline-warning");
            btn.innerHTML = '<i class="fas fa-star me-2"></i>Set as Primary Contact';
        });
        card.querySelector(".primary-contact-input").value = "1";
        const activeBtn = card.querySelector(".primary-contact-btn");
        activeBtn.classList.add("btn-warning");
        activeBtn.innerHTML = '<i class="fas fa-check me-2"></i>Primary Contact';
    }

    function ensurePrimary() {
        const cards = parentsContainer.querySelectorAll(".parent-card");
        if ([...cards].every(c => c.querySelector(".primary-contact-input").value !== "1"))
            if (cards[0]) setPrimary(cards[0]);
    }

    // --------------------------- PARENT MANAGEMENT ------------------------------
    function updateTitles() {
        parentsContainer.querySelectorAll(".parent-card").forEach((c, i) =>
            c.querySelector(".parent-title").textContent = `Parent / Guardian ${i + 1}`
        );
    }

    function updateRemoveButton() {
        removeParentBtn.disabled = parentsContainer.querySelectorAll(".parent-card").length <= 1;
    }

    function addParent(parent = {}) {
        const clone = parentTemplate.content.cloneNode(true);
        const card = clone.querySelector(".parent-card");
        card.querySelector('[name="parent_id[]"]').value = parent.parent_id || "";
        card.querySelector('[name="parent_first_name[]"]').value = parent.first_name || "";
        card.querySelector('[name="parent_last_name[]"]').value = parent.last_name || "";
        card.querySelector('[name="parent_phone[]"]').value = parent.phone || "";
        card.querySelector('[name="parent_email[]"]').value = parent.email || "";
        card.querySelector('.primary-contact-input').value = parent.is_primary ? "1" : "0";
        const btn = card.querySelector(".primary-contact-btn");
        btn.addEventListener("click", () => setPrimary(card));
        parentsContainer.appendChild(card);
        if (parent.is_primary) setPrimary(card);
        updateTitles(); updateRemoveButton(); ensurePrimary();
    }

    function removeParent() {
        const cards = parentsContainer.querySelectorAll(".parent-card");
        if (cards.length > 1) {
            cards[cards.length - 1].remove();
            updateTitles(); updateRemoveButton(); ensurePrimary();
        }
    }

    function clearParents() {
        parentsContainer.innerHTML = ""; //addParent();
    }

    // --------------------------- FORM HELPERS -----------------------------------
    function getField(n) { return form.querySelector(`[name="${n}"]`); }

    function clearForm() {
        form.reset();
        householdIdInput.value = "";
        householdSelect.value = "";
        currentHouseholdId = null;
        clearParents();
        addParent();
    }

    async function loadHouseholds() {
        const res = await fetch("/api/households");

        const text = await res.text();
        console.log("RAW RESPONSE:", text);
        
        try {
            const data = JSON.parse(text);
        } catch (e) {
            console.error("NOT JSON RESPONSE:", text);
        }
        // const res = await fetch("/api/households");
        // const households = await res.json();
        // householdSelect.innerHTML = '<option value="">Select Household...</option>';
        // households.forEach(h =>
        //     householdSelect.innerHTML += `<option value="${h.household_id}">${h.household_name}</option>`
        // );
    }

    async function loadHousehold(id) {
        if (!id) return clearForm();
        const res = await fetch(`/api/household/${id}`);
        const data = await res.json();
        if (data.error) return showToast(data.error, "danger");
        populateForm(data);
    }

    function populateForm(data) {
        Object.entries(data.household).forEach(([k, v]) => {
            const field = getField(k);
            if (field) field.value = v || "";
        });
        householdIdInput.value = data.household.household_id;
        currentHouseholdId = data.household.household_id;
        clearParents();
        (data.parents || []).forEach(addParent);
        ensurePrimary();
        document.querySelector('[name="household_name"]').focus();
        window.scrollTo(0, 0);
    }

    function buildPayload() {
        return {
            household_id: householdIdInput.value || null,
            household_name: getField("household_name").value,
            phone: getField("phone").value,
            address_line1: getField("address_line1").value,
            address_line2: getField("address_line2").value,
            city: getField("city").value,
            county: getField("county").value,
            eircode: getField("eircode").value,
            parents: [...parentsContainer.querySelectorAll(".parent-card")].map(c => ({
                parent_id: c.querySelector('[name="parent_id[]"]').value || null,
                first_name: c.querySelector('[name="parent_first_name[]"]').value,
                last_name: c.querySelector('[name="parent_last_name[]"]').value,
                phone: c.querySelector('[name="parent_phone[]"]').value,
                email: c.querySelector('[name="parent_email[]"]').value,
                is_primary: c.querySelector(".primary-contact-input").value === "1"
            }))
        };
    }

    // --------------------------- EVENTS -----------------------------------------
    addParentBtn.addEventListener("click", () => addParent());
    removeParentBtn.addEventListener("click", removeParent);
    clearFormBtn.addEventListener("click", clearForm);
    newHouseholdBtn.addEventListener("click", clearForm);
    // refreshHouseholdsBtn.addEventListener("click", loadHouseholds);
    refreshHouseholdsBtn.addEventListener("click", async () => {

        clearForm();

        await loadHouseholds();

        showToast("Households refreshed", "info");
    });
    householdSelect.addEventListener("change", e => loadHousehold(e.target.value));

    form.addEventListener("submit", async e => {
        e.preventDefault();
        const saveBtn = form.querySelector('button[type="submit"]');
        saveBtn.disabled = true;
        saveBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Saving...';
        try {
            const payload = buildPayload();
            if (!payload.household_name) return showToast("Enter a household name.", "warning");
            const res = await fetch("/api/household", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload)
            });
            const result = await res.json();
            if (result.success) {
                showToast("Household saved successfully", "success");
                await loadHouseholds();
                householdSelect.value = result.household_id;
                await loadHousehold(result.household_id);
            } else showToast(result.error || "Save failed.", "danger");
        } catch {
            showToast("Error saving household.", "danger");
        } finally {
            saveBtn.disabled = false;
            saveBtn.innerHTML = '<i class="fas fa-save me-2"></i>Save Household';
        }
    });

    // --------------------------- INIT -------------------------------------------
    loadHouseholds(); clearForm();
});
