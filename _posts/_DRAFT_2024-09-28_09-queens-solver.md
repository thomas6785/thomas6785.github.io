---
layout: post
title:
tags:
---
I've written a basic brute forcer for the new LinkedIn game _Queens_.

Current version is an extremely straightforward recursive function:
```
define attempt_solve( board ):
	while True:
		Get the next unmarked cell as next_cell
		If none are found:
			Check if the game is complete
			If so:
				Return (True,board)
			else:
				Return False # This line is bad
		If one is found:
			Copy the board into new_board
			Add a queen to next_cell
			Mark all incident cells to the new queen as 'x'
			attempt_solve( new_board )
			If this returns (True,solved_board):
				Return (True,solved_board)
			else:
				Mark new_cell on board as 'x'
```
The logic for adding queens and marking off incident cells is quite clumsy and needs some tidying, but it solved today's Queens in under two minutes. With some optimisations, this time should reduce drastically.

Future developments:
- Optimise logic for adding queens and marking off incident cells
- 
- Integrate web automation to automatically detect the colours (currently entered manually) and enter the solution in
- 