const $ = (id) => document.getElementById(id);

function table(el, rows) {
  if (!rows || !rows.length) {
    el.innerHTML = "<p class='hint'>No rows.</p>";
    return;
  }
  const cols = Object.keys(rows[0]);
  const head = cols.map((c) => `<th>${c}</th>`).join("");
  const body = rows
    .map((r) => `<tr>${cols.map((c) => `<td>${r[c] ?? ""}</td>`).join("")}</tr>`)
    .join("");
  el.innerHTML = `<div class="table-wrap"><table><thead><tr>${head}</tr></thead><tbody>${body}</tbody></table></div>`;
}

async function json(url, opts) {
  const res = await fetch(url, opts);
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

function renderAsk(payload) {
  const out = $("ask-out");
  out.hidden = false;

  const results = payload.result || [];

  if (!results.length) {
    out.innerHTML = `
      <div class="ask-result">
        <p class="hint">No results found.</p>
      </div>
    `;
    return;
  }

  // Research cohort result
  if (results.length === 1 && results[0].criteria && results[0].results) {
    const result = results[0];
    const criteria = result.criteria || {};
    const patients = result.results || [];

    const criteriaLabels = [
      criteria.condition && `Condition: ${criteria.condition}`,
      criteria.county && `County: ${criteria.county}`,
      criteria.medication && `Medication: ${criteria.medication}`,
      criteria.min_age != null && `Age: ${criteria.min_age}+`,
      criteria.max_age != null && `Age: ≤${criteria.max_age}`,
      criteria.visit_type && `Visit: ${criteria.visit_type}`,
    ].filter(Boolean);

    out.innerHTML = `
      <div class="ask-result">
        <div class="ask-header">
          <div>
            <div class="ask-count">${result.patients}</div>
            <div class="ask-label">patients matched</div>
          </div>
          <div class="ask-tool">
            <span>Tool</span>
            <strong>${payload.matched_tool}</strong>
          </div>
        </div>

        <div class="criteria">
          ${criteriaLabels
            .map((c) => `<span class="criteria-chip">${c}</span>`)
            .join("")}
        </div>

        <div class="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Patient ID</th>
                <th>Age</th>
                <th>Gender</th>
                <th>Race</th>
                <th>Visits</th>
                <th>ER Visits</th>
                <th>Metformin</th>
                <th>Hypertension</th>
                <th>Obesity</th>
                <th>CKD</th>
              </tr>
            </thead>
            <tbody>
              ${patients
                .map(
                  (p) => `
                    <tr>
                      <td>${p.person_id}</td>
                      <td>${p.age_years}</td>
                      <td>${p.gender}</td>
                      <td>${p.race}</td>
                      <td>${p.visit_count}</td>
                      <td>${p.er_visit_count}</td>
                      <td>${p.on_metformin ? "Yes" : "No"}</td>
                      <td>${p.has_hypertension ? "Yes" : "No"}</td>
                      <td>${p.has_obesity ? "Yes" : "No"}</td>
                      <td>${p.has_ckd ? "Yes" : "No"}</td>
                    </tr>
                  `
                )
                .join("")}
            </tbody>
          </table>
        </div>
      </div>
    `;

    return;
  }

  // Generic summary / metric result
  if (results.length === 1) {
    const result = results[0];

    const entries = Object.entries(result);

    out.innerHTML = `
      <div class="ask-result">
        <div class="ask-header">
          <div>
            <div class="ask-label">Result</div>
            <div class="ask-tool">
              <strong>${payload.matched_tool}</strong>
            </div>
          </div>
        </div>

        <div class="criteria">
          ${entries
            .map(
              ([key, value]) =>
                `<span class="criteria-chip"><strong>${key.replaceAll("_", " ")}:</strong> ${value ?? ""}</span>`
            )
            .join("")}
        </div>
      </div>
    `;

    return;
  }

  // Multi-row result: render as a table
  table(out, results);
}

async function ask(question) {
  $("question").value = question;
  const payload = await json("/api/ask", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ question }),
  });
  renderAsk(payload);
}

async function init() {
  const [overview, trends, counties, quality, examples] = await Promise.all([
    json("/api/overview"),
    json("/api/trends"),
    json("/api/counties"),
    json("/api/quality"),
    json("/api/examples"),
  ]);

  $("kpis").innerHTML = [
    ["Patients", overview.patients],
    ["T2DM prevalence %", overview.t2dm_pct],
    ["Hypertension prevalence %", overview.htn_pct],
    ["ER visits", overview.er_visits],
    ["Quality flags", overview.data_quality_issues],
  ]
    .map(([label, value]) => `<div class="kpi"><strong>${value}</strong><span>${label}</span></div>`)
    .join("");

  $("chips").innerHTML = examples
    .map((q) => `<button type="button" data-q="${q.replace(/"/g, "&quot;")}">${q}</button>`)
    .join("");
  $("chips").addEventListener("click", (e) => {
    if (e.target.dataset.q) ask(e.target.dataset.q);
  });

  const years = [...new Set(trends.map((r) => r.year))];
  const names = [...new Set(trends.map((r) => r.condition_name))];
  const palette = ["#1f4e79", "#8c2f39", "#2b6e4f", "#b5812d", "#5b4b8a", "#3d7ea6"];
  new Chart($("trend-chart"), {
    type: "line",
    data: {
      labels: years,
      datasets: names.map((name, i) => ({
        label: name,
        data: years.map((y) => {
          const row = trends.find((r) => r.year === y && r.condition_name === name);
          return row ? row.condition_events : 0;
        }),
        borderColor: palette[i % palette.length],
        tension: 0.2,
      })),
    },
    options: { plugins: { legend: { position: "bottom" } }, responsive: true },
  });

  new Chart($("county-chart"), {
    type: "bar",
    data: {
      labels: counties.map((c) => `${c.county}, ${c.state}`),
      datasets: [
        {
          label: "Hypertension %",
          data: counties.map((c) => c.htn_pct),
          backgroundColor: "#1f4e79",
        },
        {
          label: "T2DM %",
          data: counties.map((c) => c.t2dm_pct),
          backgroundColor: "#8c2f39",
        },
      ],
    },
    options: { plugins: { legend: { position: "bottom" } }, responsive: true },
  });

  new Chart($("quality-chart"), {
    type: "bar",
    data: {
      labels: quality.map((q) => q.check_name),
      datasets: [{ label: "Issue count", data: quality.map((q) => q.issue_count), backgroundColor: "#8c2f39" }],
    },
    options: { indexAxis: "y", plugins: { legend: { display: false } } },
  });

  table($("quality-table"), quality);
  table($("county-table"), counties);

  async function loadLookup(e) {
    if (e) e.preventDefault();
    const condition = $("condition").value;
    const county = $("county").value;
    const qs = new URLSearchParams();
    if (condition) qs.set("condition", condition);
    if (county) qs.set("county", county);
    const rows = await json("/api/lookup?" + qs.toString());
    table($("lookup-table"), rows);
  }
  $("lookup-form").addEventListener("submit", loadLookup);
  await loadLookup();

  $("ask-form").addEventListener("submit", async (e) => {
    e.preventDefault();
    await ask($("question").value);
  });
}

init().catch((err) => {
  $("kpis").innerHTML = `<p class="hint">Could not load data. Build the warehouse first. ${err}</p>`;
});
