import sys
sys.stdout.reconfigure(line_buffering=True)

print("Starting...", flush=True)

from src.dqn_agent import train_dqn

print("Imports done!", flush=True)

train_dqn(
    episodes=2000,
    board_size=8,
    include_tile_state=False,
    checkpoint_prefix="trained_dqn_agent_8x8",
)