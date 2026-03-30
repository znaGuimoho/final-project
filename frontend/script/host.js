/* ---------- IMAGE UPLOAD LOGIC (unchanged structure) ---------- */
const uploadArea = document.getElementById('uploadArea');
const fileInput = document.getElementById('image');
const previewContainer = document.getElementById('previewContainer');
const previewImg = document.getElementById('previewImage');
const submitBtn = document.getElementById('submitBtn');
const successMsg = document.getElementById('successMessage');

uploadArea.addEventListener('click', () => fileInput.click());

['dragenter', 'dragover'].forEach(ev =>
  uploadArea.addEventListener(ev, e => {
    e.preventDefault();
    uploadArea.classList.add('dragover');
  })
);

['dragleave', 'drop'].forEach(ev =>
  uploadArea.addEventListener(ev, e => {
    e.preventDefault();
    uploadArea.classList.remove('dragover');
  })
);

uploadArea.addEventListener('drop', e => {
  const files = e.dataTransfer.files;
  if (files.length) {
    fileInput.files = files;
    handleFiles(files);
  }
});

fileInput.addEventListener('change', () => {
  if (fileInput.files.length) handleFiles(fileInput.files);
});

function handleFiles(files) {
  // clear old previews
  previewContainer.innerHTML = '';

  let validCount = 0;

  Array.from(files).forEach(file => {
    if (!file.type.startsWith('image/')) return;
    validCount++;

    const reader = new FileReader();
    reader.onload = e => {
      const img = document.createElement('img');
      img.src = e.target.result;
      img.className = 'preview-image';
      img.alt = file.name;
      previewContainer.appendChild(img);
    };
    reader.readAsDataURL(file);
  });

  if (validCount === 0) return alert('Please select image files only.');

  previewContainer.style.display = 'flex';
  previewContainer.style.flexWrap = 'wrap';
  previewContainer.style.gap = '8px';
  submitBtn.disabled = false;

  if (successMsg) {
    successMsg.style.display = 'flex';
    successMsg.querySelector('span') 
      ? successMsg.querySelector('span').textContent = `${validCount} image${validCount > 1 ? 's' : ''} ready`
      : null;
  }
}

/* ---------- FORM SUBMISSION (real backend) ---------- */
document.getElementById('uploadForm').addEventListener('submit', async e => {
  e.preventDefault();

  submitBtn.disabled = true;
  submitBtn.textContent = 'Uploading...';

  const form = e.target;
  const formData = new FormData(form);

  // include additional inputs from outside the form
  const category = document.getElementById('category')?.value;
  const price = document.getElementById('price')?.value;
  const locationText = document.getElementById('locationText')?.value;
  const details = document.getElementById('details')?.value;
  const lat = document.getElementById('lat')?.value;
  const lng = document.getElementById('lng')?.value;

  if (category) formData.append('category', category);
  if (price) formData.append('price', price);
  if (locationText) formData.append('locationText', locationText);
  if (details) formData.append('details', details);
  if (lat) formData.append('lat', lat);
  if (lng) formData.append('lng', lng);

  try {
    const res = await fetch('/host', {
      method: 'POST',
      body: formData,
    });

    if (res.redirected) {
      // FastAPI redirected (ex: to /login)
      window.location.href = res.url;
    } else if (res.ok) {
      // server responded normally
      successMsg.style.display = 'flex';
      submitBtn.textContent = 'Upload Complete!';
      setTimeout(() => (successMsg.style.display = 'none'), 3000);
    } else {
      // some error from backend
      const errorText = await res.text();
      alert('Server Error: ' + errorText);
      submitBtn.textContent = 'Upload Image';
    }
  } catch (err) {
    console.error('Upload failed:', err);
    alert('Network or server error. Please try again.');
    submitBtn.textContent = 'Upload Image';
  }

  submitBtn.disabled = false;
});

/* ---------- MAP + REVERSE GEOCODING ---------- */
const map = L.map('map').setView([51.505, -0.09], 13);
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
  attribution: '&copy; OpenStreetMap contributors',
}).addTo(map);

let marker;

/* ---- REVERSE GEOCODE (lat,lng → address) ---- */
async function reverseGeocode(lat, lng) {
  try {
    const resp = await fetch(
      `https://nominatim.openstreetmap.org/reverse?format=json&lat=${lat}&lon=${lng}`
    );
    const data = await resp.json();
    return data.display_name || `${lat.toFixed(6)}, ${lng.toFixed(6)}`;
  } catch (e) {
    console.warn('Reverse geocoding failed', e);
    return `${lat.toFixed(6)}, ${lng.toFixed(6)}`;
  }
}

/* ---- CLICK ON MAP ---- */
map.on('click', async e => {
  const { lat, lng } = e.latlng;

  document.getElementById('lat').value = lat.toFixed(6);
  document.getElementById('lng').value = lng.toFixed(6);

  if (marker) marker.setLatLng(e.latlng);
  else marker = L.marker(e.latlng).addTo(map);

  const address = await reverseGeocode(lat, lng);
  document.getElementById('locationText').value = address;
});

/* ---- OPTIONAL: forward geocode when user types address ---- */
document.getElementById('locationText').addEventListener('blur', async () => {
  const addr = encodeURIComponent(document.getElementById('locationText').value.trim());
  if (!addr) return;

  const resp = await fetch(`https://nominatim.openstreetmap.org/search?format=json&q=${addr}`);
  const data = await resp.json();
  if (data && data[0]) {
    const { lat, lon } = data[0];
    map.setView([lat, lon], 15);
    if (marker) marker.setLatLng([lat, lon]);
    else marker = L.marker([lat, lon]).addTo(map);
    document.getElementById('lat').value = lat;
    document.getElementById('lng').value = lon;
  }
});
