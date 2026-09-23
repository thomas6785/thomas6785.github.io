---
layout: post
title: Solving LinkedIn's 'Queens' (Badly)
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
It solved today's Queens in under 122 milliseconds. This could be be reduced quite a bit with some more optimisation.

This was a fun and quite easy challenge I'd recommend anyone giving a go at. The basic approach outlined above is quite inefficient -- even within the domain of brute forcing there is scope for parallelism and heuristics. Getting more sophisticated, there are certainly algorithms that take a mathematical approach to this -- you can view it as a large system of equation each reflecting one of the game's constraints:

* No two queens may touch diagonally
* No two queens in the same row
* No two queens in the same column
* No two queens on the same colour

**Tip**: when getting the 'next unmarked cell', you can choose any unmarked cell. It is much, much more efficient to choose from the colour group with the fewest remaining options.