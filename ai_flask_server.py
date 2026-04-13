"""
ai_flask_server.py — Origins AI Flask API Server
=================================================
Provides a REST API for Unity to communicate with the trained DQN agent.

Endpoints:
    GET  /health        — Server status and model info
    POST /reset         — Reset the game to initial state
    GET  /state         — Get current full game state
    POST /validate      — Check if a move is legal
    POST /difficulty    — Set AI difficulty (easy / normal / hard)
    POST /move          — Get AI move for current board state

Difficulty modes:
    easy   — RandomAgent (fully random moves)
    normal — DQN with epsilon 0.3 (some randomness)
    hard   — DQN with epsilon 0.0 (fully greedy, best moves)

Usage:
    python ai_flask_server.py
    python ai_flask_server.py --host 0.0.0.0 --port 5000
"""

import argparse
import logging
import random
import sys
import time
import traceback
from datetime import datetime

from flask import Flask, jsonify, request
from flask_cors import CORS

from src.dqn_agent import DQNAgent, build_all_actions, build_action_index_map
from src.environment import OriginsEnv
from src.constants import PLAYER_1, PLAYER_2

# ─────────────────────────────────────────────
# Logging
# ─────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
log = logging.getLogger(__name__)

# ─────────────────────────────────────────────
# Configuration
# ─────────────────────────────────────────────
MODEL_PATH    = "trained_dqn_agent_8x8_best.pth"
BOARD_SIZE    = 8
INCLUDE_TILES = False

DIFFICULTY_SETTINGS = {
    "easy":   {"epsilon": 1.0,  "label": "Easy",   "description": "Random moves"},
    "normal": {"epsilon": 0.3,  "label": "Normal", "description": "Balanced DQN"},
    "hard":   {"epsilon": 0.0,  "label": "Hard",   "description": "Full DQN"},
}

# ─────────────────────────────────────────────
# Flask app
# ─────────────────────────────────────────────
app = Flask(__name__)
CORS(app)

# ─────────────────────────────────────────────
# Global state
# ─────────────────────────────────────────────
agent           = None
all_actions     = None
action_to_index = None
env             = None
server_start    = datetime.utcnow().isoformat() + "Z"
request_count   = 0
move_count      = 0
current_difficulty = "normal"


# ─────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────

def load_model():
    """Load DQN model and build action space."""
    global agent, all_actions, action_to_index, env

    log.info(f"Loading model: {MODEL_PATH}")
    agent           = DQNAgent.load_model(MODEL_PATH)
    agent.epsilon   = DIFFICULTY_SETTINGS["normal"]["epsilon"]
    all_actions     = build_all_actions(BOARD_SIZE)
    action_to_index = build_action_index_map(all_actions)
    env             = OriginsEnv(board_size=BOARD_SIZE, include_tile_state=INCLUDE_TILES)
    env.reset()
    log.info(
        f"Model loaded — State: {agent.state_size} | "
        f"Actions: {agent.action_size} | Board: {BOARD_SIZE}x{BOARD_SIZE}"
    )


def get_ai_action(state, valid_actions):
    """
    Get AI action based on current difficulty.
    Easy   → always random
    Normal → DQN with epsilon 0.3 (30% random)
    Hard   → DQN with epsilon 0.0 (fully greedy)
    """
    if not valid_actions:
        return None

    epsilon = DIFFICULTY_SETTINGS[current_difficulty]["epsilon"]

    # Easy mode — always random
    if current_difficulty == "easy":
        return random.choice(valid_actions)

    # Normal/Hard — use DQN with set epsilon
    old_epsilon   = agent.epsilon
    agent.epsilon = epsilon
    action        = agent.choose_action(state, valid_actions, all_actions, action_to_index)
    agent.epsilon = old_epsilon
    return action


def build_game_state() -> dict:
    """Serialise current game state into Unity-friendly dict."""
    raw = env.game.get_game_state_for_export()

    pieces_flat = []
    for row_idx, row in enumerate(raw["pieces"]):
        for col_idx, piece in enumerate(row):
            if piece is not None:
                pieces_flat.append({
                    "row":     row_idx,
                    "col":     col_idx,
                    "type":    piece["type"],
                    "owner":   piece["owner"],
                    "element": piece["element"],
                    "symbol":  piece["symbol"],
                })

    tiles_flat = []
    for row_idx, row in enumerate(raw["tiles"]):
        for col_idx, tile in enumerate(row):
            tiles_flat.append({
                "row":  row_idx,
                "col":  col_idx,
                "type": tile,
            })

    valid_actions = env.get_valid_actions()

    return {
        "board_size":       raw["board_size"],
        "current_player":   raw["current_player"],
        "game_over":        raw["game_over"],
        "winner":           raw["winner"],
        "steps":            raw["steps"],
        "max_steps":        raw["max_steps"],
        "pieces":           pieces_flat,
        "tiles":            tiles_flat,
        "valid_moves":      [
            {"from_row": a[0], "from_col": a[1], "to_row": a[2], "to_col": a[3]}
            for a in valid_actions
        ],
        "valid_move_count": len(valid_actions),
        "difficulty":       current_difficulty,
    }


def error_response(message: str, status: int = 400):
    log.warning(f"Error {status}: {message}")
    return jsonify({"success": False, "error": message}), status


# ─────────────────────────────────────────────
# Routes
# ─────────────────────────────────────────────

@app.route("/health", methods=["GET"])
def health():
    """GET /health — Server status and model info."""
    global request_count
    request_count += 1

    return jsonify({
        "success":        True,
        "status":         "online",
        "server_time":    datetime.utcnow().isoformat() + "Z",
        "server_started": server_start,
        "model": {
            "path":        MODEL_PATH,
            "board_size":  BOARD_SIZE,
            "state_size":  agent.state_size  if agent else None,
            "action_size": agent.action_size if agent else None,
            "algorithm":   "Deep Q-Network (DQN)",
        },
        "difficulty": {
            "current":     current_difficulty,
            "label":       DIFFICULTY_SETTINGS[current_difficulty]["label"],
            "description": DIFFICULTY_SETTINGS[current_difficulty]["description"],
            "epsilon":     DIFFICULTY_SETTINGS[current_difficulty]["epsilon"],
            "available":   list(DIFFICULTY_SETTINGS.keys()),
        },
        "session": {
            "total_requests": request_count,
            "total_moves":    move_count,
        },
        "game": {
            "current_player": env.game.current_player if env else None,
            "game_over":      env.game.game_over      if env else None,
            "steps":          env.game.steps          if env else None,
        },
    }), 200


@app.route("/difficulty", methods=["POST"])
def set_difficulty():
    """
    POST /difficulty
    Set the AI difficulty level.

    Request body:
    { "difficulty": "easy" | "normal" | "hard" }

    Response:
    {
        "success": true,
        "difficulty": "normal",
        "label": "Normal",
        "description": "Balanced DQN",
        "epsilon": 0.3
    }
    """
    global request_count, current_difficulty
    request_count += 1

    data = request.get_json(silent=True)
    if not data:
        return error_response("Request body must be JSON")

    difficulty = data.get("difficulty", "").lower().strip()

    if difficulty not in DIFFICULTY_SETTINGS:
        return error_response(
            f"Invalid difficulty '{difficulty}'. "
            f"Choose from: {list(DIFFICULTY_SETTINGS.keys())}"
        )

    current_difficulty = difficulty
    settings = DIFFICULTY_SETTINGS[difficulty]

    log.info(f"Difficulty set to: {difficulty} (epsilon={settings['epsilon']})")

    return jsonify({
        "success":     True,
        "difficulty":  difficulty,
        "label":       settings["label"],
        "description": settings["description"],
        "epsilon":     settings["epsilon"],
        "message":     f"AI difficulty set to {settings['label']}",
    }), 200


@app.route("/reset", methods=["POST"])
def reset():
    """POST /reset — Reset game to initial state."""
    global request_count, move_count, env
    request_count += 1

    data       = request.get_json(silent=True) or {}
    board_size = int(data.get("board_size", BOARD_SIZE))

    if board_size not in (4, 8):
        return error_response("board_size must be 4 or 8")

    try:
        env        = OriginsEnv(board_size=board_size, include_tile_state=INCLUDE_TILES)
        env.reset()
        move_count = 0
        log.info(f"Game reset — {board_size}x{board_size} — difficulty: {current_difficulty}")

        return jsonify({
            "success":    True,
            "message":    f"Game reset — {board_size}x{board_size}",
            "difficulty": current_difficulty,
            "game_state": build_game_state(),
        }), 200

    except Exception as exc:
        log.error(traceback.format_exc())
        return error_response(f"Reset failed: {str(exc)}", 500)


@app.route("/state", methods=["GET"])
def state():
    """GET /state — Current full game state."""
    global request_count
    request_count += 1

    if env is None:
        return error_response("Server not initialised — call /reset first", 503)

    try:
        return jsonify({
            "success":    True,
            "game_state": build_game_state(),
        }), 200

    except Exception as exc:
        log.error(traceback.format_exc())
        return error_response(f"State retrieval failed: {str(exc)}", 500)


@app.route("/validate", methods=["POST"])
def validate():
    """
    POST /validate
    Check if a move is legal in the current game state.

    Request: { "from_row": 0, "from_col": 0, "to_row": 2, "to_col": 0 }
    Response: { "success": true, "legal": true|false, "reason": "..." }
    """
    global request_count
    request_count += 1

    if env is None:
        return error_response("Server not initialised — call /reset first", 503)

    data = request.get_json(silent=True)
    if not data:
        return error_response("Request body must be JSON")

    for field in ("from_row", "from_col", "to_row", "to_col"):
        if field not in data:
            return error_response(f"Missing field: {field}")

    try:
        from_row = int(data["from_row"])
        from_col = int(data["from_col"])
        to_row   = int(data["to_row"])
        to_col   = int(data["to_col"])
    except (ValueError, TypeError):
        return error_response("Move coordinates must be integers")

    size = env.game.board.size
    for name, val in [("from_row", from_row), ("from_col", from_col),
                      ("to_row", to_row), ("to_col", to_col)]:
        if not (0 <= val < size):
            return error_response(f"{name}={val} out of bounds for {size}x{size} board")

    action        = (from_row, from_col, to_row, to_col)
    valid_actions = env.get_valid_actions()
    is_legal      = action in valid_actions

    reason = None
    if not is_legal:
        piece = env.game.board.get_piece(from_row, from_col)
        if piece is None:
            reason = "No piece at source square"
        elif piece.owner != env.game.current_player:
            reason = f"Piece belongs to {piece.owner}, current turn is {env.game.current_player}"
        elif env.game.game_over:
            reason = "Game is already over"
        else:
            reason = "Move violates game rules"

    log.info(f"Validate ({from_row},{from_col})->({to_row},{to_col}): {'LEGAL' if is_legal else f'ILLEGAL — {reason}'}")

    return jsonify({
        "success":        True,
        "legal":          is_legal,
        "reason":         reason,
        "current_player": env.game.current_player,
        "move": {
            "from_row": from_row, "from_col": from_col,
            "to_row":   to_row,   "to_col":   to_col,
        },
    }), 200


@app.route("/move", methods=["POST"])
def move():
    """
    POST /move
    Apply human move (optional) then get AI response.

    Request body:
    {
        "human_move": {          ← optional
            "from_row": int,
            "from_col": int,
            "to_row":   int,
            "to_col":   int
        }
    }

    Response:
    {
        "success":    true,
        "move":       { "from_row", "from_col", "to_row", "to_col" },
        "game_state": { ... },
        "game_over":  bool,
        "winner":     str | null,
        "think_ms":   float,
        "difficulty": str
    }
    """
    global request_count, move_count
    request_count += 1

    if env is None or agent is None:
        return error_response("Server not initialised — call /reset first", 503)

    if env.game.game_over:
        return jsonify({
            "success":    False,
            "error":      "Game is already over",
            "game_over":  True,
            "winner":     env.game.winner,
            "difficulty": current_difficulty,
            "game_state": build_game_state(),
        }), 200

    data = request.get_json(silent=True) or {}

    # ── Apply human move if provided ─────────────────────────────────
    human_move_data = data.get("human_move")
    if human_move_data:
        required = ("from_row", "from_col", "to_row", "to_col")
        if not all(f in human_move_data for f in required):
            return error_response("human_move requires: from_row, from_col, to_row, to_col")

        try:
            h_action = (
                int(human_move_data["from_row"]),
                int(human_move_data["from_col"]),
                int(human_move_data["to_row"]),
                int(human_move_data["to_col"]),
            )
        except (ValueError, TypeError):
            return error_response("human_move coordinates must be integers")

        valid_actions = env.get_valid_actions()
        if h_action not in valid_actions:
            return error_response(f"Human move {h_action} is not legal in current state")

        _, _, human_done, _ = env.step(h_action)
        move_count += 1

        if human_done:
            return jsonify({
                "success":    True,
                "move":       None,
                "game_over":  True,
                "winner":     env.game.winner,
                "message":    "Human move ended the game",
                "difficulty": current_difficulty,
                "game_state": build_game_state(),
                "think_ms":   0.0,
            }), 200

    # ── AI move ──────────────────────────────────────────────────────
    valid_actions = env.get_valid_actions()

    if not valid_actions:
        return jsonify({
            "success":    True,
            "move":       None,
            "game_over":  True,
            "winner":     env.game.winner,
            "message":    "No legal moves — game over",
            "difficulty": current_difficulty,
            "game_state": build_game_state(),
            "think_ms":   0.0,
        }), 200

    state_obs = env.get_state()

    t_start  = time.perf_counter()
    action   = get_ai_action(state_obs, valid_actions)
    think_ms = round((time.perf_counter() - t_start) * 1000, 2)

    if action is None:
        return error_response("AI could not select a move", 500)

    from_row, from_col, to_row, to_col = action
    _, reward, done, info = env.step(action)
    move_count += 1

    diff_label = DIFFICULTY_SETTINGS[current_difficulty]["label"]
    log.info(
        f"[{diff_label}] AI: ({from_row},{from_col})->({to_row},{to_col}) | "
        f"Reward: {reward:.2f} | Done: {done} | {think_ms}ms"
    )

    response = {
        "success":    True,
        "move": {
            "from_row": from_row,
            "from_col": from_col,
            "to_row":   to_row,
            "to_col":   to_col,
        },
        "reward":     round(float(reward), 4),
        "game_over":  done,
        "winner":     env.game.winner,
        "think_ms":   think_ms,
        "difficulty": current_difficulty,
        "game_state": build_game_state(),
    }

    if done:
        if env.game.winner == PLAYER_1:
            response["result_message"] = "Player 1 wins!"
        elif env.game.winner == PLAYER_2:
            response["result_message"] = f"AI wins! ({diff_label} mode)"
        else:
            response["result_message"] = "Draw!"

    return jsonify(response), 200


# ─────────────────────────────────────────────
# Error handlers
# ─────────────────────────────────────────────

@app.errorhandler(404)
def not_found(e):
    return jsonify({"success": False, "error": "Endpoint not found"}), 404

@app.errorhandler(405)
def method_not_allowed(e):
    return jsonify({"success": False, "error": "Method not allowed"}), 405

@app.errorhandler(500)
def internal_error(e):
    return jsonify({"success": False, "error": "Internal server error"}), 500


# ─────────────────────────────────────────────
# Startup
# ─────────────────────────────────────────────

def print_banner(host: str, port: int):
    print()
    print("=" * 60)
    print("  Origins AI Server")
    print("=" * 60)
    print(f"  Model      : {MODEL_PATH}")
    print(f"  Board      : {BOARD_SIZE}x{BOARD_SIZE}")
    print(f"  Difficulty : Normal (default)")
    print(f"  Host       : http://{host}:{port}")
    print()
    print("  Endpoints:")
    print(f"    GET  /health")
    print(f"    POST /difficulty  — easy | normal | hard")
    print(f"    POST /reset")
    print(f"    GET  /state")
    print(f"    POST /validate")
    print(f"    POST /move")
    print("=" * 60)
    print()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Origins AI Flask Server")
    parser.add_argument("--host",  type=str,       default="127.0.0.1")
    parser.add_argument("--port",  type=int,       default=5000)
    parser.add_argument("--debug", action="store_true")
    args = parser.parse_args()

    load_model()
    print_banner(args.host, args.port)
    app.run(host=args.host, port=args.port, debug=args.debug)