function sanitize(text) {
    // Replace all non-ASCII characters with a standard dash
    return text.replace(/[^\x00-\x7F]/g, "-");
}

// User Login / Registration
async function loginUser() {
    const email = document.getElementById("login-email").value.trim().toLowerCase();
    const password = document.getElementById("login-password").value;
	if (!email) {
        alert("Please enter your email.");
        return;
    }

    try {
        const resp = await window.pywebview.api.login(email, password);
        if (resp.success) {
            localStorage.setItem("userEmail", email);
            localStorage.setItem("userName", resp.name);
            showDashboard();
        } else {
            alert(resp.message);
        }
    } catch (err) {
        console.error("Login error:", err);
        alert("Login failed. Check console for details.");
    }
}

async function registerUser() {
    const name = document.getElementById("register-name").value.trim();
    const email = document.getElementById("register-email").value.trim().toLowerCase();
	const password = document.getElementById("register-password").value.trim();

    if (!name || !email || !password) {
        alert("Please enter all fields: name, email, and password.");
        return;
    }

    try {
        const resp = await window.pywebview.api.register(name, password, email);
        if (resp.success) {
            localStorage.setItem("userEmail", email);
            localStorage.setItem("userName", name);
            showDashboard();
        } else {
            alert(resp.message);
        }
    } catch (err) {
        console.error("Registration error:", err);
        alert("Registration failed. Check console for details.");
    }
}

// Dashboard / View
function showDashboard() {
    document.getElementById("login-section").style.display = "none";
    document.getElementById("register-section").style.display = "none";
    document.getElementById("dashboard-section").style.display = "block";
    document.getElementById("welcome-name").innerText = localStorage.getItem("userName") || "User";

    loadAvailableCars();
    loadRentalHistory();
}

// Load Available Cars
async function loadAvailableCars() {
    if (!window.pywebview || !window.pywebview.api) {
        setTimeout(loadAvailableCars, 100);
        return;
    }

    try {
        const cars = await window.pywebview.api.get_available_cars();
        const tableBody = document.querySelector("#available-cars-table tbody");
        tableBody.innerHTML = "";

        if (!cars || cars.length === 0) {
            const row = document.createElement("tr");
            row.innerHTML = `<td colspan="4" style="text-align:center;">No cars available at the moment.</td>`;
            tableBody.appendChild(row);
            return;
        }

        cars.forEach(car => {
            const safeModel = sanitize(car.model);
            const safeMake = sanitize(car.make);

            const row = document.createElement("tr");
            row.innerHTML = `
                <td>${safeMake} ${safeModel}</td>
                <td>${car.type}</td>
                <td>${car.year}</td>
                <td><button onclick="rentCar(${car.id})">Rent</button></td>
            `;
            tableBody.appendChild(row);
        });
    } catch (err) {
        console.error("Error loading cars:", err);
    }
}

// Rent a Car
async function rentCar(carId) {
    const duration = prompt("How many days do you want to rent this car?");
    if (!duration || isNaN(duration) || duration <= 0) {
        alert("Invalid duration.");
        return;
    }

    const email = localStorage.getItem("userEmail");
    if (!email) {
        alert("You must be logged in to rent a car.");
        return;
    }

    try {
        const resp = await window.pywebview.api.rent_car(carId, email, parseInt(duration));
        if (resp.success) {
            alert(resp.message);
            loadAvailableCars();
            loadRentalHistory();
        } else {
            alert(resp.message);
        }
    } catch (err) {
        console.error("Error renting car:", err);
        alert("Failed to rent car. Check console for details.");
    }
}

// Load Rental History
async function loadRentalHistory() {
    const email = localStorage.getItem("userEmail");
    if (!email) return;

    if (!window.pywebview || !window.pywebview.api) {
        setTimeout(loadRentalHistory, 100);
        return;
    }

    try {
        const rentals = await window.pywebview.api.get_rentals(email);
        const tableBody = document.querySelector("#rental-history-table tbody");
        tableBody.innerHTML = "";

        if (!rentals || rentals.length === 0) {
            const row = document.createElement("tr");
            row.innerHTML = `<td colspan="4" style="text-align:center;">No rentals yet.</td>`;
            tableBody.appendChild(row);
            return;
        }

        rentals.forEach(rental => {
            const row = document.createElement("tr");
            row.innerHTML = `
                <td>${sanitize(rental.car)}</td>
                <td>${rental.duration}</td>
                <td>${rental.from}</td>
                <td>${rental.to}</td>
            `;
            tableBody.appendChild(row);
        });
    } catch (err) {
        console.error("Error loading rentals:", err);
    }
}

// Logout
function logout() {
    // Clear stored user info
    localStorage.removeItem("userEmail");
    localStorage.removeItem("userName");
	localStorage.removeItem("userPassword");

    // Hide dashboard
    document.getElementById("dashboard-section").style.display = "none";

    // Show login and register sections
    document.getElementById("login-section").style.display = "block";
    document.getElementById("register-section").style.display = "block";

    // Clear input fields
    document.getElementById("login-email").value = "";
	document.getElementById("login-password").value = "";
    document.getElementById("register-name").value = "";
    document.getElementById("register-email").value = "";
	document.getElementById("register-password").value = "";
}
