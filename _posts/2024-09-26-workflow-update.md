---
layout: post
title: Website Configuration and Workflow
tags:
---
I originally had this website configured by-hand in HTML, but I've just installed Jekyll.

My workflow is a little unusual but working great:
- An top-level Git repo houses all of my notes for college and personal projects
	- I primarily edit this via Obsidian (Markdown files)
	- but also use VScode for LaTeX and HTML files
- Some folders within this vault are git submodules - one of these is this website
- Obsidian has built-in functionality for creating notes from templates, so now I can easily create new blog posts in Obsidian and they'll get pushed straight to the GitHub repo when I commit
- Obsidian plugin 'Webpage HTML Export' is configured to render my college notes into HTML pages and put them into one of the public repositories for classmates to view

Also, I've configured an Atom feed at [thomas6785.github.io/feed.xml](thomas6785.github.io/feed.xml "Why are you reading the tooltip?"), but it's not behaving entirely correctly.