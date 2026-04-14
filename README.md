# OrOgins AI Project

## Project Overview
This project was developed for the University of Bradford module **COS-5031-E – Discipline-specific Artificial Intelligence Project**. The aim of the project is to build a playable AI-based version of the board game **OrOgins** and train an AI agent to play it using **Reinforcement Learning**.

The game logic and AI system were developed in **Python**, while the playable interface was created in **Unity**. A **Flask API** is used to connect the trained AI model to the Unity front end so that a human player can play against the AI in real time.

## Team Members
- **Shafan Shafqat** – Reinforcement Learning, AI integration, Scrum Master
- **Abdullah Butt** – Python game logic and rule implementation
- **Ahmed Saeed** – Unity development and gameplay interface

## Project Aim
The main goal of this project is to:
- create a digital version of the OrOgins board game
- implement the full rules and gameplay system
- train an AI agent to play the game using Reinforcement Learning
- connect the trained AI to a Unity game so users can play against it

## Game Summary
OrOgins is a 2-player strategy board game played on an **8x8 board**.

Each player has:
- 1 Male piece
- 1 Female piece
- 8 Element pieces:
  - 2 Earth
  - 2 Water
  - 2 Fire
  - 2 Air

### Objective
The objective is to move both the **Male** and **Female** pieces to the opponent’s starting row.

### Element System
The game includes an element dominance cycle:
- **Earth beats Water**
- **Water beats Fire**
- **Fire beats Air**
- **Air beats Earth**

Element pieces can affect tiles and capture weaker element pieces depending on the game rules.

## Main Features
- Full OrOgins game logic implemented in Python
- Reinforcement Learning environment for training the AI
- DQN-trained AI model
- Flask API server for communication between Python and Unity
- Unity front end for human vs AI gameplay
- Difficulty modes:
  - Easy
  - Normal
  - Hard
- Move validation
- Game state export for Unity rendering
- Unit testing for rule validation and gameplay logic

## Technologies Used
- **Python**
- **PyTorch**
- **Flask**
- **Unity 6**
- **C#**
- **GitHub**
- **Reinforcement Learning (DQN)**
- **Pytest**

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

Python Files Summary
1.constants.py – stores game constants and settings
2.rules.py – contains legal move logic and rule checks
3.pieces.py – defines the piece class
4.board.py – manages the board state
5.move.py – defines move objects
6.game.py – handles main game flow and game state export
7.environment.py – reinforcement learning environment
8.dqn_agent.py – DQN model, replay buffer, and training functions
9.q_learning.py – Q-learning implementation used as a backup method
10.main.py – menu and execution entry point
11.test_game.py – unit tests for rules and gameplay logic