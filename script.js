let MASTER = {};
let DETAILS = {};
let searchText = "";

async function loadAll() {
  MASTER = await fetch("data-master.json").then(r => r.json());
  DETAILS = await fetch("data.json").then(r => r.json());
  renderLists();
}

function renderLists() {
  const s = document.getElementById("state-list");
  const c = document.getElementById("county-list");
  const u = document.getElementById("uni-list");
  s.innerHTML = "";
  c.innerHTML = "";
  u.innerHTML = "";

  Object.values(MASTER)
    .filter(x => x.type === "State" && matchesFilter(x))
    .forEach(x => addItem(s, x));

  Object.values(MASTER)
    .filter(x => x.type === "County" && matchesFilter(x))
    .forEach(x => addItem(c, x));

  Object.values(MASTER)
    .filter(x => x.type === "University" && matchesFilter(x))
    .forEach(x => addItem(u, x));
}

function matchesFilter(item) {
  if (!searchText) return true;
  const name = (item.name || "").toLowerCase();
  const slug = (item.slug || "").toLowerCase();
  return name.includes(searchText) || slug.includes(searchText);
}

function addItem(list, item) {
  const li = document.createElement("li");
  const a = document.createElement("a");
  a.textContent = item.name;
  a.href = "#";
  a.onclick = () => showDetails(item.id);
  li.appendChild(a);
  list.appendChild(li);
}

function showDetails(id) {
  const d = document.getElementById("details");
  const item = DETAILS[id];
  if (!item) {
    d.innerHTML = "No details found for this item.";
    return;
  }
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

document.getElementById("searchBox").addEventListener("input", e => {
  searchText = e.target.value.toLowerCase();
  renderLists();
});

loadAll();
