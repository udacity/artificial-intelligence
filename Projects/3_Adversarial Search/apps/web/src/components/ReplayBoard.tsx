import { useEffect, useMemo, useState } from 'react'

import type { ReplayFrame } from '../types'

const WIDTH = 11
const HEIGHT = 9
const PADDED_WIDTH = 13

export interface ReplayPlayer {
  name: string
  score: number
}

type ReplayPlayers = readonly [ReplayPlayer, ReplayPlayer]

function cellIndex(row: number, column: number): number {
  return (HEIGHT - 1 - row) * PADDED_WIDTH + (WIDTH - 1 - column)
}

export function ReplayBoard({ replay, step }: { replay?: ReplayFrame[]; step: number }) {
  const frame = replay?.[step]
  const board = frame ? BigInt(frame.board) : null
  const locations = frame?.player_locations ?? [null, null]
  const previousFrame = step > 0 ? replay?.[step - 1] : undefined
  const cells = useMemo(
    () =>
      Array.from({ length: WIDTH * HEIGHT }, (_, position) => {
        const row = Math.floor(position / WIDTH)
        const column = position % WIDTH
        return { row, column, index: cellIndex(row, column) }
      }),
    [],
  )

  return (
    <div className="board" role="grid" aria-label="11 by 9 Knight Isolation board">
      {cells.map(({ row, column, index }) => {
        const player = locations[0] === index ? 1 : locations[1] === index ? 2 : null
        const isOpen = board === null || (board & (1n << BigInt(index))) !== 0n
        const blocked = !isOpen && player === null
        const last = previousFrame?.chosen_destination === index
        const label = player
          ? `row ${row + 1} column ${column + 1}, player ${player}`
          : `row ${row + 1} column ${column + 1}, ${blocked ? 'blocked' : 'open'}`
        return (
          <div
            className={`cell ${(row + column) % 2 ? 'alt' : ''} ${blocked ? 'blocked' : ''} ${last ? 'last' : ''}`}
            key={index}
            role="gridcell"
            aria-label={label}
          >
            {player ? <span className={`piece p${player}`}>♞</span> : null}
          </div>
        )
      })}
    </div>
  )
}

export function ReplayViewer({
  replay,
  title,
  players,
}: {
  replay?: ReplayFrame[]
  title: string
  players?: ReplayPlayers
}) {
  const lastStep = Math.max(0, (replay?.length ?? 1) - 1)
  const [step, setStep] = useReplayStep(lastStep)
  const frame = replay?.[step]
  return (
    <section className="replay-card" aria-label={`${title} replay`}>
      <div className="match-head">
        <div>
          <strong>{title}</strong>
          <span>{replay?.length ? `${replay.length} replay frames` : 'Replay appears after a completed game'}</span>
        </div>
        <span className="status active">Ply {frame?.ply_index ?? 0}</span>
      </div>
      <ReplayBoard replay={replay} step={step} />
      {players ? <ReplayNameplate players={players} /> : null}
      <div className="replay-controls">
        <button className="ghost" onClick={() => setStep(0)} aria-label="Reset replay">↺</button>
        <button className="ghost" onClick={() => setStep(Math.max(0, step - 1))} aria-label="Previous move">←</button>
        <input
          aria-label="Replay position"
          className="scrubber"
          type="range"
          min="0"
          max={lastStep}
          value={step}
          onChange={(event) => setStep(Number(event.target.value))}
        />
        <button className="ghost" onClick={() => setStep(Math.min(lastStep, step + 1))} aria-label="Next move">→</button>
        <span className="tiny">{step} / {lastStep}</span>
      </div>
      {frame?.outcome ? <p className="tiny">Outcome: {frame.outcome.replace('_', ' ')}</p> : null}
    </section>
  )
}

function ReplayNameplate({ players }: { players: ReplayPlayers }) {
  return (
    <div
      className="replay-nameplate"
      aria-label={`Game score ${players[0].score} to ${players[1].score}`}
    >
      <PlayerIdentity player={players[0]} playerNumber={1} />
      <strong className="replay-game-score">
        {players[0].score}<span>–</span>{players[1].score}
      </strong>
      <PlayerIdentity player={players[1]} playerNumber={2} />
    </div>
  )
}

function PlayerIdentity({
  player,
  playerNumber,
}: {
  player: ReplayPlayer
  playerNumber: 1 | 2
}) {
  return (
    <div className={`replay-player p${playerNumber}`}>
      <span className={`replay-knight p${playerNumber}`} aria-hidden="true">♞</span>
      <span className="replay-player-copy">
        <small>Player {playerNumber}</small>
        <strong>{player.name}</strong>
      </span>
    </div>
  )
}

function useReplayStep(lastStep: number): [number, (value: number) => void] {
  const [step, setStep] = useState(0)
  useEffect(() => setStep(0), [lastStep])
  return [Math.min(step, lastStep), setStep]
}
