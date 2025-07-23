function getBackendURLs() {
	const isProduction = window.location.hostname !== 'localhost';

	if (isProduction) {
		return {
			API_BASE_URL: 'https://veggimlbackend.onrender.com',
			PRICING_API: 'https://veggigoserver.onrender.com'
		};
	} else {
		return {
			API_BASE_URL: 'http://localhost:8000',
			PRICING_API: 'http://localhost:9000'
		};
	}
}

const { API_BASE_URL, PRICING_API } = getBackendURLs();

let videoEl, canvasEl, cameraBtn, captureBtn, detectBtn, resetBtn, fileInput;
let resultsContainer, detectionStatusEl;
let manualEntryBtn, comparePricesBtn;
let imageCaptured = false;
let resultsData = [];
let currentLocation = 'Delhi';

document.addEventListener('DOMContentLoaded', () => {
	initializeElements();
	bindEvents();
	initializeTabs();
	loadSupportedVegetables();
	loadLocations();
});;

function initializeElements() {
	videoEl = document.getElementById('videoElement');
	canvasEl = document.getElementById('imageCanvas');
	captureBtn = document.getElementById('captureBtn');
	resetBtn = document.getElementById('resetBtn');
	fileInput = document.getElementById('fileInput');
	cameraBtn = document.getElementById('cameraBtn');

	detectBtn = document.createElement('button');
	detectBtn.id = 'detectBtn';
	detectBtn.textContent = 'Detect Vegetables';
	detectBtn.className = 'btn btn--primary';
	detectBtn.disabled = true;
	const captureSection = document.querySelector('.capture-section .card__body');
	captureSection.appendChild(detectBtn);

	resultsContainer = document.getElementById('detectionList');
	detectionStatusEl = document.getElementById('detectionStatus');

	manualEntryBtn = document.getElementById('manualEntry');
	comparePricesBtn = document.getElementById('comparePrices');

	console.log('All elements initialized');
}

function bindEvents() {
	if (fileInput) {
		fileInput.addEventListener('change', handleFileUpload);
	}
	if (captureBtn) {
		captureBtn.addEventListener('click', captureImage);
	}
	if (cameraBtn) {
		cameraBtn.addEventListener('click', initializeCamera);
	}
	if (detectBtn) {
		detectBtn.addEventListener('click', detectVegetables);
	}
	if (resetBtn) {
		resetBtn.addEventListener('click', resetDetection);
	}
	if (manualEntryBtn) {
		manualEntryBtn.addEventListener('click', openManualEntry);
	}
	if (comparePricesBtn) {
		comparePricesBtn.addEventListener('click', openPriceComparison);
	}
	console.log('Event listeners bound');
}

function initializeCamera() {
	if (!videoEl || !navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
		console.warn('Camera not supported');
		return;
	}
	navigator.mediaDevices.getUserMedia({ video: { facingMode: 'environment' } })
		.then(stream => {
			videoEl.srcObject = stream;
			videoEl.play();
		})
		.catch(err => console.error('Camera error:', err));
}

function handleFileUpload(e) {
	const file = e.target.files[0];
	if (!file) return;
	const reader = new FileReader();
	reader.onload = () => {
		const img = new Image();
		img.onload = () => {
			canvasEl.width = img.width;
			canvasEl.height = img.height;
			const ctx = canvasEl.getContext('2d');
			ctx.drawImage(img, 0, 0);
			imageCaptured = true;
			detectBtn.disabled = false;
			detectionStatusEl.textContent = 'Image ready. Click “Detect Vegetables.”';
		};
		img.src = reader.result;
	};
	reader.readAsDataURL(file);
}

function captureImage() {
	if (!videoEl || !canvasEl) return;
	const ctx = canvasEl.getContext('2d');
	canvasEl.width = videoEl.videoWidth;
	canvasEl.height = videoEl.videoHeight;
	ctx.drawImage(videoEl, 0, 0);
	imageCaptured = true;
	detectBtn.disabled = false;
	detectionStatusEl.textContent = 'Image captured. Click “Detect Vegetables.”';
}

async function detectVegetables() {
	if (!imageCaptured) {
		alert('Please capture or upload an image first.');
		return;
	}
	detectBtn.disabled = true;
	detectionStatusEl.textContent = 'Detecting...';
	try {
		const blob = await new Promise(res => canvasEl.toBlob(res, 'image/jpeg'));
		const formData = new FormData();
		formData.append('image', blob, 'capture.jpg');
		formData.append('location', currentLocation);

		const resp = await fetch(`${API_BASE_URL}/detect`, {
			method: 'POST',
			body: formData
		});
		if (!resp.ok) throw new Error(`Status ${resp.status}`);
		const { detections, annotated_image } = await resp.json();
		renderDetections(detections, annotated_image);
	} catch (err) {
		console.error(err);
		detectionStatusEl.textContent = 'Detection failed.';
	} finally {
		detectBtn.disabled = false;
	}
}

function displayAnnotatedImage(imageData) {
	const imageContainer = document.getElementById('detectedVegetables')
		|| document.querySelector('.detection-results');
	if (imageContainer) {
		imageContainer.innerHTML = `
      <img 
        src="data:image/jpeg;base64,${imageData}" 
        alt="Annotated Vegetables" 
        style="max-width:100%; height:auto;"
      />
    `;
	}
}

function addResultRow(detection, lineTotal) {
	if (!resultsTable) return;

	const tbody = resultsTable.querySelector('tbody');
	const row = document.createElement('tr');
	row.innerHTML = `
        <td>
            <div class="vegetable-info">
                <span class="veg-name">${detection.vegetable}</span>
                <span class="confidence">${(detection.confidence * 100).toFixed(1)}% sure</span>
            </div>
        </td>
        <td>${detection.quantity} ${detection.unit || 'kg'}</td>
        <td>₹${detection.price_per_kg}</td>
        <td class="price-cell">₹${lineTotal.toFixed(2)}</td>
        <td><span class="live-badge">LIVE</span></td>
    `;
	tbody.appendChild(row);
}

function updateTotals(subtotal) {
	const tax = subtotal * 0.1;
	const total = subtotal + tax;

	const subtotalEl = document.getElementById('subtotal');
	const taxEl = document.getElementById('tax');
	const totalEl = document.getElementById('total');

	if (subtotalEl) subtotalEl.textContent = `₹${subtotal.toFixed(2)}`;
	if (taxEl) taxEl.textContent = `₹${tax.toFixed(2)}`;
	if (totalEl) totalEl.textContent = `₹${total.toFixed(2)}`;
}

function showResults() {
	const resultSection = document.getElementById('detectionResults');
	if (resultSection) {
		resultSection.style.display = 'block';
		resultSection.scrollIntoView({ behavior: 'smooth' });
	}
}

function confirmLocation() {
	if (locationSelect) {
		currentLocation = locationSelect.value;
		document.getElementById('currentLocation').textContent = currentLocation;
		closeModal();
		showToast(`Location set to ${currentLocation}`, 'success');
	}
}


function proceedToCheckout() {
	if (cartData.length === 0) {
		showToast('Cart is empty', 'warning');
		return;
	}

	showToast('Redirecting to checkout...', 'info');

	setTimeout(() => {
		alert('Thank you! This would redirect to payment gateway in a real app.');
	}, 1000);
}

function openManualEntry() {
	const modal = document.getElementById('manualEntryModal');
	if (modal) {
		modal.style.display = 'block';
	}
}

function openPriceComparison() {
	showToast('Loading price comparison...', 'info');

	const comparisonData = resultsData.map(item => ({
		vegetable: item.vegetable,
		currentPrice: item.price,
		locations: ['Delhi', 'Mumbai', 'Bangalore', 'Chennai'].map(loc => ({
			location: loc,
			price: item.price + (Math.random() - 0.5) * 10 // Mock price variation
		}))
	}));

	console.log('Price comparison:', comparisonData);
}

async function loadSupportedVegetables() {
	try {
		const response = await fetch(`${PRICING_API}/api/vegetables`);
		if (response.ok) {
			const data = await response.json();
			console.log('Supported vegetables:', data.vegetables);
		}
	} catch (error) {
		console.error('Failed to load vegetables:', error);
	}
}

async function loadLocations() {
	try {
		const response = await fetch(`${PRICING_API}/api/locations`);
		if (response.ok) {
			const data = await response.json();
			console.log('Supported locations:', data.locations);
		}
	} catch (error) {
		console.error('Failed to load locations:', error);
	}
}

function initializeTabs() {
	const tabBtns = document.querySelectorAll('.tab-btn');
	const tabContents = document.querySelectorAll('.tab-content');
	tabBtns.forEach(btn => btn.addEventListener('click', e => {
		const target = btn.dataset.tab;
		tabBtns.forEach(b => b.classList.toggle('active', b === btn));
		tabContents.forEach(c => c.id === target
			? c.classList.add('active')
			: c.classList.remove('active'));
	}));
}

async function initializeAnalytics() {
	const chartCanvas = document.getElementById('priceChart');
	if (!chartCanvas) return;

	let priceHistory;
	try {
		const res = await fetch(`${PRICING_API}/api/price-history`);
		if (!res.ok) throw new Error(res.statusText);
		priceHistory = await res.json();
		console.log(priceHistory)
	} catch (err) {
		console.error('Failed to load price history:', err);
		return;
	}

	if (priceChart) {
		priceChart.destroy();
	}

	const labels = priceHistory.map(e => e.date);
	const tomatoData = priceHistory.map(e => e.tomato);
	const onionData = priceHistory.map(e => e.onion);
	const potatoData = priceHistory.map(e => e.potato);

	const ctx = chartCanvas.getContext('2d');
	priceChart = new Chart(ctx, {
		type: 'line',
		data: {
			labels,
			datasets: [
				{
					label: 'Tomato',
					data: tomatoData,
					borderColor: '#1FB8CD',
					backgroundColor: 'rgba(31,184,205,0.1)',
					fill: true
				},
				{
					label: 'Onion',
					data: onionData,
					borderColor: '#FFC185',
					backgroundColor: 'rgba(255,193,133,0.1)',
					fill: true
				},
				{
					label: 'Potato',
					data: potatoData,
					borderColor: '#B4413C',
					backgroundColor: 'rgba(180,65,60,0.1)',
					fill: true
				}
			]
		},
		options: {
			responsive: true,
			maintainAspectRatio: false,
			scales: {
				y: {
					beginAtZero: false,
					title: { display: true, text: 'Price (₹/kg)' }
				}
			},
			plugins: {
				title: { display: true, text: 'Vegetable Price Trends' }
			}
		}
	});
}

function resetDetection() {
	imageCaptured = false;
	canvasEl.getContext('2d').clearRect(0, 0, canvasEl.width, canvasEl.height);
	detectBtn.disabled = true;
	fileInput.value = '';
	resultsContainer.innerHTML = '';
	detectionStatusEl.textContent = 'Ready to detect';
}

function renderDetections(detections, annotatedImage) {
	resultsContainer.innerHTML = '';
	if (!detections || !detections.length) {
		resultsContainer.innerHTML = '<p>No vegetables detected.</p>';
		detectionStatusEl.textContent = 'No vegetables found.';
		return;
	}
	detections.forEach(d => {
		const item = document.createElement('div');
		item.className = 'detection-item';
		item.innerHTML = `
            <strong>${d.vegetable}</strong> — ${d.quantity}${d.unit || 'kg'} @ ₹${d.price_per_kg}/kg (${(d.confidence * 100).toFixed(1)}%)
        `;
		resultsContainer.appendChild(item);
	});
	if (annotatedImage) {
		const img = new Image();
		img.src = `data:image/jpeg;base64,${annotatedImage}`;
		img.alt = 'Annotated';
		img.className = 'annotated-image';
		resultsContainer.appendChild(img);
	}
	detectionStatusEl.textContent = `Detected ${detections.length} items.`;
}

function closeModal() {
	const modals = document.querySelectorAll('.modal');
	modals.forEach(modal => {
		modal.style.display = 'none';
	});
}

function showToast(message, type = 'info') {
	const existingToasts = document.querySelectorAll('.toast');
	existingToasts.forEach(toast => toast.remove());

	const toast = document.createElement('div');
	toast.className = `toast toast-${type}`;
	toast.textContent = message;

	Object.assign(toast.style, {
		position: 'fixed',
		top: '20px',
		right: '20px',
		padding: '15px 20px',
		borderRadius: '8px',
		color: 'white',
		fontWeight: 'bold',
		zIndex: '10000',
		opacity: '0',
		transition: 'all 0.3s ease',
		maxWidth: '350px',
		wordWrap: 'break-word',
		backgroundColor: getToastColor(type),
		boxShadow: '0 4px 15px rgba(0,0,0,0.2)'
	});

	document.body.appendChild(toast);

	setTimeout(() => toast.style.opacity = '1', 100);

	setTimeout(() => {
		toast.style.opacity = '0';
		setTimeout(() => {
			if (toast.parentNode) {
				toast.parentNode.removeChild(toast);
			}
		}, 300);
	}, 4000);
}

function getToastColor(type) {
	const colors = {
		'error': '#dc3545',
		'success': '#28a745',
		'warning': '#ffc107',
		'info': '#007bff'
	};
	return colors[type] || '#6c757d';
}

async function checkAPIHealth() {
	try {
		const response = await fetch(`${API_BASE_URL}/health`);
		const health = await response.json();
		console.log('API Status:', health);
		return response.ok;
	} catch (error) {
		console.error('API health check failed:', error);
		return false;
	}
}

setTimeout(async () => {
	const isHealthy = await checkAPIHealth();
	if (isHealthy) {
		showToast('🤖 AI Detection Service Ready!', 'success');
	} else {
		showToast('⚠️ AI Service Unavailable', 'warning');
	}
}, 1000);

window.VegetableDetector = {
	detectVegetables,
	captureImage,
	resetDetection,
	showToast,
	initializeTabs
};

console.log('🥬 Vegetable Detection App Loaded Successfully!');
