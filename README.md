# Mini Battleship Game with AI

## Overview  
**Mini Battleship** is a Python-based game inspired by the classic Battleship. This version is designed for fast-paced gameplay on a 5x5 grid and features an AI opponent that uses a probability-based attack strategy to challenge players.

---

## Features  
- **Smaller Grid:** 5x5 grid for quick matches.  
- **Simplified Gameplay:** Fewer ships and straightforward rules.  
- **Smart AI:** The AI adjusts its strategy based on hits and misses, using probability to improve its guesses.  
- **Interactive GUI:** Built with Pygame for a user-friendly experience.  

---

## Game Rules  
1. The game is played on a 5x5 grid.  
2. Players have 2-3 ships of varying sizes (e.g., 2-cell and 3-cell ships).  
3. Players take turns guessing coordinates to attack the opponent's ships.  
4. The first player to sink all opponent ships wins.  

---

## AI Strategy  
- **Initial Random Guesses:** The AI starts with random guesses.  
- **Adaptive Attacks:** Focuses on cells adjacent to successful hits.  
- **Probability-Based Decisions:** Calculates the likelihood of a ship being in each cell.  

---

## Installation  
1. Clone the repository:  
   ```bash
   git clone https://github.com/username/repository-name.git
   cd repository-name
