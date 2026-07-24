export type ViewName = 'overview' | 'code' | 'leaderboard' | 'agents' | 'submit'

export interface Rules {
  game: 'knight_isolation'
  board_width: number
  board_height: number
  runtime: string
  move_budget_ms: number
  fixture_games: number
  points: { win: number; draw: number; loss: number }
  engine_version: string
  ruleset_version: string
  demo_owner_name: string
  minimum_ranked_fixtures: number
}

export interface ReplayFrame {
  ply_index: number
  active_player: number
  board: string
  player_locations: [number | null, number | null]
  chosen_action: number | null
  chosen_destination: number | null
  legal_actions: number[]
  elapsed_ms: number
  stdout_excerpt: string
  stderr_excerpt: string
  outcome: string | null
}

export interface Submission {
  id: string
  agent_id: string
  number: number
  source_hash: string
  execution_kind: string
  validation_result: Record<string, unknown>
  created_at: string
  is_active: boolean
}

export interface RecordSummary {
  fixtures: number
  wins: number
  draws: number
  losses: number
  points: number
}

export interface Agent {
  id: string
  owner_name: string
  name: string
  active_submission_id: string | null
  created_at: string
  submissions: Submission[]
  record: RecordSummary | null
}

export interface LeaderboardEntry {
  rank: number | null
  agent_id: string
  agent_name: string
  owner_name: string
  submission_id: string
  submission_number: number
  fixtures: number
  wins: number
  draws: number
  losses: number
  points: number
  points_per_fixture: number
  qualified: boolean
  recent_form: Array<'W' | 'D' | 'L'>
}

export interface AgentFixtureHistoryEntry {
  id: string
  submission_number: number
  opponent_name: string
  opponent_submission_number: number
  outcome: 'W' | 'D' | 'L'
  score: string
  completed_at: string
}

export interface PracticeResult {
  status: string
  result: Record<string, unknown>
  replay: ReplayFrame[]
  logs: Array<{ level: string; message: string }>
}

export interface Game {
  id: string
  leg_number: number
  first_submission_id: string
  second_submission_id: string
  winner_submission_id: string | null
  end_status: string
  losing_reason: string
  replay: ReplayFrame[]
  engine_version: string
  ruleset_version: string
}

export interface Fixture {
  id: string
  submission_a_id: string
  submission_b_id: string
  agent_a_name: string
  agent_b_name: string
  status: string
  winner_submission_id: string | null
  is_draw: boolean
  points_a: number
  points_b: number
  games: Game[]
}
