const appFrame = document.getElementById('appFrame');
const errorMsg = document.getElementById('errorMsg');
const preloader = document.getElementById('preloader');

const BASE_URL = 'http://127.0.0.1:8000/';
const LOGIN_URL = BASE_URL + 'login/';
const DASHBOARD_URL = BASE_URL + 'dashboard/'; // or any authenticated landing page
const LOAD_TIMEOUT = 5000; // ms

function showError(message) {
  preloader.style.display = 'none';
  appFrame.style.display = 'none';
  errorMsg.textContent = message;
  errorMsg.style.display = 'block';
}

function showApp() {
  preloader.style.display = 'none';
  errorMsg.style.display = 'none';
  appFrame.style.display = 'block';
}

function showPreloader() {
  preloader.style.display = 'flex';
  errorMsg.style.display = 'none';
  appFrame.style.display = 'none';
}

function setIframeUrl(url) {
  showPreloader();
  appFrame.src = url;
}

// Detect login success by monitoring iframe URL
appFrame.onload = function() {
  try {
    // Only works if same-origin (should be for localhost/dev)
    const currentUrl = appFrame.contentWindow.location.href;
    if (currentUrl.startsWith(DASHBOARD_URL)) {
      showApp();
    } else {
      // Still on login or another page
      showApp(); // Optionally: keep as preloader until dashboard
    }
  } catch (e) {
    // Cross-origin: fallback to just show the app
    showApp();
  }
};

appFrame.onerror = function() {
  showError('The app could not be loaded. Please check if it is running.');
};

// Timeout fallback
setTimeout(() => {
  if (preloader.style.display === 'flex') {
    showError('The app could not be reached. Please check if it is running.');
  }
}, LOAD_TIMEOUT);

// On load, show login page in iframe
setIframeUrl(LOGIN_URL);
