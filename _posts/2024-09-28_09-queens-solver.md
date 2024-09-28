---
layout: post
title: LinkedIn Queens Solver (Python Project)
tags:
---
I've written a basic brute forcer for the new LinkedIn game _Queens_.

Current version is a straightforward recursive function:
```
define attempt_solve( board ):
	while True:
		next_cell <= get the next unmarked cell
		
		If none are found:
			Check if the game is complete
			If so:
				Return (True,board)
			else:
				Return False # This line is bad
		
		If one is found:
			new_board <= copy the board
			
			Add a queen to next_cell
			Mark all incident cells to the new queen as 'x'
			
			attempt_solve( new_board )

			If this returns (True,solved_board):
				Return (True,solved_board)
			else:
				Mark new_cell on board as 'x'
```
It solved today's Queens in under 7 seconds. This could be reduced quite drastically with some more optimisation.

This was a fun challenge I'd recommend anyone giving a go at.

**Tip**: when getting the 'next unmarked cell', you can choose any unmarked cell. It is much, much more efficient to choose from the colour group with the fewest remaining options.