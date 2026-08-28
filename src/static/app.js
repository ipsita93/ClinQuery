const $ = (id) => document.getElementById(id);


function escapeHtml(value) {
  if (value === null || value === undefined) return "";

  return String(value)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}


function formatLabel(key) {
  return String(key)
    .replace(/_/g, " ")
    .replace(/\b\w/g, (c) => c.toUpperCase());
}


function formatValue(value) {
  if (value === null || value === undefined) {
    return "";
  }

  if (typeof value === "boolean") {
    return value ? "Yes" : "No";
  }

  return escapeHtml(value);
}


function table(el, rows) {
  if (!rows || !rows.length) {
    el.innerHTML = "<p class='hint'>No rows found.</p>";
    return;
  }

  const cols = Object.keys(rows[0]);

  const head = cols
    .map((c) => `<th>${formatLabel(c)}</th>`)
    .join("");

  const body = rows
    .map(
      (row) => `
        <tr>
          ${cols
            .map((c) => `<td>${formatValue(row[c])}</td>`)
            .join("")}
        </tr>
      `
    )
    .join("");

  el.innerHTML = `
    <div class="table-wrap">
      <table>
        <thead>
          <tr>${head}</tr>
        </thead>
        <tbody>${body}</tbody>
      </table>
    </div>
  `;
}


async function json(url, opts) {
  const res = await fetch(url, opts);

  if (!res.ok) {
    throw new Error(await res.text());
  }

  return res.json();
}


/* ---------------------------------------------------------
   Ask-the-data result rendering
   --------------------------------------------------------- */

function renderToolHeader(payload) {
  return `
    <div class="ask-header">
      <div>
        <div class="ask-label">Matched tool</div>
        <div class="ask-tool-name">${escapeHtml(payload.matched_tool || "—")}</div>
      </div>

      <div class="ask-tool">
        <span>Router</span>
        <strong>Rule-based NLP</strong>
      </div>
    </div>
  `;
}


function renderCriteria(criteria) {
  if (!criteria) return "";

  const labels = [
    criteria.condition &&
      `Condition: ${formatLabel(criteria.condition)}`,

    criteria.county &&
      `County: ${criteria.county}`,

    criteria.medication &&
      `Medication: ${formatLabel(criteria.medication)}`,

    criteria.min_age != null &&
      `Min age: ${criteria.min_age}`,

    criteria.max_age != null &&
      `Max age: ${criteria.max_age}`,

    criteria.visit_type &&
      `Visit: ${formatLabel(criteria.visit_type)}`,
  ].filter(Boolean);

  if (!labels.length) return "";

  return `
    <div class="criteria">
      ${labels
        .map(
          (label) =>
            `<span class="criteria-chip">${escapeHtml(label)}</span>`
        )
        .join("")}
    </div>
  `;
}


function renderResearchCohort(payload, result) {
  const patients = result.results || [];

  return `
    <div class="ask-result">
      ${renderToolHeader(payload)}

      <div class="ask-header">
        <div>
          <div class="ask-count">${result.patients ?? patients.length}</div>
          <div class="ask-label">patients matched</div>
        </div>
      </div>

      ${renderCriteria(result.criteria)}

      ${
        patients.length
          ? `
            <div class="table-wrap">
              <table>
                <thead>
                  <tr>
                    <th>Patient ID</th>
                    <th>Age</th>
                    <th>Gender</th>
                    <th>Race</th>
                    <th>County</th>
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
                          <td>${formatValue(p.person_id)}</td>
                          <td>${formatValue(p.age_years)}</td>
                          <td>${formatValue(p.gender)}</td>
                          <td>${formatValue(p.race)}</td>
                          <td>${formatValue(p.county)}</td>
                          <td>${formatValue(p.visit_count)}</td>
                          <td>${formatValue(p.er_visit_count)}</td>
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
          `
          : "<p class='hint'>No patients matched these criteria.</p>"
      }
    </div>
  `;
}


function renderSummary(payload, result) {
  const rows = Array.isArray(result) ? result : [result];

  if (!rows.length) {
    return `
      <div class="ask-result">
        ${renderToolHeader(payload)}
        <p class="hint">No results found.</p>
      </div>
    `;
  }

  const first = rows[0];

  return `
    <div class="ask-result">
      ${renderToolHeader(payload)}

      <div class="summary-grid">
        ${Object.entries(first)
          .map(
            ([key, value]) => `
              <div class="summary-item">
                <span>${formatLabel(key)}</span>
                <strong>${formatValue(value)}</strong>
              </div>
            `
          )
          .join("")}
      </div>
    </div>
  `;
}


function renderTableResult(payload, rows) {
  return `
    <div class="ask-result">
      ${renderToolHeader(payload)}
      ${tableHtml(rows)}
    </div>
  `;
}


function tableHtml(rows) {
  if (!rows || !rows.length) {
    return "<p class='hint'>No results found.</p>";
  }

  const cols = Object.keys(rows[0]);

  return `
    <div class="table-wrap">
      <table>
        <thead>
          <tr>
            ${cols.map((c) => `<th>${formatLabel(c)}</th>`).join("")}
          </tr>
        </thead>

        <tbody>
          ${rows
            .map(
              (row) => `
                <tr>
                  ${cols
                    .map((c) => `<td>${formatValue(row[c])}</td>`)
                    .join("")}
                </tr>
              `
            )
            .join("")}
        </tbody>
      </table>
    </div>
  `;
}


function renderAsk(payload) {
  const out = $("ask-out");

  out.hidden = false;

  if (payload.error) {
    out.innerHTML = `
      <div class="ask-result">
        ${renderToolHeader(payload)}
        <p class="error">
          ${escapeHtml(payload.error)}
        </p>
      </div>
    `;
    return;
  }

  if (!payload.result) {
    out.innerHTML = `
      <div class="ask-result">
        ${renderToolHeader(payload)}
        <p class="hint">
          ${escapeHtml(payload.message || "No results found.")}
        </p>
      </div>
    `;
    return;
  }

  const result = payload.result;

  /* Research cohort:
     [{"patients": 7, "criteria": {...}, "results": [...]}]
  */
  if (
    Array.isArray(result) &&
    result.length > 0 &&
    result[0] &&
    typeof result[0] === "object" &&
    "patients" in result[0] &&
    "results" in result[0]
  ) {
    out.innerHTML = renderResearchCohort(payload, result[0]);
    return;
  }

  /* Standard list/table results */
  if (Array.isArray(result)) {
    out.innerHTML = renderTableResult(payload, result);
    return;
  }

  /* Single summary object */
  if (typeof result === "object") {
    out.innerHTML = renderSummary(payload, result);
    return;
  }

  out.innerHTML = `
    <div class="ask-result">
      ${renderToolHeader(payload)}
      <div class="summary-grid">
        <div class="summary-item">
          <span>Result</span>
          <strong>${formatValue(result)}</strong>
        </div>
      </div>
    </div>
  `;
}


/* ---------------------------------------------------------
   Ask API
   --------------------------------------------------------- */

async function ask(question) {
  $("question").value = question;

  const out = $("ask-out");

  out.hidden = false;

  out.innerHTML = `
    <div class="ask-result">
      <p class="hint">Running query…</p>
    </div>
  `;

  try {
    const payload = await json("/api/ask", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ question }),
    });

    renderAsk(payload);
  } catch (err) {
    out.innerHTML = `
      <div class="ask-result">
        <p class="error">
          ${escapeHtml(err.message)}
        </p>
      </div>
    `;
  }
}


/* ---------------------------------------------------------
   Dashboard initialization
   --------------------------------------------------------- */

async function init() {
  const [
    overview,
    trends,
    counties,
    quality,
    examples,
  ] = await Promise.all([
    json("/api/overview"),
    json("/api/trends"),
    json("/api/counties"),
    json("/api/quality"),
    json("/api/examples"),
  ]);


  /* KPI cards */

  $("kpis").innerHTML = [
    ["Patients", overview.patients],
    ["T2DM prevalence %", overview.t2dm_pct],
    ["Hypertension prevalence %", overview.htn_pct],
    ["ER visits", overview.er_visits],
    ["Quality flags", overview.data_quality_issues],
  ]
    .map(
      ([label, value]) => `
        <div class="kpi">
          <strong>${formatValue(value)}</strong>
          <span>${escapeHtml(label)}</span>
        </div>
      `
    )
    .join("");


  /* Example question chips */

  $("chips").innerHTML = examples
    .map(
      (q) => `
        <button
          type="button"
          data-q="${escapeHtml(q)}"
        >
          ${escapeHtml(q)}
        </button>
      `
    )
    .join("");


  $("chips").addEventListener("click", (e) => {
    const question = e.target.dataset.q;

    if (question) {
      ask(question);
    }
  });


  /* Condition trend chart */

  const years = [...new Set(trends.map((r) => r.year))];
  const names = [
    ...new Set(trends.map((r) => r.condition_name)),
  ];

  const palette = [
    "#1f4e79",
    "#8c2f39",
    "#2b6e4f",
    "#b5812d",
    "#5b4b8a",
    "#3d7ea6",
  ];

  new Chart($("trend-chart"), {
    type: "line",

    data: {
      labels: years,

      datasets: names.map((name, i) => ({
        label: name,

        data: years.map((year) => {
          const row = trends.find(
            (r) =>
              r.year === year &&
              r.condition_name === name
          );

          return row ? row.condition_events : 0;
        }),

        borderColor: palette[i % palette.length],
        tension: 0.2,
      })),
    },

    options: {
      plugins: {
        legend: {
          position: "bottom",
        },
      },

      responsive: true,
    },
  });


  /* County prevalence chart */

  new Chart($("county-chart"), {
    type: "bar",

    data: {
      labels: counties.map(
        (c) => `${c.county}, ${c.state}`
      ),

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

    options: {
      plugins: {
        legend: {
          position: "bottom",
        },
      },

      responsive: true,
    },
  });


  /* Data quality chart */

  new Chart($("quality-chart"), {
    type: "bar",

    data: {
      labels: quality.map((q) => q.check_name),

      datasets: [
        {
          label: "Issue count",
          data: quality.map((q) => q.issue_count),
          backgroundColor: "#8c2f39",
        },
      ],
    },

    options: {
      indexAxis: "y",

      plugins: {
        legend: {
          display: false,
        },
      },
    },
  });


  /* Existing dashboard tables */

  table($("quality-table"), quality);
  table($("county-table"), counties);


  /* Patient lookup */

  async function loadLookup(e) {
    if (e) {
      e.preventDefault();
    }

    const condition = $("condition").value;
    const county = $("county").value;

    const qs = new URLSearchParams();

    if (condition) {
      qs.set("condition", condition);
    }

    if (county) {
      qs.set("county", county);
    }

    const rows = await json(
      "/api/lookup?" + qs.toString()
    );

    table($("lookup-table"), rows);
  }


  $("lookup-form").addEventListener(
    "submit",
    loadLookup
  );

  await loadLookup();


  /* Ask form */

  $("ask-form").addEventListener(
    "submit",
    async (e) => {
      e.preventDefault();

      const question = $("question").value.trim();

      if (question) {
        await ask(question);
      }
    }
  );
}


/* ---------------------------------------------------------
   Start application
   --------------------------------------------------------- */

init().catch((err) => {
  $("kpis").innerHTML = `
    <p class="hint">
      Could not load data. Build the warehouse first.
      ${escapeHtml(err.message)}
    </p>
  `;
});