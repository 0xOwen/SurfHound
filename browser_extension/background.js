// background.js

// Function to send URLs to your Flask API
function detectPhishing(url) {
    // Get the user_id from storage
    chrome.storage.sync.get(['user_id'], function(result) {
        fetch('http://localhost:5000/check_phishing', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ url: url, user_id: result.user_id }),
        })
        .then(response => response.json())
        .then(data => {
            console.log('Message from server: ', data);

            if (data.message !== 'Ignored URL'){
                // If the URL contains 'phishing', display the warning popup
                if (url.includes(data.is_phishing)) {
                    chrome.windows.create({
                        type: 'popup',
                        url: chrome.runtime.getURL('warning.html'),
                        width: 400,
                        height: 200,
                        focused: true
                    });
                } else {
                    // If the URL does not contain 'phishing', display the safe popup
                    chrome.windows.create({
                        type: 'popup',
                        url: chrome.runtime.getURL('safe.html'),
                        width: 400,
                        height: 200,
                        focused: true
                    });
                }
            }
        })
        .catch(error => console.error('Error:', error));
    });
}

// Listen for clicks on the browser action button
chrome.action.onClicked.addListener((tab) => {
    // Send the URL to your Flask API
    detectPhishing(tab.url);
});

// Listen for tab updates
chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
    // If the updated tab is a popup, return early
    if (tab.url.includes('popup.html') || tab.url.includes('safe.html') || tab.url.includes('warning.html')) {
        return;
    }

    // If the URL has changed, send it to your Flask API
    if (changeInfo.url) {
        detectPhishing(changeInfo.url);
    }
});