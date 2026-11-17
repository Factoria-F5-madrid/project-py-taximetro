
async function loadDashboard(day = "") {
    try {
        const query = day ? `?day=${day}` : "";

        const tripsResponse = await fetch(`/trips${query}`);

        if (!tripsResponse.ok) {
            throw new Error("Failed to load trips");
        }

        const trips = await tripsResponse.json();

        const summaryResponse = await fetch(`/trips/summary${query}`);

        if (!summaryResponse.ok) {
            throw new Error("Failed to load summary");
        }

        const summary = await summaryResponse.json();

        document.getElementById("trip-count").textContent = summary.count;

        document.getElementById("total-earnings").textContent =
            "€" + Number(summary.total_eur).toFixed(2);

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


// Update the current trip display
async function loadCurrentTrip() {
    try {
        const response = await fetch("/trips/current");

        if (response.status === 404) {
            updateTripDisplay(false);
            return;
        }

        if (!response.ok) {
            throw new Error("Could not load current trip");
        }

        const trip = await response.json();

        updateTripDisplay(true, trip);

    } catch (error) {
        console.error("Current trip error:", error);
    }
}


// Update trip status and buttons
function updateTripDisplay(active, trip = {}) {
    const status = document.getElementById("trip-status");
    const fare = document.getElementById("current-fare");

    const startButton = document.getElementById("start-trip");
    const movingButton = document.getElementById("moving");
    const stoppedButton = document.getElementById("stopped");
    const finishButton = document.getElementById("finish-trip");

    if (!active) {
        status.textContent = "No active trip";
        fare.textContent = "€0.00";

        startButton.disabled = false;
        movingButton.disabled = true;
        stoppedButton.disabled = true;
        finishButton.disabled = true;

        return;
    }

    status.textContent = `Trip ${trip.state}`;
    fare.textContent =
        "€" + Number(trip.current_total_eur).toFixed(2);

    startButton.disabled = true;
    movingButton.disabled = trip.state === "moving";
    stoppedButton.disabled = trip.state === "stopped";
    finishButton.disabled = false;
}


// Send authenticated requests with CSRF protection
async function sendTripAction(url, data = {}) {
    const csrfToken = document.getElementById("csrf-token").value;

    const response = await fetch(url, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": csrfToken
        },
        body: JSON.stringify(data)
    });

    const result = await response.json();

    if (!response.ok) {
        throw new Error(result.error || "Something went wrong");
    }

    return result;
}


// Show messages to the user
function showTripMessage(message) {
    document.getElementById("trip-message").textContent = message;
}


// Set up dashboard
document.addEventListener("DOMContentLoaded", () => {

    loadDashboard();
    loadCurrentTrip();

    // Refresh the current fare every second
    setInterval(loadCurrentTrip, 1000);

    // Date filter
    const dateInput = document.getElementById("filter-date");

    document.getElementById("apply-filter").addEventListener("click", () => {
        if (!dateInput.value) {
            alert("Please select a date first.");
            return;
        }

        loadDashboard(dateInput.value);
    });

    document.getElementById("clear-filter").addEventListener("click", () => {
        dateInput.value = "";
        loadDashboard();
    });


    // Start trip
    document.getElementById("start-trip").addEventListener("click", async () => {
        try {
            const result = await sendTripAction("/trips/start");

            showTripMessage(result.message);
            await loadCurrentTrip();

        } catch (error) {
            showTripMessage(error.message);
        }
    });


    // Change trip state
    document.getElementById("moving").addEventListener("click", async () => {
        try {
            const result = await sendTripAction("/trips/state", {
                state: "moving"
            });

            showTripMessage(result.message);
            await loadCurrentTrip();

        } catch (error) {
            showTripMessage(error.message);
        }
    });


    document.getElementById("stopped").addEventListener("click", async () => {
        try {
            const result = await sendTripAction("/trips/state", {
                state: "stopped"
            });

            showTripMessage(result.message);
            await loadCurrentTrip();

        } catch (error) {
            showTripMessage(error.message);
        }
    });


    // Finish trip
    document.getElementById("finish-trip").addEventListener("click", async () => {
        try {
            const result = await sendTripAction("/trips/finish");

            showTripMessage(
                `${result.message}. Total: €${Number(result.total_eur).toFixed(2)}`
            );

            await loadCurrentTrip();
            await loadDashboard();

        } catch (error) {
            showTripMessage(error.message);
        }
    });

});
