
async function loadDashboard() {
    try {
        // Get trip history from Flask API
        const tripsResponse = await fetch("/trips");

        if (!tripsResponse.ok) {
            throw new Error("Failed to load trips");
        }

        const trips = await tripsResponse.json();

        // Get dashboard summary
        const summaryResponse = await fetch("/trips/summary");

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
                    <td colspan="3">No trips recorded yet.</td>
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

// Load dashboard when page is ready
document.addEventListener("DOMContentLoaded", loadDashboard);
