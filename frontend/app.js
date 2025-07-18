// Enhanced detection function for real data
async function detectVegetables() {
	if (!imageCaptured) {
		showToast('Please capture an image first', 'error');
		return;
	}

	try {
		showToast(' Analyzing image with AI...', 'info');
		detectBtn.disabled = true;
		detectBtn.textContent = 'AI Processing...';

		// Convert canvas to blob
		const blob = await new Promise(resolve => {
			canvasEl.toBlob(resolve, 'image/jpeg', 0.8);
		});

		// Create FormData
		const formData = new FormData();
		formData.append('image', blob, 'captured_image.jpg');
		formData.append('location', currentLocation);

		// Send to backend for REAL detection
		const response = await fetch(`${API_BASE_URL}/detect`, {
			method: 'POST',
			body: formData
		});

		if (!response.ok) {
			throw new Error(`Detection failed: ${response.status}`);
		}

		const detections = await response.json();

		// Clear previous results
		resultsData = [];
		const tbody = resultsTable.querySelector('tbody');
		tbody.innerHTML = '';

		if (detections.length === 0) {
			showToast('No vegetables detected in image', 'warning');
			return;
		}

		let subtotal = 0;

		// Process each real detection
		for (const detection of detections) {
			const livePrice = detection.live_price;
			const lineTotal = detection.quantity * livePrice;

			resultsData.push({
				vegetable: detection.vegetable,
				quantity: detection.quantity,
				price: livePrice,
				total: lineTotal,
				confidence: detection.confidence,
				source: 'real_detection'
			});

			subtotal += lineTotal;

			// Add to results table with live price indicator
			const row = document.createElement('tr');
			row.innerHTML = `
                <td>
                    ${capitalizeWords(detection.vegetable)}
                    <br><small style="color: #10b981;">🔴 Live Price</small>
                </td>
                <td>${detection.quantity.toFixed(2)}</td>
                <td>
                    ${formatCurrency(livePrice)}
                    <br><small style="color: #666;">Real-time</small>
                </td>
                <td>${formatCurrency(lineTotal)}</td>
                <td>
                    <button onclick="addToBill('${detection.vegetable}', ${detection.quantity}, ${livePrice})" 
                            class="btn btn--primary btn--sm">
                        Add to Bill
                    </button>
                </td>
            `;
			tbody.appendChild(row);
		}

		resultsSubtotal.textContent = formatCurrency(subtotal);

		showToast(`✅ Detected ${detections.length} vegetables with live prices!`, 'success');

	} catch (error) {
		console.error('Detection failed:', error);
		showToast('❌ Detection failed. Please try again.', 'error');
	} finally {
		detectBtn.disabled = false;
		detectBtn.textContent = 'Detect Vegetables';
	}
}

// Enhanced price fetching with live data
async function getVegetablePrice(vegetable, location) {
	try {
		const response = await fetch(`${API_BASE_URL}/price/${vegetable}?location=${location}`);
		if (!response.ok) {
			throw new Error(`Price fetch failed: ${response.status}`);
		}
		const data = await response.json();
		return data.price;
	} catch (error) {
		console.error('Failed to fetch live price:', error);
		showToast('Using estimated price due to API error', 'warning');
		return 30; // Fallback price
	}
}

// Enhanced camera function for mobile
async function startCamera() {
	try {
		// Request camera with mobile-specific constraints
		const constraints = {
			video: {
				width: { ideal: 640, max: 1280 },
				height: { ideal: 480, max: 720 },
				facingMode: 'environment', // Use back camera
				frameRate: { ideal: 30, max: 30 }
			}
		};

		stream = await navigator.mediaDevices.getUserMedia(constraints);

		// Handle mobile-specific video setup
		videoEl.srcObject = stream;
		videoEl.setAttribute('playsinline', true); // Important for iOS
		videoEl.setAttribute('webkit-playsinline', true); // iOS Safari

		await videoEl.play();

		startCameraBtn.disabled = true;
		startCameraBtn.textContent = 'Camera Active';
		captureBtn.disabled = false;

		showToast('Camera started successfully', 'success');

	} catch (error) {
		console.error('Camera access failed:', error);

		// Show mobile-specific error messages
		if (error.name === 'NotAllowedError') {
			showToast('Camera permission denied. Please allow camera access in browser settings.', 'error');
		} else if (error.name === 'NotFoundError') {
			showToast('No camera found on this device.', 'error');
		} else if (error.name === 'NotSecureError') {
			showToast('Camera requires HTTPS. Please use https:// URL.', 'error');
		} else {
			showToast(`Camera error: ${error.message}`, 'error');
		}
	}
}

// Check camera support
function checkCameraSupport() {
	if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
		showToast('Camera not supported on this browser', 'error');
		return false;
	}

	// Check for iOS Safari specific issues
	const isIOS = /iPad|iPhone|iPod/.test(navigator.userAgent);
	const isSafari = /^((?!chrome|android).)*safari/i.test(navigator.userAgent);

	if (isIOS && isSafari) {
		console.log('iOS Safari detected - using compatibility mode');
		return 'ios_safari';
	}

	return true;
}

// Initialize with compatibility check
function init() {
	const cameraSupport = checkCameraSupport();

	if (!cameraSupport) {
		document.getElementById('camera-section').innerHTML = `
            <div class="alert alert-warning">
                <h3>Camera Not Supported</h3>
                <p>Your browser doesn't support camera access. Please try:</p>
                <ul>
                    <li>Using Chrome or Firefox mobile browser</li>
                    <li>Updating your browser to the latest version</li>
                    <li>Using HTTPS instead of HTTP</li>
                </ul>
            </div>
        `;
		return;
	}

	// Continue with normal initialization
	loadLocations();
	loadVegetablesList();
	attachEventListeners();
}

// Optimize image capture for mobile
function captureImage() {
	if (!stream) {
		showToast('Camera not started', 'error');
		return;
	}

	try {
		// Use smaller canvas size for mobile
		const isMobile = window.innerWidth <= 768;
		const maxWidth = isMobile ? 480 : 640;
		const maxHeight = isMobile ? 360 : 480;

		canvasEl.width = Math.min(videoEl.videoWidth, maxWidth);
		canvasEl.height = Math.min(videoEl.videoHeight, maxHeight);

		const ctx = canvasEl.getContext('2d');
		ctx.drawImage(videoEl, 0, 0, canvasEl.width, canvasEl.height);

		// Show canvas, hide video
		canvasEl.style.display = 'block';
		videoEl.style.display = 'none';

		imageCaptured = true;
		detectBtn.disabled = false;

		showToast('Image captured successfully', 'success');

	} catch (error) {
		console.error('Image capture failed:', error);
		showToast('Failed to capture image', 'error');
	}
}

// Detect if running on mobile and adjust API URLs
const isMobile = /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
const isLocal = location.hostname === 'localhost' || location.hostname === '127.0.0.1';

let API_BASE_URL, GO_API_URL;

if (isMobile && isLocal) {
	// Use computer's IP address for mobile access
	API_BASE_URL = 'https://192.168.1.100:8000';  // Replace with your IP
	GO_API_URL = 'https://192.168.1.100:9000';
} else {
	API_BASE_URL = 'http://localhost:8000';
	GO_API_URL = 'http://localhost:9000';
}
