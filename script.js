let MASTER = {};
let DETAILS = {};
let searchText = "";
let selectedState = null; 

// Load master + detail data
async function loadAll() {
  MASTER = await fetch("data-master.json").then(r => r.json());
  let detailsLoaded = false;
  try {
    const resp = await fetch("data-detail.json");
    if (resp.ok) {
      DETAILS = await resp.json();
      if (Object.keys(DETAILS).length > 0) {
        detailsLoaded = true;
        console.log("[INFO] Loaded DETAILS from data-detail.json");
      }
    }
  } catch (err) {
    console.warn("[WARN] Could not load data-detail.json:", err);
  }

  // If no detail → run scrapers
  if (!detailsLoaded) {
    alert("data-detail.json not found.\nStarting live web scraping...");
    console.log("[INFO] No detail cache → fetching live data...");

    DETAILS = {};

    await runLoader("loader-master-states.py");
    await runLoader("loader-master-counties.py");
    await runLoader("loader-master-universities.py");

    // Reload after scraping
    try {
      const resp2 = await fetch("data-detail.json");
      if (resp2.ok) DETAILS = await resp2.json();
    } catch (e) {}
  }

  renderLists();
}

// Call backend loader script
async function runLoader(scriptName) {
  console.log("[INFO] Running loader:", scriptName);
  const resp = await fetch("/run/" + encodeURIComponent(scriptName));

  if (!resp.ok) {
    console.error("[ERROR] Loader failed:", scriptName);
    return;
  }

  const data = await resp.json().catch(() => ({}));
  console.log("[INFO] Loader finished:", scriptName, data);
}

// Render lists
function renderLists() {
  const s = document.getElementById("state-list");
  const c = document.getElementById("county-list");
  const u = document.getElementById("uni-list");

  s.innerHTML = "";
  c.innerHTML = "";
  u.innerHTML = "";

  // STATES
  Object.values(MASTER)
    .filter(x => x.type === "State" && matchesFilter(x))
    .forEach(x => addStateItem(s, x));

  // COUNTIES (filtered)
  Object.values(MASTER)
    .filter(x => x.type === "County")
    .filter(x => matchesFilter(x))
    .filter(x => filterCountyBySelectedState(x))
    .forEach(x => addItem(c, x));

  // UNIVERSITIES
  Object.values(MASTER)
    .filter(x => x.type === "University" && matchesFilter(x))
    .forEach(x => addItem(u, x));
}

// Filter counties ONLY when a state is selected
function filterCountyBySelectedState(county) {
  if (!selectedState || !selectedState.abbr) return true;

  const parts = (county.name || "").split(", ");
  if (parts.length < 2) return true;

  return parts[1] === selectedState.abbr;
}

// Add State item with special click handler
function addStateItem(list, item) {
  const li = document.createElement("li");
  const a = document.createElement("a");

  a.textContent = item.name;
  a.href = "#";

  a.onclick = () => {
    selectState(item);
    showDetails(item.id);
  };

  li.appendChild(a);
  list.appendChild(li);
}

// When clicking a state
function selectState(stateItem) {
  selectedState = {
    name: stateItem.name,
    abbr: getStateAbbr(stateItem.name)
  };

  const label = document.getElementById("selected-state-label");
  if (label) {
    label.textContent = `Showing counties in: ${selectedState.name} (${selectedState.abbr || ""})`;
  }

  renderLists();
}

// Convert state full name → abbreviation
function getStateAbbr(fullName) {
  const states = {
    "Alabama": "AL", "Alaska": "AK", "Arizona": "AZ", "Arkansas": "AR",
    "California": "CA", "Colorado": "CO", "Connecticut": "CT",
    "Delaware": "DE", "Florida": "FL", "Georgia": "GA", "Hawaii": "HI",
    "Idaho": "ID", "Illinois": "IL", "Indiana": "IN", "Iowa": "IA",
    "Kansas": "KS", "Kentucky": "KY", "Louisiana": "LA", "Maine": "ME",
    "Maryland": "MD", "Massachusetts": "MA", "Michigan": "MI",
    "Minnesota": "MN", "Mississippi": "MS", "Missouri": "MO",
    "Montana": "MT", "Nebraska": "NE", "Nevada": "NV", "New Hampshire": "NH",
    "New Jersey": "NJ", "New Mexico": "NM", "New York": "NY",
    "North Carolina": "NC", "North Dakota": "ND", "Ohio": "OH",
    "Oklahoma": "OK", "Oregon": "OR", "Pennsylvania": "PA",
    "Rhode Island": "RI", "South Carolina": "SC", "South Dakota": "SD",
    "Tennessee": "TN", "Texas": "TX", "Utah": "UT", "Vermont": "VT",
    "Virginia": "VA", "Washington": "WA", "West Virginia": "WV",
    "Wisconsin": "WI", "Wyoming": "WY",
    "District Of Columbia": "DC",
    "Puerto Rico": "PR",
    "Guam": "GU",
    "United States Virgin Islands": "VI",
    "American Samoa": "AS",
    "Commonwealth Of The Northern Mariana Islands": "MP"
  };

  return states[fullName] || null;
}

// Add county / university items
function addItem(list, item) {
  const li = document.createElement("li");
  const a = document.createElement("a");

  a.textContent = item.name;
  a.href = "#";
  a.onclick = () => showDetails(item.id);

  li.appendChild(a);
  list.appendChild(li);
}

// Search filter logic
function matchesFilter(item) {
  if (!searchText) return true;
  const t = searchText.toLowerCase();
  return (
    (item.name ?? "").toLowerCase().includes(t) ||
    (item.slug ?? "").toLowerCase().includes(t)
  );
}

/////// DETAILS VIEW ///////
function showDetails(id) {
  const d = document.getElementById("details");
  const master = MASTER[id];
  const item = DETAILS[id];

  // If detail missing → show basic info
  if (!item) {
    d.innerHTML = `
      <h3>${master.name}</h3>
      <p><b>Type:</b> ${master.type}</p>
      <p><b>URL:</b> <a href="${master.url}" target="_blank">Open on DataUSA</a></p>
      <p style="color:#c00;"><i>No detailed data yet — scraping will begin if needed.</i></p>
    `;
    return;
  }

  // UNIVERSITY DETAILS
  if (item.type === "University") {
    d.innerHTML = `
      <h3>${item.name}</h3>
      <p><b>Type:</b> University</p>
      <p><b>Undergraduate Tuition:</b> ${item.tuition ?? "N/A"}</p>
      <p><b>Enrolled Students:</b> ${item.enrolled ?? "N/A"}</p>
      <p><b>Average Net Price:</b> ${item.net_price ?? "N/A"}</p>
      <p><b>1 Year Growth:</b> ${item.growth ?? "N/A"}</p>
      <p><b>Acceptance Rate:</b> ${item.acceptance_rate ?? "N/A"}</p>
      <p><b>Full-Time Enrollment:</b> ${item.full_time ?? "N/A"}</p>
      <p><a href="${item.url}" target="_blank">Open on DataUSA</a></p>
    `;
    return;
  }

  // STATE + COUNTY DETAILS
  d.innerHTML = `
    <h3>${item.name}</h3>
    <p><b>Type:</b> ${item.type}</p>
    <p><b>Population:</b> ${item.population ?? "N/A"}</p>
    <p><b>Median Age:</b> ${item.median_age ?? "N/A"}</p>
    <p><b>Income:</b> ${item.income ?? "N/A"}</p>
    <p><b>Poverty Rate:</b> ${item.poverty_rate ?? "N/A"}</p>
    <p><b>Property Value:</b> ${item.property_value ?? "N/A"}</p>
    <p><a href="${item.url}" target="_blank">Open on DataUSA</a></p>
  `;
}

// Search box: typing removes the state filter
document.getElementById("searchBox").addEventListener("input", e => {
  searchText = e.target.value.toLowerCase();

  // Clear selected state when typing
  if (searchText.length > 0) {
    selectedState = null;

    const label = document.getElementById("selected-state-label");
    if (label) label.textContent = "";
  }

  renderLists();
});

// Start app
loadAll();
