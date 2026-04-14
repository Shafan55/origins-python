cat > README.md <<'EOF'
# OrOgins AI Project

> AI-powered board game prototype built for **COS-5031-E – Discipline-specific Artificial Intelligence Project**  
> **University of Bradford**

---

## Overview

**OrOgins AI Project** is a digital board game prototype that combines:

- **Python** for game logic and AI
- **PyTorch** for Deep Q-Network (DQN) training
- **Flask** for API communication
- **Unity 6** and **C#** for the front-end gameplay experience

The aim of the project is to build a playable version of **OrOgins** and integrate a trained **Reinforcement Learning AI agent** that can play against a human user in real time.

---

## Team Members

- **Shafan Shafqat** — Reinforcement Learning, AI integration, Scrum Master
- **Abdullah Butt** — Python game logic and rules
- **Ahmed Saeed** — Unity development and gameplay interface

---

## Project Aim

The main goals of this project are:

- create a digital version of the **OrOgins** board game
- implement the full rules and gameplay system
- train an AI agent using **Reinforcement Learning**
- connect the AI to a **Unity** front end
- allow **Human vs AI** gameplay in a working prototype

---

## Game Summary

**OrOgins** is a 2-player strategy board game played on an **8x8 board**.

Each player has:

- **1 Male piece**
- **1 Female piece**
- **8 Element pieces**
  - 2 Earth
  - 2 Water
  - 2 Fire
  - 2 Air

### Objective

The objective is to move both the **Male** and **Female** pieces to the opponent's starting row.

### Element Dominance Cycle

- **Earth beats Water**
- **Water beats Fire**
- **Fire beats Air**
- **Air beats Earth**

Element pieces interact with the board by changing tiles and capturing weaker elements according to the game rules.

---

## Main Features

- Full **OrOgins** rule system implemented in Python
- **Reinforcement Learning environment** for AI training
- **DQN-trained AI model**
- **Flask API** for Unity integration
- **Unity playable prototype**
- **Human vs AI gameplay**
- Difficulty modes:
  - Easy
  - Normal
  - Hard
- Move validation
- Board state export for Unity rendering
- Unit testing for gameplay and rules

---

## Tech Stack

| Technology | Purpose |
|---|---|
| Python | Core game logic and AI |
| PyTorch | DQN model training |
| Flask | API communication |
| Unity 6 | Front-end game engine |
| C# | Unity gameplay scripting |
| Pytest | Unit testing |
| GitHub | Version control |

---

## Project Structure

```text
origins-python/
├── main.py
├── ai_flask_server.py
├── trained_dqn_agent_8x8_best.pth
├── trained_dqn_agent_4x4_best.pth
├── src/
│   ├── constants.py
│   ├── rules.py
│   ├── game.py
│   ├── environment.py
│   ├── dqn_agent.py
│   ├── q_learning.py
│   ├── board.py
│   ├── pieces.py
│   └── move.py
└── tests/
    └── test_game.py

## How to Run

### Install dependencies

```bash
pip install -r requirements.txt
```

### Start the Flask AI server

```bash
python ai_flask_server.py
```

Keep this terminal open while using Unity.

### Open the Unity project

Open the Unity project and press **Play** to start the game.

---

## Run Tests

```bash
python -m pytest -v
```

---

## Optional: Retrain the AI Model

```bash
python main.py
```

Use the Python CLI menu for training, evaluation, and testing.

---

## Trained Models

### `trained_dqn_agent_8x8_best.pth`

* Main model for the full **8x8** board
* Approximate **76% win rate** vs random agent

### `trained_dqn_agent_4x4_best.pth`

* Prototype model for simplified testing
* Approximate **91.5% win rate**

---

## Flask API Endpoints

| Endpoint      | Method | Purpose                                   |
| ------------- | ------ | ----------------------------------------- |
| `/health`     | GET    | Check server status                       |
| `/reset`      | POST   | Reset the game                            |
| `/state`      | GET    | Get current game state                    |
| `/validate`   | POST   | Check whether a move is legal             |
| `/difficulty` | POST   | Change AI difficulty                      |
| `/move`       | POST   | Submit human move and receive AI response |

---

## Difficulty Modes

* **Easy** — random AI
* **Normal** — balanced DQN with some randomness
* **Hard** — strongest DQN mode using greedy decisions

---

## Unity Integration

Unity is responsible for:

* rendering the board and pieces
* handling player input
* sending moves to Flask
* receiving AI moves
* updating the board visually
* showing move logs, status text, and difficulty controls

---

## Current Status

### Completed

* Python game engine
* OrOgins rule implementation
* Reinforcement Learning environment
* DQN training
* trained AI models
* Flask API server
* Unity prototype
* Human vs AI gameplay
* testing and debugging

---

## Future Improvements

* improved UI polish
* custom icons and artwork
* more AI training
* stronger gameplay balancing
* full-game testing
* standalone executable build

---

## Academic Context

**Module:** COS-5031-E – Discipline-specific Artificial Intelligence Project
**University:** University of Bradford

This repository supports the **group AI prototype, presentation, and live demonstration** for the module assessment.

---

## Authors

Developed by the **OrOgins project group** for academic use.

* **Shafan Shafqat**
* **Abdullah Butt**
* **Ahmed Saeed**
