---
layout: post
title:
tags:
---
I've written a basic brute forcer for the new LinkedIn game _Queens_.

Current version is extremely straightforward, resembling:
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
				
```