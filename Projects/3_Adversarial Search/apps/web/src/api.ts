import type {
  Agent,
  AgentFixtureHistoryEntry,
  Fixture,
  LeaderboardEntry,
  PracticeResult,
  Rules,
} from './types'

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(path, {
    ...init,
    headers: { 'Content-Type': 'application/json', ...init?.headers },
  })
  if (!response.ok) {
    const payload = (await response.json().catch(() => ({}))) as { detail?: unknown }
    const detail = typeof payload.detail === 'string'
      ? payload.detail
      : JSON.stringify(payload.detail ?? `Request failed (${response.status})`)
    throw new Error(detail)
  }
  return response.json() as Promise<T>
}

export const api = {
  health: () => request<{ status: 'ok'; runner: { available: boolean; code: string; message: string } }>('/api/health'),
  rules: () => request<Rules>('/api/rules'),
  leaderboard: () => request<LeaderboardEntry[]>('/api/leaderboard'),
  agents: () => request<Agent[]>('/api/agents'),
  agent: (agentId: string) => request<Agent>(`/api/agents/${agentId}`),
  agentFixtures: (agentId: string) =>
    request<AgentFixtureHistoryEntry[]>(`/api/agents/${agentId}/fixtures`),
  featuredFixture: () => request<Fixture | null>('/api/fixtures/featured'),
  fixture: (fixtureId: string) => request<Fixture>(`/api/fixtures/${fixtureId}`),
  createAgent: (ownerName: string, name: string, source: string) =>
    request<Agent>('/api/agents', {
      method: 'POST',
      body: JSON.stringify({ owner_name: ownerName, name, source }),
    }),
  createSubmission: (agentId: string, source: string) =>
    request<Agent>(`/api/agents/${agentId}/submissions`, {
      method: 'POST',
      body: JSON.stringify({ source }),
    }),
  practice: (source: string, baseline: string) =>
    request<PracticeResult>('/api/practice', {
      method: 'POST',
      body: JSON.stringify({ source, baseline, seed: 17 }),
    }),
  runRound: () =>
    request<{ fixture_ids: string[]; status: string }>('/api/competition/run-round', {
      method: 'POST',
    }),
}
