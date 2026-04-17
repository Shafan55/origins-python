import random
from collections import deque

import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim

from src.environment import OriginsEnv
from src.constants import PLAYER_1, PLAYER_2


class DQNNetwork(nn.Module):
    def __init__(self, state_size: int, action_size: int):
        super().__init__()
        self.model = nn.Sequential(
            nn.Linear(state_size, 256),
            nn.ReLU(),
            nn.Linear(256, 256),
            nn.ReLU(),
            nn.Linear(256, 128),
            nn.ReLU(),
            nn.Linear(128, action_size),
        )

    def forward(self, x):
        return self.model(x)


class ReplayBuffer:
    def __init__(self, capacity: int = 100000):
        self.buffer = deque(maxlen=capacity)

    def add(self, state, action_index, reward, next_state, done):
        self.buffer.append((state, action_index, reward, next_state, done))

    def sample(self, batch_size: int):
        batch = random.sample(self.buffer, batch_size)
        states, action_indices, rewards, next_states, dones = zip(*batch)
        return (
            np.array(states,         dtype=np.float32),
            np.array(action_indices, dtype=np.int64),
            np.array(rewards,        dtype=np.float32),
            np.array(next_states,    dtype=np.float32),
            np.array(dones,          dtype=np.float32),
        )

    def __len__(self):
        return len(self.buffer)


def build_all_actions(board_size: int):
    actions = []
    for from_row in range(board_size):
        for from_col in range(board_size):
            for to_row in range(board_size):
                for to_col in range(board_size):
                    if (from_row, from_col) != (to_row, to_col):
                        actions.append((from_row, from_col, to_row, to_col))
    return actions


def build_action_index_map(all_actions):
    return {action: index for index, action in enumerate(all_actions)}


class DQNAgent:
    def __init__(
        self,
        state_size: int,
        action_size: int,
        lr: float = 0.0003,
        gamma: float = 0.98,
        epsilon: float = 1.0,
        epsilon_decay: float = 0.9985,
        epsilon_min: float = 0.05,
        batch_size: int = 64,
        target_update_freq: int = 200,
        replay_capacity: int = 100000,
    ):
        self.state_size = state_size
        self.action_size = action_size
        self.gamma = gamma
        self.epsilon = epsilon
        self.epsilon_decay = epsilon_decay
        self.epsilon_min = epsilon_min
        self.batch_size = batch_size
        self.target_update_freq = target_update_freq

        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        print(f"DQNAgent using device: {self.device}")

        self.policy_net = DQNNetwork(state_size, action_size).to(self.device)
        self.target_net = DQNNetwork(state_size, action_size).to(self.device)
        self.target_net.load_state_dict(self.policy_net.state_dict())
        self.target_net.eval()

        self.optimizer = optim.Adam(self.policy_net.parameters(), lr=lr)
        self.scheduler = optim.lr_scheduler.StepLR(
            self.optimizer, step_size=1000, gamma=0.5
        )
        self.loss_fn = nn.SmoothL1Loss()

        self.memory = ReplayBuffer(capacity=replay_capacity)
        self.train_steps = 0

    def choose_action(self, state, valid_actions, all_actions, action_to_index):
        if not valid_actions:
            return None

        if random.random() < self.epsilon:
            return random.choice(valid_actions)

        state_array = np.array(state, dtype=np.float32)
        state_tensor = torch.tensor(
            state_array, dtype=torch.float32, device=self.device
        ).unsqueeze(0)

        with torch.no_grad():
            q_values = self.policy_net(state_tensor).cpu().numpy()[0]

        valid_indices = [action_to_index[action] for action in valid_actions]
        best_index = max(valid_indices, key=lambda idx: q_values[idx])
        return all_actions[best_index]

    def store_experience(
        self, state, action, reward, next_state, done, action_to_index
    ):
        action_index = action_to_index[action]
        self.memory.add(
            np.array(state,      dtype=np.float32),
            action_index,
            reward,
            np.array(next_state, dtype=np.float32),
            done,
        )

    def train_step(self):
        if len(self.memory) < self.batch_size:
            return None

        states, action_indices, rewards, next_states, dones = self.memory.sample(
            self.batch_size
        )

        states        = torch.tensor(states,        dtype=torch.float32, device=self.device)
        action_indices= torch.tensor(action_indices,dtype=torch.int64,   device=self.device).unsqueeze(1)
        rewards       = torch.tensor(rewards,       dtype=torch.float32, device=self.device)
        next_states   = torch.tensor(next_states,   dtype=torch.float32, device=self.device)
        dones         = torch.tensor(dones,         dtype=torch.float32, device=self.device)

        current_q_values = self.policy_net(states).gather(1, action_indices).squeeze(1)

        with torch.no_grad():
            next_policy_actions = self.policy_net(next_states).argmax(dim=1, keepdim=True)
            next_target_q_values = self.target_net(next_states).gather(
                1, next_policy_actions
            ).squeeze(1)
            target_q_values = rewards + (1 - dones) * self.gamma * next_target_q_values
            target_q_values = torch.clamp(target_q_values, -60.0, 60.0)

        loss = self.loss_fn(current_q_values, target_q_values)

        self.optimizer.zero_grad()
        loss.backward()
        torch.nn.utils.clip_grad_norm_(self.policy_net.parameters(), 1.0)
        self.optimizer.step()

        self.train_steps += 1
        if self.train_steps % self.target_update_freq == 0:
            self.target_net.load_state_dict(self.policy_net.state_dict())
            self.scheduler.step()

        return loss.item()

    def decay_epsilon(self):
        self.epsilon = max(self.epsilon_min, self.epsilon * self.epsilon_decay)

    def save_model(self, filepath: str):
        payload = {
            "state_size":          self.state_size,
            "action_size":         self.action_size,
            "gamma":               self.gamma,
            "epsilon":             self.epsilon,
            "epsilon_decay":       self.epsilon_decay,
            "epsilon_min":         self.epsilon_min,
            "batch_size":          self.batch_size,
            "target_update_freq":  self.target_update_freq,
            "policy_state_dict":   self.policy_net.state_dict(),
            "target_state_dict":   self.target_net.state_dict(),
            "optimizer_state_dict":self.optimizer.state_dict(),
        }
        torch.save(payload, filepath)
        print(f"Model saved to: {filepath}")

    @classmethod
    def load_model(cls, filepath: str):
        payload = torch.load(filepath, map_location="cpu")
        agent = cls(
            state_size=        payload["state_size"],
            action_size=       payload["action_size"],
            gamma=             payload.get("gamma",            0.97),
            epsilon=           payload.get("epsilon",          0.0),
            epsilon_decay=     payload.get("epsilon_decay",    0.9995),
            epsilon_min=       payload.get("epsilon_min",      0.05),
            batch_size=        payload.get("batch_size",       64),
            target_update_freq=payload.get("target_update_freq", 200),
        )
        agent.policy_net.load_state_dict(payload["policy_state_dict"])
        if "target_state_dict" in payload:
            agent.target_net.load_state_dict(payload["target_state_dict"])
        else:
            agent.target_net.load_state_dict(payload["policy_state_dict"])
        if "optimizer_state_dict" in payload:
            agent.optimizer.load_state_dict(payload["optimizer_state_dict"])
        return agent


class RandomAgent:
    def choose_action(
        self, state, valid_actions, all_actions=None, action_to_index=None
    ):
        if not valid_actions:
            return None
        return random.choice(valid_actions)


def clone_as_frozen_agent(agent: DQNAgent) -> DQNAgent:
    frozen = DQNAgent(
        state_size=        agent.state_size,
        action_size=       agent.action_size,
        lr=                0.0001,
        gamma=             agent.gamma,
        epsilon=           0.0,
        epsilon_decay=     1.0,
        epsilon_min=       0.0,
        batch_size=        agent.batch_size,
        target_update_freq=agent.target_update_freq,
        replay_capacity=   1,
    )
    frozen.policy_net.load_state_dict(agent.policy_net.state_dict())
    frozen.target_net.load_state_dict(agent.target_net.state_dict())
    frozen.policy_net.eval()
    frozen.target_net.eval()
    return frozen


def choose_opponent_mode():
    roll = random.random()
    if roll < 0.50:
        return "random"
    if roll < 0.80:
        return "frozen"
    return "self"


_side_counter = 0

def choose_agent_side():
    global _side_counter
    _side_counter += 1
    return PLAYER_1 if _side_counter % 2 == 0 else PLAYER_2


def play_episode_dqn(
    agent_p1,
    agent_p2,
    all_actions,
    action_to_index,
    board_size: int = 8,
    include_tile_state: bool = False,
    render: bool = False,
):
    env = OriginsEnv(board_size=board_size, include_tile_state=include_tile_state)
    state = env.reset()
    done = False
    step_count = 0
    info = {"winner": None}

    while not done:
        valid_actions = env.get_valid_actions()
        if not valid_actions:
            break

        current_player = env.game.current_player

        if current_player == PLAYER_1:
            action = agent_p1.choose_action(
                state, valid_actions, all_actions, action_to_index
            )
        else:
            action = agent_p2.choose_action(
                state, valid_actions, all_actions, action_to_index
            )

        if action is None:
            break

        next_state, _, done, info = env.step(action)
        state = next_state
        step_count += 1

        if render:
            env.render()

    return {
        "winner": info.get("winner"),
        "done": done,
        "steps": step_count,
    }


def evaluate_quick_fair(
    agent,
    all_actions,
    action_to_index,
    board_size: int = 8,
    include_tile_state: bool = True,
    episodes_each_side: int = 20,
):
    random_agent = RandomAgent()
    old_epsilon = agent.epsilon
    agent.epsilon = 0.0

    wins = draws = losses = 0

    for _ in range(episodes_each_side):
        result = play_episode_dqn(
            agent, random_agent, all_actions, action_to_index,
            board_size=board_size, include_tile_state=include_tile_state,
        )
        if not result["done"]:
            draws += 1
        elif result["winner"] == PLAYER_1:
            wins += 1
        elif result["winner"] == PLAYER_2:
            losses += 1
        else:
            draws += 1

    for _ in range(episodes_each_side):
        result = play_episode_dqn(
            random_agent, agent, all_actions, action_to_index,
            board_size=board_size, include_tile_state=include_tile_state,
        )
        if not result["done"]:
            draws += 1
        elif result["winner"] == PLAYER_2:
            wins += 1
        elif result["winner"] == PLAYER_1:
            losses += 1
        else:
            draws += 1

    total = episodes_each_side * 2
    agent.epsilon = old_epsilon

    return {
        "wins":      wins,
        "draws":     draws,
        "losses":    losses,
        "win_rate":  wins  / total,
        "draw_rate": draws / total,
        "loss_rate": losses/ total,
    }


def train_dqn(
    episodes: int = 300,
    board_size: int = 8,
    include_tile_state: bool = False,
    checkpoint_prefix: str | None = None,
):
    print("train_dqn called!", flush=True)  
    env = OriginsEnv(board_size=board_size, include_tile_state=include_tile_state)
    print("env created!", flush=True)  
    initial_state = env.reset()
    print("env reset!", flush=True)  

    env = OriginsEnv(board_size=board_size, include_tile_state=include_tile_state)
    initial_state = env.reset()

    state_size    = len(initial_state)
    all_actions   = build_all_actions(board_size)
    action_to_index = build_action_index_map(all_actions)
    action_size   = len(all_actions)

    
    replay_capacity   = 10000  if board_size == 4 else 50000
    batch_size        = 32     if board_size == 4 else 64
    target_update_freq= 50    if board_size == 4 else 100

    agent = DQNAgent(
        state_size=state_size,
        action_size=action_size,
        replay_capacity=replay_capacity,
        batch_size=batch_size,
        target_update_freq=target_update_freq,
    )

    frozen_agent = clone_as_frozen_agent(agent)
    random_agent = RandomAgent()

    episode_rewards = []
    episode_steps   = []
    episode_p1_wins = []
    episode_p2_wins = []
    episode_draws   = []
    episode_losses  = []

    best_eval_score = float("-inf")

    print("Starting DQN training...")
    print(f"Board size:        {board_size}x{board_size}")
    print(f"State size:        {state_size}")
    print(f"Action size:       {action_size}")
    print(f"Tile-aware state:  {include_tile_state}")
    print(f"Replay capacity:   {replay_capacity}")
    print(f"Batch size:        {batch_size}")

    for episode in range(episodes):

        
        if episode > 0 and episode % 500 == 0:
            frozen_agent = clone_as_frozen_agent(agent)
            print(f"  [Episode {episode}] Frozen opponent updated.")

        state  = env.reset()
        done   = False
        total_reward    = 0.0
        step_count      = 0
        info            = {"winner": None}
        losses_this_ep  = []

        opponent_mode = choose_opponent_mode()
        agent_side    = choose_agent_side()

        while not done:
            valid_actions = env.get_valid_actions()
            if not valid_actions:
                break

            current_player = env.game.current_player

            if current_player == agent_side:
                action = agent.choose_action(
                    state, valid_actions, all_actions, action_to_index
                )
                if action is None:
                    break

                next_state, reward, done, info = env.step(action)

                agent.store_experience(
                    state, action, reward, next_state, done, action_to_index
                )

                loss = agent.train_step()
                if loss is not None:
                    losses_this_ep.append(loss)

                state = next_state
                total_reward += reward
                step_count   += 1

            else:
                if opponent_mode == "random":
                    action = random_agent.choose_action(state, valid_actions)
                elif opponent_mode == "frozen":
                    action = frozen_agent.choose_action(
                        state, valid_actions, all_actions, action_to_index
                    )
                else:
                    old_eps = agent.epsilon
                    agent.epsilon = 0.0
                    action = agent.choose_action(
                        state, valid_actions, all_actions, action_to_index
                    )
                    agent.epsilon = old_eps

                if action is None:
                    break

                next_state, _, done, info = env.step(action)
                state = next_state
                step_count += 1

        winner = info.get("winner")
        p1_win = 1 if winner == PLAYER_1 else 0
        p2_win = 1 if winner == PLAYER_2 else 0
        draw   = 1 if done and winner is None else 0
        avg_loss = (
            sum(losses_this_ep) / len(losses_this_ep)
            if losses_this_ep else 0.0
        )

        agent.decay_epsilon()

        episode_rewards.append(total_reward)
        episode_steps.append(step_count)
        episode_p1_wins.append(p1_win)
        episode_p2_wins.append(p2_win)
        episode_draws.append(draw)
        episode_losses.append(avg_loss)

        if (episode + 1) % 10 == 0:
            recent_rewards = episode_rewards[-100:]
            recent_steps   = episode_steps[-100:]
            recent_p1      = sum(episode_p1_wins[-100:])
            recent_p2      = sum(episode_p2_wins[-100:])
            recent_draws   = sum(episode_draws[-100:])
            recent_losses  = [l for l in episode_losses[-100:] if l > 0]

            avg_reward = sum(recent_rewards) / len(recent_rewards)
            avg_steps  = sum(recent_steps)   / len(recent_steps)
            avg_loss_v = sum(recent_losses)  / len(recent_losses) if recent_losses else 0.0

            win_rate  = ((recent_p1 + recent_p2) / 100) * 100
            draw_rate = (recent_draws / 100) * 100

            print(
                f"Episode {episode + 1}/{episodes} | "
                f"Avg Reward: {avg_reward:.2f} | "
                f"Avg Steps: {avg_steps:.2f} | "
                f"P1: {recent_p1}/100 | "
                f"P2: {recent_p2}/100 | "
                f"Draws: {recent_draws}/100 | "
                f"Win%: {win_rate:.1f} | "
                f"Draw%: {draw_rate:.1f} | "
                f"Loss: {avg_loss_v:.4f} | "
                f"Eps: {agent.epsilon:.3f}"
            )

        
        if checkpoint_prefix and (episode + 1) % 500 == 0:
            quick_eval = evaluate_quick_fair(
                agent, all_actions, action_to_index,
                board_size=board_size,
                include_tile_state=include_tile_state,
                episodes_each_side=20,
            )

            eval_score = quick_eval["win_rate"] - (0.5 * quick_eval["draw_rate"])

            print(
                f"\nCheckpoint Eval @ Episode {episode + 1} | "
                f"Wins: {quick_eval['wins']} | "
                f"Draws: {quick_eval['draws']} | "
                f"Losses: {quick_eval['losses']} | "
                f"Win Rate: {quick_eval['win_rate'] * 100:.1f}% | "
                f"Eval Score: {eval_score:.4f}"
            )

            if eval_score > best_eval_score:
                best_eval_score = eval_score
                best_path = f"{checkpoint_prefix}_best.pth"
                agent.save_model(best_path)
                print(f"New best model saved: {best_path}")


    print("\nDQN TRAINING SUMMARY")
    print("=" * 50)
    print(f"Total episodes:         {episodes}")
    print(f"Overall avg reward:     {sum(episode_rewards)/len(episode_rewards):.2f}")
    print(f"Overall avg steps:      {sum(episode_steps)/len(episode_steps):.2f}")
    print(f"Player 1 wins:          {sum(episode_p1_wins)}/{episodes}")
    print(f"Player 2 wins:          {sum(episode_p2_wins)}/{episodes}")
    print(f"Draws:                  {sum(episode_draws)}/{episodes}")
    print(f"Final epsilon:          {agent.epsilon:.3f}")

    return (
        agent,
        episode_rewards,
        episode_steps,
        episode_p1_wins,
        episode_p2_wins,
        episode_draws,
        all_actions,
        action_to_index,
    )


def train_dqn_8x8(episodes: int = 8000):
    return train_dqn(
        episodes=episodes,
        board_size=8,
        include_tile_state=False,
        checkpoint_prefix="trained_dqn_agent_8x8",
    )


def evaluate_dqn_self_play(
    agent,
    all_actions,
    action_to_index,
    episodes: int = 100,
    board_size: int = 8,
    include_tile_state: bool = True,
    render: bool = False,
):
    print("\nDQN SELF-PLAY EVALUATION")
    print("=" * 40)

    old_epsilon = agent.epsilon
    agent.epsilon = 0.0

    metrics = {
        "p1_wins": 0, "p2_wins": 0,
        "draws": 0, "unfinished": 0,
        "total_steps": 0,
    }

    for _ in range(episodes):
        result = play_episode_dqn(
            agent, agent, all_actions, action_to_index,
            board_size=board_size,
            include_tile_state=include_tile_state,
            render=render,
        )
        if not result["done"]:
            metrics["unfinished"] += 1
        elif result["winner"] == PLAYER_1:
            metrics["p1_wins"] += 1
        elif result["winner"] == PLAYER_2:
            metrics["p2_wins"] += 1
        else:
            metrics["draws"] += 1
        metrics["total_steps"] += result["steps"]

    avg_steps = metrics["total_steps"] / episodes
    print(f"Episodes:      {episodes}")
    print(f"P1 wins:       {metrics['p1_wins']}")
    print(f"P2 wins:       {metrics['p2_wins']}")
    print(f"Draws:         {metrics['draws']}")
    print(f"Unfinished:    {metrics['unfinished']}")
    print(f"Avg steps:     {avg_steps:.2f}")

    agent.epsilon = old_epsilon
    return metrics


def evaluate_dqn_agent_fair(
    agent,
    all_actions,
    action_to_index,
    episodes_each_side: int = 100,
    board_size: int = 8,
    include_tile_state: bool = True,
):
    print("\nDQN FAIR COMBINED EVALUATION")
    print("=" * 40)

    random_agent = RandomAgent()
    old_epsilon  = agent.epsilon
    agent.epsilon = 0.0

    def run_side(agent_p1, agent_p2, winning_player):
        m = {"wins": 0, "draws": 0, "losses": 0, "unfinished": 0, "total_steps": 0}
        for _ in range(episodes_each_side):
            result = play_episode_dqn(
                agent_p1, agent_p2, all_actions, action_to_index,
                board_size=board_size, include_tile_state=include_tile_state,
            )
            if not result["done"]:
                m["unfinished"] += 1
            elif result["winner"] == winning_player:
                m["wins"] += 1
            elif result["winner"] is None:
                m["draws"] += 1
            else:
                m["losses"] += 1
            m["total_steps"] += result["steps"]
        return m

    p1_m = run_side(agent, random_agent, PLAYER_1)
    p2_m = run_side(random_agent, agent, PLAYER_2)

    total     = episodes_each_side * 2
    wins      = p1_m["wins"]      + p2_m["wins"]
    draws     = p1_m["draws"]     + p2_m["draws"]
    losses    = p1_m["losses"]    + p2_m["losses"]
    unfinished= p1_m["unfinished"]+ p2_m["unfinished"]
    avg_steps = (p1_m["total_steps"] + p2_m["total_steps"]) / total

    print(f"Total episodes: {total}")
    print(f"Wins:           {wins}  ({wins/total*100:.1f}%)")
    print(f"Draws:          {draws} ({draws/total*100:.1f}%)")
    print(f"Losses:         {losses}({losses/total*100:.1f}%)")
    print(f"Unfinished:     {unfinished} ({unfinished/total*100:.1f}%)")
    print(f"Avg steps:      {avg_steps:.2f}")

    agent.epsilon = old_epsilon

    return {
        "wins": wins, "draws": draws, "losses": losses,
        "unfinished": unfinished, "episodes": total,
        "win_rate":  wins/total*100,
        "draw_rate": draws/total*100,
        "loss_rate": losses/total*100,
        "average_steps": avg_steps,
    }