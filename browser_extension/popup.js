document.getElementById('loginForm').addEventListener('submit', function(event) {
    event.preventDefault();

    var username = document.getElementById('loginUsername').value;
    var password = document.getElementById('loginPassword').value;

    // Validate username and password
    var usernameRegex = /^[a-zA-Z0-9]+$/; // Alphanumeric characters only
    var passwordRegex = /^.{8,}$/; // At least 8 characters

    if (!usernameRegex.test(username)) {
        alert('Invalid username. Only alphanumeric characters are allowed.');
        return;
    }

    if (!passwordRegex.test(password)) {
        alert('Invalid password. It must be at least 8 characters long.');
        return;
    }

fetch('http://localhost:5000/login', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
    },
    body: JSON.stringify({username: username, password: password}),
})
.then(response => response.json())
.then(data => {
    if (data.message === 'Logged in successfully') {
        chrome.storage.sync.set({user_id: data.user_id});
        document.getElementById('notLoggedIn').style.display = 'none';
        document.getElementById('loggedIn').style.display = 'block';
    } else {
        alert('Login failed');
    }
})
.catch((error) => {
    console.error('Error:', error);
});
});

document.getElementById('registerForm').addEventListener('submit', function(event) {
event.preventDefault();

var username = document.getElementById('registerUsername').value;
var password = document.getElementById('registerPassword').value;

// Validate username and password
var usernameRegex = /^[a-zA-Z0-9]+$/; // Alphanumeric characters only
var passwordRegex = /^.{8,}$/; // At least 8 characters

if (!usernameRegex.test(username)) {
    alert('Invalid username. Only alphanumeric characters are allowed.');
    return;
}

if (!passwordRegex.test(password)) {
    alert('Invalid password. It must be at least 8 characters long.');
    return;
}

fetch('http://localhost:5000/register', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
    },
    body: JSON.stringify({username: username, password: password}),
})
.then(response => response.json())
.then(data => {
    if (data.message === 'Registered and logged in successfully') {
        chrome.storage.sync.set({user_id: data.user_id});
        document.getElementById('notLoggedIn').style.display = 'none';
        document.getElementById('loggedIn').style.display = 'block';
    } else {
        alert('Registration failed');
    }
})
.catch((error) => {
    console.error('Error:', error);
});
});

document.getElementById('urlForm').addEventListener('submit', function(event) {
event.preventDefault();

var url = document.getElementById('url').value;

chrome.storage.sync.get(['user_id'], function(result) {
    fetch('http://localhost:5000/check_phishing', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({url: url, user_id: result.user_id || null}),
    })
    .then(response => response.json())
    .then(data => {
        var resultText = data.is_phishing ? 'This URL is a phishing site.' : 'This URL is safe.';
        document.getElementById('urlCheckResult').textContent = resultText;
    })
    .catch((error) => {
        console.error('Error:', error);
        document.getElementById('urlCheckResult').textContent = 'Error checking URL';
    });
});
});