import { fireEvent, render, screen, waitFor, within } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { beforeEach, describe, expect, test, vi } from 'vitest'

import App from './App'

const mockApi = vi.hoisted(() => ({
  health: vi.fn(),
  rules: vi.fn(),
  leaderboard: vi.fn(),
  agents: vi.fn(),
  agent: vi.fn(),
  agentFixtures: vi.fn(),
  featuredFixture: vi.fn(),
  fixture: vi.fn(),
  createAgent: vi.fn(),
  createSubmission: vi.fn(),
  practice: vi.fn(),
  runRound: vi.fn(),
}))

vi.mock('./api', () => ({ api: mockApi }))

const blankBoard = '41523161203939122082683632224299007'
const replay = [
  {
    ply_index: 0,
    active_player: 0,
    board: blankBoard,
    player_locations: [null, null],
    chosen_action: 57,
    chosen_destination: 57,
    legal_actions: [57],
    elapsed_ms: 1,
    stdout_excerpt: '',
    stderr_excerpt: '',
    outcome: null,
  },
  {
    ply_index: 1,
    active_player: 1,
    board: blankBoard,
    player_locations: [57, null],
    chosen_action: null,
    chosen_destination: null,
    legal_actions: [],
    elapsed_ms: 0,
    stdout_excerpt: '',
    stderr_excerpt: '',
    outcome: 'game_over',
  },
]
const rules = {
  game: 'knight_isolation',
  board_width: 11,
  board_height: 9,
  runtime: 'Python 3.12',
  move_budget_ms: 150,
  fixture_games: 2,
  points: { win: 3, draw: 1, loss: 0 },
  engine_version: 'engine-v1',
  ruleset_version: 'rules-v1',
  demo_owner_name: 'oualid',
  minimum_ranked_fixtures: 10,
}
const table = [{
  rank: 1,
  agent_id: 'agent-1',
  agent_name: 'Atlas-AB',
  owner_name: 'oualid',
  submission_id: 'submission-1',
  submission_number: 2,
  fixtures: 12,
  wins: 2,
  draws: 1,
  losses: 0,
  points: 25,
  points_per_fixture: 2.083,
  qualified: true,
  recent_form: ['W', 'D'],
}]
const submission = {
  id: 'submission-1',
  agent_id: 'agent-1',
  number: 2,
  source_hash: 'a'.repeat(64),
  execution_kind: 'docker',
  validation_result: { accepted: true },
  created_at: '2026-07-13T00:00:00Z',
  is_active: true,
}
const agents = [{
  id: 'agent-1',
  owner_name: 'oualid',
  name: 'Atlas-AB',
  active_submission_id: 'submission-1',
  created_at: '2026-07-13T00:00:00Z',
  submissions: [submission, { ...submission, id: 'old', number: 1, is_active: false }],
  record: { fixtures: 3, wins: 2, draws: 1, losses: 0, points: 7 },
}]
const fixtureHistory = [{
  id: 'fixture-1',
  submission_number: 2,
  opponent_name: 'GreedyFox',
  opponent_submission_number: 1,
  outcome: 'W',
  score: '3-0',
  completed_at: '2026-07-13T00:00:00Z',
}]
const fixture = {
  id: 'fixture-1',
  submission_a_id: 'submission-1',
  submission_b_id: 'submission-2',
  agent_a_name: 'Atlas-AB',
  agent_b_name: 'GreedyFox',
  status: 'complete',
  winner_submission_id: 'submission-1',
  is_draw: false,
  points_a: 3,
  points_b: 0,
  games: [1, 2].map((leg) => ({
    id: `game-${leg}`,
    leg_number: leg,
    first_submission_id: leg === 1 ? 'submission-1' : 'submission-2',
    second_submission_id: leg === 1 ? 'submission-2' : 'submission-1',
    winner_submission_id: 'submission-1',
    end_status: 'game_over',
    losing_reason: 'no legal moves',
    replay,
    engine_version: 'engine-v1',
    ruleset_version: 'rules-v1',
  })),
}
const completedPractice = {
  status: 'complete',
  result: { winner: 'submitted' },
  logs: [{ level: 'success', message: 'Real game complete.' }],
  replay,
}

beforeEach(() => {
  window.history.replaceState(null, '', '/')
  vi.clearAllMocks()
  mockApi.rules.mockResolvedValue(rules)
  mockApi.health.mockResolvedValue({
    status: 'ok',
    runner: { available: true, code: 'ready', message: 'Runner ready.' },
  })
  mockApi.leaderboard.mockResolvedValue(table)
  mockApi.agents.mockResolvedValue(agents)
  mockApi.agent.mockResolvedValue(agents[0])
  mockApi.agentFixtures.mockResolvedValue(fixtureHistory)
  mockApi.featuredFixture.mockResolvedValue(fixture)
  mockApi.fixture.mockResolvedValue(fixture)
  mockApi.practice.mockResolvedValue(completedPractice)
  mockApi.runRound.mockResolvedValue({ fixture_ids: ['fixture-1'], status: 'complete' })
  mockApi.createAgent.mockResolvedValue(agents[0])
  mockApi.createSubmission.mockResolvedValue(agents[0])
})

test('route navigation and editor-to-submission handoff preserve code', async () => {
  const user = userEvent.setup()
  render(<App />)
  await user.click(screen.getByRole('button', { name: /Code & Play/ }))
  const editor = screen.getByRole('textbox', { name: 'agent.py editor' })
  fireEvent.change(editor, { target: { value: 'class CustomPlayer:\n    pass' } })
  await user.click(screen.getByRole('button', { name: 'Prepare submission' }))
  expect(await screen.findByRole('heading', { name: 'Submit Agent' })).toBeInTheDocument()
  expect(screen.getByRole('textbox', { name: 'Submission source' })).toHaveValue(
    'class CustomPlayer:\n    pass',
  )
})

test('synchronous practice renders logs and replay controls', async () => {
  const user = userEvent.setup()
  render(<App />)
  await user.click(screen.getByRole('button', { name: /Code & Play/ }))
  await user.click(screen.getByRole('button', { name: 'Run practice' }))
  expect(await screen.findByText('Real game complete.')).toBeInTheDocument()
  expect(mockApi.practice).toHaveBeenCalled()
  expect(screen.getAllByText('complete').length).toBeGreaterThan(0)
  expect(screen.getByRole('slider', { name: 'Replay position' })).toBeInTheDocument()
})

test('submission is validated and activated in one visible action', async () => {
  const user = userEvent.setup()
  render(<App />)
  await user.click(primaryNavigation().getByRole('button', { name: /Submit Agent/ }))
  await user.click(screen.getByRole('button', { name: 'Validate and submit' }))
  expect(await screen.findByText(/Accepted submission 2/)).toBeInTheDocument()
  expect(mockApi.createAgent).toHaveBeenCalled()
})

test('competition round refreshes the leaderboard without opening fixture details', async () => {
  const user = userEvent.setup()
  render(<App />)
  await user.click(primaryNavigation().getByRole('button', { name: /Leaderboard/ }))
  await user.click(screen.getByRole('button', { name: 'Run competition round' }))
  expect(await screen.findByText('Completed 1 fixtures.')).toBeInTheDocument()
  expect(mockApi.runRound).toHaveBeenCalled()
  expect(screen.queryByRole('region', { name: /Game 1.*replay/ })).not.toBeInTheDocument()
})

test('leaderboard summary opens a dedicated agent page with fixture history and replays', async () => {
  const user = userEvent.setup()
  render(<App />)
  await user.click(primaryNavigation().getByRole('button', { name: /Leaderboard/ }))
  expect(screen.queryByText('Recent fixtures')).not.toBeInTheDocument()
  await user.click(screen.getByRole('button', { name: 'Open Agent page' }))
  await waitFor(() => expect(mockApi.agent).toHaveBeenCalledWith('agent-1'))
  expect(window.location.hash).toBe('#/agent/agent-1')
  expect(await screen.findByText('Agent details and immutable competition history for @oualid.')).toBeInTheDocument()
  await user.click(screen.getByRole('tab', { name: 'Fixture history' }))
  await user.click(screen.getByRole('button', { name: /Submission 2 vs GreedyFox v1/ }))
  const gameOne = within(screen.getByRole('region', { name: /Game 1.*replay/ }))
  const gameTwo = within(screen.getByRole('region', { name: /Game 2.*replay/ }))
  expect(gameOne.getByText('Atlas-AB').closest('.replay-player')).toHaveClass('p1')
  expect(gameOne.getByLabelText('Game score 1 to 0')).toBeInTheDocument()
  expect(gameTwo.getByText('Atlas-AB').closest('.replay-player')).toHaveClass('p2')
  expect(gameTwo.getByLabelText('Game score 0 to 1')).toBeInTheDocument()
})

test('My Agents shows active and previous immutable submissions', async () => {
  const user = userEvent.setup()
  render(<App />)
  await user.click(primaryNavigation().getByRole('button', { name: /My Agents/ }))
  expect((await screen.findAllByText('src aaaaaaaaaaaa')).length).toBe(2)
  expect(screen.getByText('previous')).toBeInTheDocument()
  expect(screen.getByText('7 pts')).toBeInTheDocument()
})

describe.each(['timeout', 'invalid_action'])('practice failure %s', (failure) => {
  test('is presented explicitly', async () => {
    mockApi.practice.mockResolvedValue({
      ...completedPractice,
      status: failure,
      logs: [{ level: 'error', message: `Runner ended with ${failure}` }],
    })
    const user = userEvent.setup()
    render(<App />)
    await user.click(screen.getByRole('button', { name: /Code & Play/ }))
    await user.click(screen.getByRole('button', { name: 'Run practice' }))
    expect(await screen.findByText(`Runner ended with ${failure}`)).toBeInTheDocument()
    expect(screen.getAllByText(failure.replace('_', ' ')).length).toBeGreaterThan(0)
  })
})

test('malicious names and logs are rendered as inert text', async () => {
  mockApi.leaderboard.mockResolvedValue([{ ...table[0], agent_name: '<img src=x onerror=alert(1)>' }])
  mockApi.practice.mockResolvedValue({
    ...completedPractice,
    logs: [{ level: 'error', message: '<script>window.pwned=true</script>' }],
  })
  const user = userEvent.setup()
  render(<App />)
  await user.click(screen.getByRole('button', { name: /Code & Play/ }))
  await user.click(screen.getByRole('button', { name: 'Run practice' }))
  expect(await screen.findByText('<script>window.pwned=true</script>')).toBeInTheDocument()
  expect(document.querySelector('script:not([type="module"])')).toBeNull()
  await user.click(primaryNavigation().getByRole('button', { name: /Leaderboard/ }))
  await waitFor(() => expect(screen.getAllByText('<img src=x onerror=alert(1)>').length).toBeGreaterThan(0))
  expect(document.querySelector('img')).toBeNull()
})

function primaryNavigation() {
  return within(screen.getByRole('navigation', { name: 'Primary navigation' }))
}
