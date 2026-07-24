import { useCallback, useEffect, useState, type ReactNode } from 'react'

import { api } from './api'
import { ReplayViewer, type ReplayPlayer } from './components/ReplayBoard'
import type {
  Agent,
  AgentFixtureHistoryEntry,
  Fixture,
  Game,
  LeaderboardEntry,
  PracticeResult,
  Rules,
  ViewName,
} from './types'

type AppView = ViewName | 'agent'

interface AppRoute {
  view: AppView
  agentId?: string
}

const views: Array<{ id: ViewName; label: string; icon: string }> = [
  { id: 'overview', label: 'Overview', icon: '◫' },
  { id: 'code', label: 'Code & Play', icon: '⌨' },
  { id: 'leaderboard', label: 'Leaderboard', icon: '↗' },
  { id: 'agents', label: 'My Agents', icon: '◇' },
  { id: 'submit', label: 'Submit Agent', icon: '⇧' },
]

const starterCode = `class CustomPlayer:
    """Return a legal action before the 150 ms deadline."""

    def __init__(self, player_id=0):
        self.player_id = player_id
        self.context = None

    def get_action(self, state):
        actions = state.actions()
        if not actions:
            return None

        return max(actions, key=lambda action: self.score(state.result(action)))

    def score(self, state):
        own = state.liberties(state.locs[self.player_id])
        opponent = state.liberties(state.locs[1 - self.player_id])
        return len(own) - len(opponent)
`

export default function App() {
  const [route, navigate] = useHashRoute()
  const view = route.view
  const [rules, setRules] = useState<Rules | null>(null)
  const [runner, setRunner] = useState<{ available: boolean; message: string } | null>(null)
  const [leaderboard, setLeaderboard] = useState<LeaderboardEntry[]>([])
  const [agents, setAgents] = useState<Agent[]>([])
  const [featured, setFeatured] = useState<Fixture | null>(null)
  const [preparedSource, setPreparedSource] = useState(starterCode)
  const [submissionTarget, setSubmissionTarget] = useState<string | null>(null)
  const [error, setError] = useState('')

  const refresh = useCallback(async () => {
    try {
      const [nextRules, health, table, localAgents, fixture] = await Promise.all([
        api.rules(),
        api.health(),
        api.leaderboard(),
        api.agents(),
        api.featuredFixture(),
      ])
      setRules(nextRules)
      setRunner(health.runner)
      setLeaderboard(table)
      setAgents(localAgents.filter((agent) => agent.owner_name === nextRules.demo_owner_name))
      setFeatured(fixture)
      setError('')
    } catch (loadError) {
      setError(loadError instanceof Error ? loadError.message : 'The API could not be loaded.')
    }
  }, [])

  useEffect(() => {
    void refresh()
  }, [refresh])

  const prepareSubmission = (source: string) => {
    setPreparedSource(source)
    setSubmissionTarget(null)
    navigate('submit')
  }

  const submitNewVersion = (agentId: string) => {
    setSubmissionTarget(agentId)
    navigate('submit')
  }

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <button className="brand" onClick={() => navigate('overview')}>
          <span className="brand-mark">♞</span>
          <span><strong>Agent Arena</strong><small>Knight Isolation</small></span>
        </button>
        <span className="nav-label">Competition</span>
        <nav aria-label="Primary navigation">
          {views.map((item) => (
            <button
              className={view === item.id ? 'active' : ''}
              key={item.id}
              onClick={() => navigate(item.id)}
              aria-current={view === item.id ? 'page' : undefined}
            >
              <span>{item.icon}</span>{item.label}
            </button>
          ))}
        </nav>
        <div className="runner-note">
          <strong>{runner?.available ? 'Runner ready' : 'Execution unavailable'}</strong>
          <span>{runner?.message ?? 'Checking the Docker runner…'}</span>
        </div>
      </aside>

      <main>
        <header className="topbar">
          <div className="crumb">Knight Isolation / <strong>{views.find((item) => item.id === view)?.label ?? 'Agent'}</strong></div>
          <div className="top-actions">
            <span className="pill"><span className="live-dot" />Points from completed fixtures</span>
            <button className="primary" onClick={() => navigate('code')}>Open Code Lab</button>
          </div>
        </header>

        <div className="content">
          {error ? <div className="error-banner" role="alert">API unavailable: {error}</div> : null}
          {view === 'overview' ? (
            <Overview rules={rules} table={leaderboard} featured={featured} navigate={navigate} />
          ) : null}
          {view === 'code' ? (
            <CodeAndPlay runnerAvailable={runner?.available ?? false} onPrepare={prepareSubmission} />
          ) : null}
          {view === 'leaderboard' ? (
            <Leaderboard
              table={leaderboard}
              minimumFixtures={rules?.minimum_ranked_fixtures ?? 10}
              onOpenAgent={(agentId) => navigate('agent', agentId)}
              onRefresh={refresh}
            />
          ) : null}
          {view === 'agent' && route.agentId ? (
            <AgentPage agentId={route.agentId} onBack={() => navigate('leaderboard')} />
          ) : null}
          {view === 'agents' ? (
            <MyAgents agents={agents} onNewSubmission={submitNewVersion} onRefresh={refresh} />
          ) : null}
          {view === 'submit' ? (
            <SubmitAgent
              agents={agents}
              initialOwner={rules?.demo_owner_name ?? 'oualid'}
              initialSource={preparedSource}
              initialTarget={submissionTarget}
              onComplete={refresh}
            />
          ) : null}
        </div>
      </main>

      <nav className="mobile-nav" aria-label="Mobile navigation">
        {views.map((item) => (
          <button className={view === item.id ? 'active' : ''} key={item.id} onClick={() => navigate(item.id)}>
            <span>{item.icon}</span>{item.label.split(' ')[0]}
          </button>
        ))}
      </nav>
    </div>
  )
}

function Overview({
  rules,
  table,
  featured,
  navigate,
}: {
  rules: Rules | null
  table: LeaderboardEntry[]
  featured: Fixture | null
  navigate: (view: ViewName) => void
}) {
  return (
    <section aria-labelledby="overview-title">
      <div className="hero">
        <div className="hero-copy">
          <span className="eyebrow">One game · one points table</span>
          <h1 id="overview-title">Submit once. Your Knight Isolation agent keeps competing.</h1>
          <p>Write a Python agent, test it against a trusted baseline, submit one immutable version, and inspect every mirrored fixture.</p>
          <div className="actions">
            <button className="primary" onClick={() => navigate('code')}>Write an agent</button>
            <button className="secondary" onClick={() => navigate('leaderboard')}>View leaderboard</button>
          </div>
        </div>
        <aside className="hero-side">
          <span className="eyebrow">Fixed competition rules</span>
          <div className="metric-grid">
            <Metric value="11 × 9" label="board" />
            <Metric value={`${rules?.move_budget_ms ?? 150} ms`} label="per move" />
            <Metric value="3 / 1 / 0" label="fixture points" />
          </div>
          <div className="callout">Every ranked fixture contains two games. Player order swaps, then points are calculated from the two winners.</div>
        </aside>
      </div>

      <div className="steps-grid section-gap">
        {[
          ['01', 'Code', 'Implement CustomPlayer.get_action(state).'],
          ['02', 'Practice', 'Run one real game against a baseline.'],
          ['03', 'Submit', 'Validation succeeds before source is stored.'],
          ['04', 'Compete', 'Mirrored games produce fixture points.'],
        ].map(([number, title, copy]) => (
          <article className="simple-step" key={number}><span>{number}</span><strong>{title}</strong><p>{copy}</p></article>
        ))}
      </div>

      <SectionHead title="Featured fixture" copy="A completed fixture from the authoritative engine." />
      <div className="feature-grid">
        <ReplayViewer
          replay={featured?.games[0]?.replay}
          title={featured ? `${featured.agent_a_name} vs ${featured.agent_b_name}` : 'Waiting for a fixture'}
          players={featured?.games[0] ? fixtureReplayPlayers(featured, featured.games[0]) : undefined}
        />
        <FixtureSummary fixture={featured} />
      </div>

      <SectionHead title="Top of the table" copy="Qualified agents are ranked by points per fixture, then points, wins, and name." />
      <LeaderboardTable rows={table.slice(0, 4)} />
    </section>
  )
}

function CodeAndPlay({
  runnerAvailable,
  onPrepare,
}: {
  runnerAvailable: boolean
  onPrepare: (source: string) => void
}) {
  const [source, setSource] = useState(starterCode)
  const [baseline, setBaseline] = useState('greedy')
  const [practice, setPractice] = useState<PracticeResult | null>(null)
  const [running, setRunning] = useState(false)
  const [tab, setTab] = useState<'goal' | 'rules' | 'api'>('goal')

  const runPractice = async () => {
    setRunning(true)
    setPractice(null)
    try {
      setPractice(await api.practice(source, baseline))
    } catch (runError) {
      setPractice({
        status: 'exception',
        result: {},
        replay: [],
        logs: [{ level: 'error', message: runError instanceof Error ? runError.message : 'Practice request failed.' }],
      })
    } finally {
      setRunning(false)
    }
  }

  const status = running ? 'running' : practice?.status ?? 'idle'
  const lines = source.split('\n').map((_, index) => index + 1).join('\n')
  return (
    <section aria-labelledby="code-title">
      <SectionHead title="Code & Play" copy="Edit one file, run one synchronous practice game, and inspect its replay." id="code-title" />
      <div className="workspace">
        <div className="workspace-left">
          <div className="game-pane">
            <div className="match-head">
              <div><strong>YourAgent vs {titleCase(baseline)}</strong><span>Practice · seed 17 · no table points</span></div>
              <span className={`status ${statusTone(status)}`}>{status.replace('_', ' ')}</span>
            </div>
            <ReplayViewer
              replay={practice?.replay}
              title="Practice game"
              players={practiceReplayPlayers(practice, baseline)}
            />
          </div>
          <div className="problem-pane">
            <div className="tabs" role="tablist" aria-label="Problem guide">
              {(['goal', 'rules', 'api'] as const).map((name) => (
                <button role="tab" aria-selected={tab === name} className={tab === name ? 'active' : ''} key={name} onClick={() => setTab(name)}>{titleCase(name)}</button>
              ))}
            </div>
            {tab === 'goal' ? <Problem title="Block your opponent before they block you." items={['Choose any legal opening cell.', 'Then move by a chess-knight offset.', 'A player without a legal move loses.']} /> : null}
            {tab === 'rules' ? <Problem title="Fixture rules" items={['11 × 9 immutable bitboard.', '150 ms wall-clock decision budget.', 'Two games with order swapped.', '3 / 1 / 0 fixture points.']} /> : null}
            {tab === 'api' ? <Problem title="Agent contract" items={['class CustomPlayer', 'get_action(self, state)', 'Return an action or call self.queue.put(action).', 'self.context lasts for one game.']} /> : null}
          </div>
        </div>
        <div className="workspace-right">
          <div className="editor-pane">
            <div className="editor-toolbar">
              <div><strong>agent.py</strong><span>Python 3.12</span></div>
              <div className="controls">
                <select aria-label="Baseline opponent" value={baseline} onChange={(event) => setBaseline(event.target.value)}>
                  <option value="random">Random</option>
                  <option value="greedy">Greedy</option>
                  <option value="minimax">Minimax</option>
                </select>
                <button className="ghost" onClick={() => setSource(starterCode)}>Reset</button>
              </div>
            </div>
            <div className="editor-wrap">
              <pre aria-hidden="true" className="line-numbers">{lines}</pre>
              <textarea aria-label="agent.py editor" spellCheck="false" value={source} onChange={(event) => setSource(event.target.value)} />
            </div>
          </div>
          <div className="console-pane">
            <div className="console-toolbar"><strong>Runner output</strong><span className={`status ${statusTone(status)}`}>{status.replace('_', ' ')}</span></div>
            <div className="console-body" aria-live="polite">
              {!runnerAvailable ? <p className="log-warn">Docker is unavailable. Submitted source will not execute.</p> : null}
              {!practice && !running ? <p>Choose a baseline and run one practice game.</p> : null}
              {running ? <p>Waiting for the isolated game to finish…</p> : null}
              {practice?.logs.map((log, index) => <p className={`log-${log.level}`} key={`${index}-${log.message}`}>{log.message}</p>)}
            </div>
            <div className="workspace-actions">
              <button className="primary" disabled={running} onClick={() => void runPractice()}>Run practice</button>
              <button className="secondary" disabled={running} onClick={() => void runPractice()}>Replay same</button>
              <button className="ghost" onClick={() => onPrepare(source)}>Prepare submission</button>
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}

function Leaderboard({
  table,
  minimumFixtures,
  onOpenAgent,
  onRefresh,
}: {
  table: LeaderboardEntry[]
  minimumFixtures: number
  onOpenAgent: (agentId: string) => void
  onRefresh: () => Promise<void>
}) {
  const [selectedId, setSelectedId] = useState<string | null>(null)
  const [runningRound, setRunningRound] = useState(false)
  const [message, setMessage] = useState('')
  const selected = table.find((entry) => entry.submission_id === selectedId) ?? table[0]

  const runCompetition = async () => {
    setRunningRound(true)
    setMessage('Running every mirrored fixture. This request stays open until the round finishes.')
    try {
      const result = await api.runRound()
      setMessage(`Completed ${result.fixture_ids.length} fixtures.`)
      await onRefresh()
    } catch (roundError) {
      setMessage(roundError instanceof Error ? roundError.message : 'The round failed.')
    } finally {
      setRunningRound(false)
    }
  }

  return (
    <section aria-labelledby="leaderboard-title">
      <SectionHead
        id="leaderboard-title"
        title="Knight Isolation leaderboard"
        copy="Points are calculated directly from completed mirrored fixtures."
        action={<button className="primary" disabled={runningRound} onClick={() => void runCompetition()}>{runningRound ? 'Running round…' : 'Run competition round'}</button>}
      />
      {message ? <div className="callout" aria-live="polite">{message}</div> : null}
      <div className="ranking-note">
        <strong>Official ranking starts at {minimumFixtures} fixtures.</strong>
        <span>Qualified agents are ordered by points per fixture, then total points, wins, and agent name. New agents remain provisional until they reach the threshold.</span>
      </div>
      <div className="leader-layout">
        <LeaderboardTable rows={table} onSelect={(entry) => setSelectedId(entry.submission_id)} selectedId={selected?.submission_id} />
        <aside className="card agent-profile">
          {selected ? (
            <>
              <h2>{selected.agent_name}</h2>
              <span className="developer">@{selected.owner_name}</span>
              <div className="record-grid">
                <Metric value={String(selected.points)} label="points" />
                <Metric value={String(selected.wins)} label="wins" />
                <Metric value={String(selected.draws)} label="draws" />
                <Metric value={String(selected.losses)} label="losses" />
              </div>
              <button className="secondary" onClick={() => onOpenAgent(selected.agent_id)}>
                Open Agent page
              </button>
            </>
          ) : <p>Seed the database to populate the table.</p>}
        </aside>
      </div>
    </section>
  )
}

function AgentPage({ agentId, onBack }: { agentId: string; onBack: () => void }) {
  const [agent, setAgent] = useState<Agent | null>(null)
  const [history, setHistory] = useState<AgentFixtureHistoryEntry[]>([])
  const [selectedFixture, setSelectedFixture] = useState<Fixture | null>(null)
  const [tab, setTab] = useState<'submissions' | 'fixtures'>('submissions')
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    let active = true
    setLoading(true)
    setSelectedFixture(null)
    void Promise.all([api.agent(agentId), api.agentFixtures(agentId)])
      .then(([nextAgent, nextHistory]) => {
        if (!active) return
        setAgent(nextAgent)
        setHistory(nextHistory)
        setError('')
      })
      .catch((loadError: unknown) => {
        if (active) setError(loadError instanceof Error ? loadError.message : 'Agent could not be loaded.')
      })
      .finally(() => {
        if (active) setLoading(false)
      })
    return () => { active = false }
  }, [agentId])

  const loadFixture = async (fixtureId: string) => {
    try {
      setSelectedFixture(await api.fixture(fixtureId))
      setError('')
    } catch (fixtureError) {
      setError(fixtureError instanceof Error ? fixtureError.message : 'Fixture could not be loaded.')
    }
  }

  if (loading) return <div className="card empty-state">Loading agent pageâ€¦</div>
  if (!agent) {
    return <div className="card empty-state"><p>{error || 'Agent was not found.'}</p><button className="secondary" onClick={onBack}>Back to leaderboard</button></div>
  }

  const record = agent.record
  const pointsPerFixture = record?.fixtures ? record.points / record.fixtures : 0
  return (
    <section aria-labelledby="agent-page-title">
      <SectionHead
        id="agent-page-title"
        title={agent.name}
        copy={`Agent details and immutable competition history for @${agent.owner_name}.`}
        action={<button className="ghost" onClick={onBack}>Back to leaderboard</button>}
      />
      {error ? <div className="error-banner" role="alert">{error}</div> : null}
      <div className="card agent-page-summary">
        <div><span className="status active">{agent.active_submission_id ? 'Active' : 'Inactive'}</span><h2>{agent.name}</h2><span className="developer">@{agent.owner_name}</span></div>
        <div className="record-grid">
          <Metric value={(record?.points ?? 0).toString()} label="points" />
          <Metric value={pointsPerFixture.toFixed(3)} label="PPF" />
          <Metric value={`${record?.wins ?? 0}-${record?.draws ?? 0}-${record?.losses ?? 0}`} label="W-D-L" />
          <Metric value={(record?.fixtures ?? 0).toString()} label="fixtures" />
        </div>
      </div>
      <div className="tabs agent-page-tabs" role="tablist" aria-label="Agent details">
        <button role="tab" aria-selected={tab === 'submissions'} className={tab === 'submissions' ? 'active' : ''} onClick={() => setTab('submissions')}>Submission history</button>
        <button role="tab" aria-selected={tab === 'fixtures'} className={tab === 'fixtures' ? 'active' : ''} onClick={() => setTab('fixtures')}>Fixture history</button>
      </div>
      {tab === 'submissions' ? (
        <div className="card version-list agent-page-list">
          {agent.submissions.map((submission) => (
            <div className="version-row" key={submission.id}>
              <strong>Submission {submission.number}</strong>
              <span><code>src {submission.source_hash}</code><small>{submission.execution_kind} Â· {submission.validation_result.accepted ? 'validated' : 'trusted'} Â· {new Date(submission.created_at).toLocaleString()}</small></span>
              <span className={`status ${submission.is_active ? 'active' : 'draft'}`}>{submission.is_active ? 'active' : 'previous'}</span>
            </div>
          ))}
        </div>
      ) : (
        <div className="card agent-page-list fixture-history">
          {history.map((fixture) => (
            <button className="event-row fixture-link" key={fixture.id} onClick={() => void loadFixture(fixture.id)}>
              <span className={`form-dot ${fixture.outcome}`}>{fixture.outcome}</span>
              <strong>Submission {fixture.submission_number} vs {fixture.opponent_name} v{fixture.opponent_submission_number}</strong>
              <span>{fixture.score}</span>
              <small>{new Date(fixture.completed_at).toLocaleString()}</small>
            </button>
          ))}
          {!history.length ? <span className="tiny">No completed fixtures yet.</span> : null}
        </div>
      )}
      {selectedFixture ? <FixtureReplays fixture={selectedFixture} /> : null}
    </section>
  )
}

function MyAgents({
  agents,
  onNewSubmission,
  onRefresh,
}: {
  agents: Agent[]
  onNewSubmission: (id: string) => void
  onRefresh: () => Promise<void>
}) {
  return (
    <section aria-labelledby="my-agents-title">
      <SectionHead
        id="my-agents-title"
        title="My Agents"
        copy="Each source submission is immutable; the newest accepted submission is active."
        action={<button className="ghost" onClick={() => void onRefresh()}>Refresh</button>}
      />
      <div className="agent-grid">
        {agents.map((agent) => (
          <article className="card agent-card" key={agent.id}>
            <div className="card-title">
              <div><span className="status active">{agent.active_submission_id ? 'Active' : 'No submission'}</span><h2>{agent.name}</h2><span className="developer">@{agent.owner_name}</span></div>
              <strong className="points">{agent.record?.points ?? 0} pts</strong>
            </div>
            <div className="record-grid">
              <Metric value={`${agent.record?.wins ?? 0}-${agent.record?.draws ?? 0}-${agent.record?.losses ?? 0}`} label="W-D-L" />
              <Metric value={String(agent.submissions.length)} label="submissions" />
              <Metric value={String(agent.record?.fixtures ?? 0)} label="fixtures" />
            </div>
            <div className="version-list">
              {agent.submissions.map((submission) => (
                <div className="version-row" key={submission.id}>
                  <strong>v{submission.number}</strong>
                  <span><code>src {submission.source_hash.slice(0, 12)}</code><small>{submission.validation_result.accepted ? 'validated' : 'trusted built-in'}</small></span>
                  <span className={`status ${submission.is_active ? 'active' : 'draft'}`}>{submission.is_active ? 'active' : 'previous'}</span>
                </div>
              ))}
            </div>
            <button className="secondary" onClick={() => onNewSubmission(agent.id)}>Submit new version</button>
          </article>
        ))}
        {!agents.length ? <div className="card empty-state">No agents yet. Create one in Submit Agent.</div> : null}
      </div>
    </section>
  )
}

function SubmitAgent({
  agents,
  initialOwner,
  initialSource,
  initialTarget,
  onComplete,
}: {
  agents: Agent[]
  initialOwner: string
  initialSource: string
  initialTarget: string | null
  onComplete: () => Promise<void>
}) {
  const [mode, setMode] = useState<'new' | 'submission'>(initialTarget ? 'submission' : 'new')
  const [owner, setOwner] = useState(initialOwner)
  const [name, setName] = useState('MyKnightAgent')
  const [target, setTarget] = useState(initialTarget ?? agents[0]?.id ?? '')
  const [source, setSource] = useState(initialSource)
  const [submitting, setSubmitting] = useState(false)
  const [result, setResult] = useState<Agent | null>(null)
  const [message, setMessage] = useState('Validation happens before a permanent Submission is created.')

  useEffect(() => {
    if (initialTarget) {
      setMode('submission')
      setTarget(initialTarget)
    }
  }, [initialTarget])

  const submit = async () => {
    setSubmitting(true)
    setResult(null)
    setMessage('Checking the Python contract, isolated sample actions, and Greedy scrimmage…')
    try {
      const accepted = mode === 'new'
        ? await api.createAgent(owner, name, source)
        : await api.createSubmission(target, source)
      setResult(accepted)
      const active = accepted.submissions.find((item) => item.is_active)
      setMessage(`Accepted submission ${active?.number ?? ''}. It is now the active competitor.`)
      await onComplete()
    } catch (submitError) {
      setMessage(submitError instanceof Error ? submitError.message : 'Submission failed.')
    } finally {
      setSubmitting(false)
    }
  }

  const loadFile = async (file: File | undefined) => {
    if (file) setSource(await file.text())
  }

  const active = result?.submissions.find((item) => item.is_active)
  return (
    <section aria-labelledby="submit-title">
      <SectionHead id="submit-title" title="Submit Agent" copy="A successful validation immediately creates the active immutable submission." />
      <div className="submission-layout">
        <div className="card">
          <div className="mode-tabs">
            <button className={mode === 'new' ? 'active' : ''} onClick={() => setMode('new')}>New agent</button>
            <button className={mode === 'submission' ? 'active' : ''} onClick={() => setMode('submission')}>New submission</button>
          </div>
          <div className="form-grid">
            {mode === 'new' ? (
              <>
                <label>Owner name<input value={owner} onChange={(event) => setOwner(event.target.value)} /></label>
                <label>Agent name<input value={name} onChange={(event) => setName(event.target.value)} /></label>
              </>
            ) : (
              <label className="full">Agent<select value={target} onChange={(event) => setTarget(event.target.value)}><option value="">Choose an agent</option>{agents.map((agent) => <option value={agent.id} key={agent.id}>{agent.name}</option>)}</select></label>
            )}
            <label>Game<div className="fixed-field">Knight Isolation</div></label>
            <label>Runtime<div className="fixed-field">Python 3.12 · 150 ms</div></label>
            <label className="full">Upload agent.py<input type="file" accept=".py,text/x-python" onChange={(event) => void loadFile(event.target.files?.[0])} /></label>
            <label className="full">Source<textarea className="submission-source" aria-label="Submission source" value={source} onChange={(event) => setSource(event.target.value)} /></label>
          </div>
          <div className="actions">
            <button className="primary" disabled={submitting || (mode === 'submission' && !target)} onClick={() => void submit()}>{submitting ? 'Validating…' : 'Validate and submit'}</button>
          </div>
        </div>
        <aside className="card submission-preview">
          <span className={`status ${active ? 'active' : submitting ? 'draft' : 'draft'}`}>{active ? 'accepted' : submitting ? 'validating' : 'ready'}</span>
          <h2>Submission result</h2>
          <p aria-live="polite">{message}</p>
          {active ? (
            <div className="hash-preview">
              <code>submission {active.id}</code>
              <code>source {active.source_hash}</code>
              <details><summary>Validation result</summary><pre>{JSON.stringify(active.validation_result, null, 2)}</pre></details>
            </div>
          ) : null}
        </aside>
      </div>
    </section>
  )
}

function FixtureSummary({ fixture }: { fixture: Fixture | null }) {
  return (
    <div className="card fixture-summary">
      <span className={`status ${fixture?.status === 'complete' ? 'active' : 'draft'}`}>{fixture?.status ?? 'Not seeded'}</span>
      <h2>{fixture ? `${fixture.agent_a_name} ${fixture.points_a}-${fixture.points_b} ${fixture.agent_b_name}` : 'Seed data to see a fixture'}</h2>
      <p>Two games, order swapped. Points are derived from the recorded winners.</p>
      {fixture?.games.map((game) => (
        <div className="event-row" key={game.id}>
          <span>Game {game.leg_number}</span>
          <strong>{game.end_status.replace('_', ' ')}</strong>
          <small>{Math.max(0, game.replay.length - 1)} plies</small>
        </div>
      ))}
    </div>
  )
}

function FixtureReplays({ fixture }: { fixture: Fixture }) {
  return (
    <section className="section-gap" aria-label="Selected fixture replays">
      <SectionHead title={`${fixture.agent_a_name} ${fixture.points_a}-${fixture.points_b} ${fixture.agent_b_name}`} copy="Both mirrored games from the selected fixture." />
      <div className="feature-grid">
        {fixture.games.map((game) => (
          <ReplayViewer
            key={game.id}
            replay={game.replay}
            title={`Game ${game.leg_number} · ${game.end_status.replace('_', ' ')}`}
            players={fixtureReplayPlayers(fixture, game)}
          />
        ))}
      </div>
    </section>
  )
}

function LeaderboardTable({
  rows,
  onSelect,
  selectedId,
}: {
  rows: LeaderboardEntry[]
  onSelect?: (entry: LeaderboardEntry) => void
  selectedId?: string
}) {
  return (
    <div className="table-card">
      <table>
        <thead><tr><th>Rank</th><th>Agent submission</th><th>Owner</th><th>Fixtures</th><th>PPF</th><th>W</th><th>D</th><th>L</th><th>Points</th><th>Form</th></tr></thead>
        <tbody>
          {rows.map((entry) => (
            <tr className={selectedId === entry.submission_id ? 'selected' : ''} key={entry.submission_id} onClick={() => onSelect?.(entry)} tabIndex={onSelect ? 0 : undefined} onKeyDown={(event) => { if (onSelect && (event.key === 'Enter' || event.key === ' ')) onSelect(entry) }}>
              <td className="rank">{entry.rank ?? 'â€”'}</td>
              <td><strong>{entry.agent_name} v{entry.submission_number}</strong>{!entry.qualified ? <small className="provisional">provisional</small> : null}</td>
              <td><span className="developer">@{entry.owner_name}</span></td>
              <td>{entry.fixtures}</td><td>{entry.points_per_fixture.toFixed(3)}</td><td>{entry.wins}</td><td>{entry.draws}</td><td>{entry.losses}</td>
              <td className="points">{entry.points}</td>
              <td><div className="form-row">{entry.recent_form.map((outcome, index) => <span className={`form-dot ${outcome}`} key={`${outcome}-${index}`}>{outcome}</span>)}</div></td>
            </tr>
          ))}
        </tbody>
      </table>
      {!rows.length ? <div className="empty-state">No completed standings yet. Run the seed command.</div> : null}
    </div>
  )
}

function SectionHead({
  title,
  copy,
  id,
  action,
}: {
  title: string
  copy: string
  id?: string
  action?: ReactNode
}) {
  return <div className="section-head"><div><h2 id={id}>{title}</h2><p>{copy}</p></div>{action}</div>
}

function Metric({ value, label }: { value: string; label: string }) {
  return <div className="metric"><strong>{value}</strong><span>{label}</span></div>
}

function Problem({ title, items }: { title: string; items: string[] }) {
  return <div><h3>{title}</h3><ul>{items.map((item) => <li key={item}>{item}</li>)}</ul></div>
}

function useHashRoute(): [AppRoute, (view: AppView, agentId?: string) => void] {
  const read = (): AppRoute => {
    const value = window.location.hash.replace('#/', '')
    const [view, encodedId] = value.split('/')
    if (view === 'agent' && encodedId) return { view: 'agent', agentId: decodeURIComponent(encodedId) }
    if (views.some((item) => item.id === view)) return { view: view as ViewName }
    return { view: 'overview' }
  }
  const [route, setRoute] = useState<AppRoute>(read)
  useEffect(() => {
    const onHash = () => setRoute(read())
    window.addEventListener('hashchange', onHash)
    return () => window.removeEventListener('hashchange', onHash)
  }, [])
  return [route, (next, agentId) => {
    window.location.hash = next === 'agent' && agentId
      ? `/agent/${encodeURIComponent(agentId)}`
      : `/${next}`
    setRoute(read())
  }]
}

function statusTone(status: string): string {
  if (['complete', 'accepted', 'active'].includes(status)) return 'active'
  if (['timeout', 'invalid_action', 'exception', 'invalid', 'runner_unavailable'].includes(status)) return 'danger'
  return 'draft'
}

function titleCase(value: string): string {
  return value.charAt(0).toUpperCase() + value.slice(1)
}

function fixtureReplayPlayers(fixture: Fixture, game: Game): [ReplayPlayer, ReplayPlayer] {
  const nameFor = (submissionId: string) => (
    submissionId === fixture.submission_a_id ? fixture.agent_a_name : fixture.agent_b_name
  )
  return [
    {
      name: nameFor(game.first_submission_id),
      score: game.winner_submission_id === game.first_submission_id ? 1 : 0,
    },
    {
      name: nameFor(game.second_submission_id),
      score: game.winner_submission_id === game.second_submission_id ? 1 : 0,
    },
  ]
}

function practiceReplayPlayers(
  practice: PracticeResult | null,
  baseline: string,
): [ReplayPlayer, ReplayPlayer] {
  const winner = typeof practice?.result.winner === 'string' ? practice.result.winner : null
  return [
    { name: 'Your Agent', score: winner === 'submitted' ? 1 : 0 },
    { name: titleCase(baseline), score: winner === baseline ? 1 : 0 },
  ]
}
