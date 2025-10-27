export const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000';

async function request(path, options = {}) {
  const response = await fetch(`${API_BASE}${path}`, {
    headers: {
      'Content-Type': 'application/json',
      ...(options.headers || {}),
    },
    credentials: 'include',
    ...options,
  });
  if (!response.ok) {
    throw new Error(`Request failed: ${response.status}`);
  }
  return response.status === 204 ? null : response.json();
}

export const api = {
  getRulepacks: () => request('/rulepacks/'),
  importRulepack: async (formData, query) => {
    const url = new URL(`${API_BASE}/rulepacks/import`);
    Object.entries(query).forEach(([key, value]) => url.searchParams.append(key, value));
    const response = await fetch(url, {
      method: 'POST',
      body: formData,
    });
    if (!response.ok) {
      throw new Error(await response.text());
    }
    return response.json();
  },
  listRuns: (runId) => request(`/runs/${runId}`),
  startRun: (payload) => request('/runs/', {
    method: 'POST',
    body: JSON.stringify(payload),
  }),
  exportRun: (runId) => request(`/runs/${runId}/export`, { method: 'POST' }),
  settings: () => request('/settings/config'),
  elasticsearch: (index) => request(`/settings/elasticsearch?index=${index || ''}`),
  auditLogs: () => request('/audit/'),
  createRule: (versionId, payload) => request(`/rulepacks/${versionId}/rules`, {
    method: 'POST',
    body: JSON.stringify(payload),
  }),
  updateRule: (ruleId, payload) => request(`/rulepacks/rules/${ruleId}`, {
    method: 'PUT',
    body: JSON.stringify(payload),
  }),
  deleteRule: (ruleId) => request(`/rulepacks/rules/${ruleId}`, { method: 'DELETE' }),
  bulkUpdateRules: (versionId, payload) => request(`/rulepacks/${versionId}/rules/bulk`, {
    method: 'POST',
    body: JSON.stringify(payload),
  }),
  exportRulepack: (versionId) => request(`/rulepacks/${versionId}/export`),
};
