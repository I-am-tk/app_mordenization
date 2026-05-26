let currentSnippetId = null;

async function analyzeCode() {
  const language = document.getElementById('language').value;
  const moduleName = document.getElementById('module-name').value.trim();
  const codeSnippet = document.getElementById('code-snippet').value.trim();
  const description = document.getElementById('description').value.trim();
  const framework = document.getElementById('target-framework').value;

  if (!moduleName) { showError('Module name is required.'); return; }
  if (!codeSnippet) { showError('Code snippet is required.'); return; }

  showSpinner('Analysing with GPT-4o...');
  hideError();
  hideSection('analysis-panel');
  hideSection('migration-panel');

  try {
    const res = await fetch(`/analyze?target_framework=${framework}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        language,
        module_name: moduleName,
        code_snippet: codeSnippet,
        description: description || undefined
      })
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || JSON.stringify(data));

    currentSnippetId = data.snippet_id;
    renderAnalysis(data);
    showSection('analysis-panel');
  } catch (e) {
    showError('Analysis failed: ' + e.message);
  } finally {
    hideSpinner();
  }
}

async function migrateCode() {
  if (!currentSnippetId) return;
  const framework = document.getElementById('target-framework').value;

  showSpinner('Generating modernised code...');
  hideSection('migration-panel');

  try {
    const res = await fetch(`/migrate/${currentSnippetId}?target_framework=${framework}`, {
      method: 'POST'
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || JSON.stringify(data));
    renderMigration(data);
    showSection('migration-panel');
  } catch (e) {
    showError('Migration failed: ' + e.message);
  } finally {
    hideSpinner();
  }
}

function renderAnalysis(data) {
  // Risk badge
  const riskBadge = document.getElementById('risk-badge');
  riskBadge.textContent = data.risk_level;
  riskBadge.className = 'badge risk-' + data.risk_level.toLowerCase();

  // Risk reasons
  const reasonsList = document.getElementById('risk-reasons');
  reasonsList.innerHTML = (data.risk_reasons || []).map(r => `<li>${escapeHtml(r)}</li>`).join('');

  // Complexity
  document.getElementById('complexity-score').textContent = data.complexity_score;

  // Patterns
  const patternDiv = document.getElementById('patterns-list');
  if (!data.identified_patterns || data.identified_patterns.length === 0) {
    patternDiv.innerHTML = '<span class="no-patterns">None detected</span>';
  } else {
    patternDiv.innerHTML = data.identified_patterns
      .map(p => `<span class="pattern-tag">${escapeHtml(p)}</span>`)
      .join('');
  }

  // Summary
  document.getElementById('summary-text').textContent = data.summary;
}

function renderMigration(data) {
  // Migration status badge
  const statusBadge = document.getElementById('migration-status-badge');
  statusBadge.textContent = data.migration_status;
  statusBadge.className = 'badge status-' + data.migration_status.toLowerCase().replace(/_/g, '-');

  // Framework tag
  document.getElementById('framework-label').textContent = data.target_framework;

  // Code
  document.getElementById('modernized-code').textContent = data.modernized_code;

  // Checklist
  const list = document.getElementById('migration-checklist');
  list.innerHTML = (data.migration_checklist || [])
    .map(item => `<li>${escapeHtml(item)}</li>`)
    .join('');
}

function escapeHtml(str) {
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

function showSpinner(text) {
  document.getElementById('spinner-text').textContent = text;
  document.getElementById('spinner').classList.remove('hidden');
}

function hideSpinner() {
  document.getElementById('spinner').classList.add('hidden');
}

function showError(msg) {
  const el = document.getElementById('error-banner');
  el.textContent = msg;
  el.classList.remove('hidden');
}

function hideError() {
  document.getElementById('error-banner').classList.add('hidden');
}

function showSection(id) {
  document.getElementById(id).classList.remove('hidden');
}

function hideSection(id) {
  document.getElementById(id).classList.add('hidden');
}
