document.getElementById('urlForm').addEventListener('submit', function(event) {
    event.preventDefault();
        // Clear result text
    document.getElementById('urlCheckResult').textContent = '';
    var url = document.getElementById('url').value;

    // Validate URL
    var protocolRegex = /^(https?:\/\/)/i; // protocol
    var domainRegex = /^((([a-z\d]([a-z\d-]*[a-z\d])*)\.)+[a-z]{2,}|((\d{1,3}\.){3}\d{1,3}))/i; // domain name or ip (v4) address

    if (!protocolRegex.test(url)) {
        alert('Invalid URL. Please include http:// or https:// in your URL.');
        return;
    }

    // Remove protocol for domain validation
    var urlWithoutProtocol = url.replace(protocolRegex, '');
    if (!domainRegex.test(urlWithoutProtocol)) {
        alert('Invalid URL. Please enter a valid domain name or IP address.');
        return;
    }

        // Show spinner
        document.getElementById('spinner').style.display = 'block';

    fetch('http://localhost:5000/api/check_url', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({url: url}),
    })
    .then(response => response.json())
    .then(data => {
            // Hide spinner
        document.getElementById('spinner').style.display = 'none';
        var resultText = data.is_phishing ? 'This URL is a phishing site.' : 'This URL is safe.';
        var resultClass = data.is_phishing ? 'phishing' : 'safe';
        var urlCheckResult = document.getElementById('urlCheckResult');
        urlCheckResult.textContent = resultText;
        urlCheckResult.className = resultClass;
    })
    .catch((error) => {
            // Hide spinner
        document.getElementById('spinner').style.display = 'none';
        console.error('Error:', error);
        document.getElementById('urlCheckResult').textContent = 'Error checking URL';
    });
});
document.getElementById('check-url-virustotal').addEventListener('click', function(event) {
    event.preventDefault();
    // Clear result text
    document.getElementById('urlCheckResult').textContent = '';
    var url = document.getElementById('url').value;

    // Validate URL
    var protocolRegex = /^(https?:\/\/)/i; // protocol
    var domainRegex = /^((([a-z\d]([a-z\d-]*[a-z\d])*)\.)+[a-z]{2,}|((\d{1,3}\.){3}\d{1,3}))/i; // domain name or ip (v4) address

    if (!protocolRegex.test(url)) {
        alert('Invalid URL. Please include http:// or https:// in your URL.');
        return;
    }

    // Remove protocol for domain validation
    var urlWithoutProtocol = url.replace(protocolRegex, '');
    if (!domainRegex.test(urlWithoutProtocol)) {
        alert('Invalid URL. Please enter a valid domain name or IP address.');
        return;
    }

    // Show spinner
    document.getElementById('spinner').style.display = 'block';

    fetch('http://localhost:5000/check_url_virustotal', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({url: url}),
    })
    .then(response => response.json())
    .then(data => {
        // Hide spinner
        document.getElementById('spinner').style.display = 'none';
        var resultText = data.is_phishing ? 'This URL is a phishing site according to VirusTotal API.' : 'This URL is safe according to VirusTotal API.';
        var resultClass = data.is_phishing ? 'phishing' : 'safe';
        var urlCheckResult = document.getElementById('urlCheckResult');
        urlCheckResult.textContent = resultText;
        urlCheckResult.className = resultClass;
    })
    .catch((error) => {
        // Hide spinner
        document.getElementById('spinner').style.display = 'none';
        console.error('Error:', error);
        document.getElementById('urlCheckResult').textContent = 'Error checking URL on VirusTotal';
    });
});