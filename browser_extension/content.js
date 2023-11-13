// content.js

chrome.runtime.sendMessage({ type: 'url', url: window.location.href });
