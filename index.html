<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ANPR Web App</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background: #121212;
            color: white;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            flex-direction: column;
        }
        .container {
            background: #1E1E1E;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0px 0px 10px rgba(255, 255, 255, 0.2);
            width: 300px;
            text-align: center;
        }
        input, button, select {
            width: 100%;
            padding: 10px;
            margin: 10px 0;
            border: none;
            border-radius: 5px;
        }
        button {
            background: #00A86B;
            color: white;
            cursor: pointer;
            font-size: 16px;
        }
        button:hover {
            background: #007B50;
        }
    </style>
</head>
<body>
    <div class="container" id="login-container">
        <h2>Login</h2>
        <input type="text" id="username" placeholder="Username">
        <input type="password" id="password" placeholder="Password">
        <button onclick="login()">Login</button>
    </div>

    <div class="container" id="admin-panel" style="display: none;">
        <h2>Admin Panel</h2>
        <input type="text" id="plate" placeholder="Plate Number">
        <button onclick="addPrimaryVehicle()">Add Primary Vehicle</button>
        <button onclick="removeVehicle()">Remove Vehicle</button>
        <h3>Users</h3>
        <input type="text" id="newUser" placeholder="New Username">
        <input type="password" id="newPassword" placeholder="New Password">
        <button onclick="createUser()">Create User</button>
    </div>

    <div class="container" id="user-panel" style="display: none;">
        <h2>User Panel</h2>
        <h3>Primary Vehicles</h3>
        <div id="primary-vehicles"></div>
        <h3>Add Temporary Vehicle</h3>
        <input type="text" id="tempPlate" placeholder="Plate Number">
        <button onclick="addTemporaryVehicle()">Add Temporary Vehicle</button>
    </div>

    <script>
        function login() {
            const username = document.getElementById("username").value;
            const password = document.getElementById("password").value;
            fetch('/login', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ username, password })
            }).then(res => res.json()).then(data => {
                if (data.role === 'admin') {
                    document.getElementById("login-container").style.display = "none";
                    document.getElementById("admin-panel").style.display = "block";
                } else if (data.role === 'user') {
                    document.getElementById("login-container").style.display = "none";
                    document.getElementById("user-panel").style.display = "block";
                    loadUserVehicles();
                } else {
                    alert("Invalid login");
                }
            });
        }
        function addPrimaryVehicle() {
            fetch('/add_primary_vehicle', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ plate: document.getElementById("plate").value })
            }).then(res => res.json()).then(data => alert(data.message));
        }
        function removeVehicle() {
            fetch('/remove_vehicle', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ plate: document.getElementById("plate").value })
            }).then(res => res.json()).then(data => alert(data.message));
        }
        function createUser() {
            fetch('/create_user', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    username: document.getElementById("newUser").value,
                    password: document.getElementById("newPassword").value
                })
            }).then(res => res.json()).then(data => alert(data.message));
        }
        function addTemporaryVehicle() {
            fetch('/add_temp_vehicle', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ plate: document.getElementById("tempPlate").value })
            }).then(res => res.json()).then(data => alert(data.message));
        }
        function loadUserVehicles() {
            fetch('/user_vehicles')
            .then(res => res.json())
            .then(data => {
                document.getElementById("primary-vehicles").innerHTML = data.vehicles.join("<br>");
            });
        }
    </script>
</body>
</html>
