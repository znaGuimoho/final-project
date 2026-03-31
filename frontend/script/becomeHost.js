const countryPhoneCodes = {
  "Afghanistan": "+93",
  "Albania": "+355",
  "Algeria": "+213",
  "Argentina": "+54",
  "Australia": "+61",
  "Austria": "+43",
  "Bangladesh": "+880",
  "Belgium": "+32",
  "Brazil": "+55",
  "Bulgaria": "+359",
  "Canada": "+1",
  "Chile": "+56",
  "China": "+86",
  "Colombia": "+57",
  "Croatia": "+385",
  "Czech Republic": "+420",
  "Denmark": "+45",
  "Egypt": "+20",
  "Finland": "+358",
  "France": "+33",
  "Germany": "+49",
  "Greece": "+30",
  "Hungary": "+36",
  "Iceland": "+354",
  "India": "+91",
  "Indonesia": "+62",
  "Iran": "+98",
  "Iraq": "+964",
  "Ireland": "+353",
  "Italy": "+39",
  "Japan": "+81",
  "Jordan": "+962",
  "Kenya": "+254",
  "Kuwait": "+965",
  "Lebanon": "+961",
  "Malaysia": "+60",
  "Mexico": "+52",
  "Morocco": "+212",
  "Netherlands": "+31",
  "New Zealand": "+64",
  "Nigeria": "+234",
  "Norway": "+47",
  "Palestine": "+970",
  "Pakistan": "+92",
  "Peru": "+51",
  "Philippines": "+63",
  "Poland": "+48",
  "Portugal": "+351",
  "Qatar": "+974",
  "Romania": "+40",
  "Russia": "+7",
  "Saudi Arabia": "+966",
  "Serbia": "+381",
  "Singapore": "+65",
  "Slovakia": "+421",
  "Slovenia": "+386",
  "South Africa": "+27",
  "South Korea": "+82",
  "Spain": "+34",
  "Sweden": "+46",
  "Switzerland": "+41",
  "Thailand": "+66",
  "Tunisia": "+216",
  "Turkey": "+90",
  "Ukraine": "+380",
  "United Arab Emirates": "+971",
  "United Kingdom": "+44",
  "United States": "+1",
  "Vietnam": "+84"
};

const countrySelect = document.getElementById('country');
const phoneInput = document.getElementById('phone_number');

countrySelect.addEventListener('change', function () {
  const code = countryPhoneCodes[this.value];
  if (!code || !phoneInput) return;

  // Replace existing code prefix or set fresh
  const current = phoneInput.value;
  const hasCode = current.startsWith('+');

  phoneInput.value = hasCode
    ? current.replace(/^\+\d+\s?/, code + ' ')
    : code + ' ' + current;

  phoneInput.focus();
  // Place cursor at end
  phoneInput.setSelectionRange(phoneInput.value.length, phoneInput.value.length);
});
