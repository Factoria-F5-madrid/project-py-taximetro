
async function loadDashboard(day = "") {
    try {
        // Build the API URLs
        const query = day ? `?day=${day}` : "";

        // Get trip history
        const tripsResponse = await fetch(`/trips${query}`);

        if (!tripsResponse.ok) {
            throw new Error("Failed to load trips");
        }

        const trips = await tripsResponse.json();

        // Get dashboard summary
        const summaryResponse = await fetch(`/trips/summary${query}`);

        if (!summaryResponse.ok) {
            throw new Error("Failed to load summary");
        }

        const summary = await summaryResponse.json();

        // Update summary cards
        document.getElementById("trip-count").textContent = summary.count;

        document.getElementById("total-earnings").textContent =
            "€" + Number(summary.total_eur).toFixed(2);

        // Display trip history
        const tripList = document.getElementById("trip-list");

        tripList.innerHTML = "";

        if (trips.length === 0) {
            tripList.innerHTML = `
                <tr>
                    <td colspan="3">No trips recorded for this date.</td>
                </tr>
            `;
            return;
        }

        trips.forEach(trip => {
            const row = document.createElement("tr");

            const startCell = document.createElement("td");
            startCell.textContent = new Date(trip.start).toLocaleString();

            const endCell = document.createElement("td");
            endCell.textContent = new Date(trip.end).toLocaleString();

            const fareCell = document.createElement("td");
            fareCell.textContent =
                "€" + Number(trip.total_eur).toFixed(2);

            row.appendChild(startCell);
            row.appendChild(endCell);
            row.appendChild(fareCell);

            tripList.appendChild(row);
        });

    } catch (error) {
        console.error("Dashboard error:", error);
    }
}

// Set up date filter buttons
document.addEventListener("DOMContentLoaded", () => {

    // Load all trips when dashboard opens
    loadDashboard();

    const dateInput = document.getElementById("filter-date");
    const applyButton = document.getElementById("apply-filter");
    const clearButton = document.getElementById("clear-filter");

    // Apply selected date
    applyButton.addEventListener("click", () => {
        const selectedDate = dateInput.value;

        if (!selectedDate) {
            alert("Please select a date first.");
            return;
        }

        loadDashboard(selectedDate);
    });

    // Clear date filter
    clearButton.addEventListener("click", () => {
        dateInput.value = "";
        loadDashboard();
    });
});
