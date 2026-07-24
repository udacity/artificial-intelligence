import { fireEvent, render, screen } from '@testing-library/react'
import { expect, test } from 'vitest'

import { ReplayViewer } from './ReplayBoard'

const blankBoard = '41523161203939122082683632224299007'

test('replay stepping and scrubbing select canonical frames', () => {
  render(
    <ReplayViewer
      title="Test fixture"
      players={[
        { name: 'Teal Knight', score: 1 },
        { name: 'Blue Knight', score: 0 },
      ]}
      replay={[
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
          chosen_action: 0,
          chosen_destination: 0,
          legal_actions: [0],
          elapsed_ms: 1,
          stdout_excerpt: '',
          stderr_excerpt: '',
          outcome: null,
        },
        {
          ply_index: 2,
          active_player: 0,
          board: blankBoard,
          player_locations: [57, 0],
          chosen_action: null,
          chosen_destination: null,
          legal_actions: [],
          elapsed_ms: 0,
          stdout_excerpt: '',
          stderr_excerpt: '',
          outcome: 'game_over',
        },
      ]}
    />,
  )
  fireEvent.click(screen.getByRole('button', { name: 'Next move' }))
  expect(screen.getByRole('slider', { name: 'Replay position' })).toHaveValue('1')
  fireEvent.change(screen.getByRole('slider', { name: 'Replay position' }), {
    target: { value: '2' },
  })
  expect(screen.getByRole('slider', { name: 'Replay position' })).toHaveValue('2')
  expect(screen.getByLabelText(/player 2/)).toBeInTheDocument()
  expect(screen.getByText('Teal Knight').closest('.replay-player')).toHaveClass('p1')
  expect(screen.getByText('Blue Knight').closest('.replay-player')).toHaveClass('p2')
  expect(screen.getByLabelText('Game score 1 to 0')).toBeInTheDocument()
})
