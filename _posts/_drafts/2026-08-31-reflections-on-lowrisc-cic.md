---
title: Reflections on lowRISC C.I.C.
layout: post
---
Today marks the end of my 3-month placement at lowRISC C.I.C..

I was reporting to Marno van der Maas while here, and mentored by Ray Lau. The vast majority of my work was on designing, verifying, and integrating an Ethernet interface for FPGA implementation.

One wonderful thing about working in open-source is that I can share as much detail as I want about the project, including [a link to the source code](https://github.com/lowRISC/ethernet/tree/2dc3a8b12da4006f343d6be82872dd80990cab6f).

I went into this design project with two (related) goals in mind:

**Do not be a over-work**

As something of a workaholic I've often started started work before 8am and worked long days, continuing to think about my work over evenings and weekends. I do enjoy my work a great deal, and in previous jobs I indulged this addiction as it was also very valuable to my career.

However, that was when I was doing internships and placements, and another break or holiday or year of college was always around the corner. My lifestyle was constantly shifting every few months, so I could afford to "go all in" on my latest sprint.

Being now a college graduate, the sprint will become a marathon. The lifestyle I define now will continue for months or (potentially) years, so I decided I should take this opportunity to establish a routine that I felt was more sustainable. I made an effort not to arrive to work early -- if I woke up early, I would spend the extra time in a coffee shop, working on my own projects or texting with friends -- and not to leave after 6pm -- though admittedly that rule was broken on a few occasions.

Still, I'm very happy with the changes I've made in this respect.

**Do not over-commit**

Nothing is more exciting than starting a brand new project, and I have a long history of proposing new ideas, running off to work on them, leaving previous projects half-finished. This time round I made a considerable effort not to do this -- barring a small number of side projects, I stuck to one "big project".

A critical moment came around week 5/6 of my placement when the design of my Ethernet RTL was beginning to feel mature. I had a basic testbench and pretty good documentation too. I spoke to my manager who offered to identify a new project for me to work on. I declined this offer, instead asking to spend more time on the Ethernet IP until it could be considered "complete". This meant comprehensive verification and documentation, software support, and integration into an SoC.

Now ending my placement over week 11, I'm happy to have taken that path. I didn't get the same chance to work on other new, exciting RTL work, but I am immensely happy with the Ethernet IP. It has what I consider to be excellent documentation, a strong test suite, and coverage collectors (which, admittedly, revealed some holes in the test suite).

I submitted a Pull Request to overwrite a piece of legacy Ethernet IP, and my designs are now officially public on the lowRISC GitHub.

# Lessons Learned

Keep a checklist. There are a million little things to check and you will forget some -- functional correctness, documentation, CDC, RDC, power, timing, correct handling of primitives, protocol compliance. In future projects I would like a sign-off checklist detailing which of these items should be checked and at what intervals.

In a similar vein, I think it would be valuable to me to start all my projects from a template moving forward. Setting up those flows is cumbersome, which makes it tempting to skip them, or do it manually 'from time to time'.

# Git is still amazing
Obviously I had used Git before, but more often for my own work than collaborative projects.

In particular, I find using fixups with an autosquashing interactive rebase to be excellent.

# Some specific skills I learned

- AXI4
- AXI ATOPS
- AXI Stream
- (R)(G)MII
- Ethernet protocol
- Some tcl
- SVA's

# A wishlist
- FuseSoC is nearly great but basically terrible
-

# CocoTB is excellent
One of the first questions I asked myself starting out in the semiconductor industry: Why are testbenches written in SystemVerilog, a hardware description language (HDL)?

The answer of course is that SystemVerilog is not just a HDL, it is also an object-oriented languages, and includes a language for writing properties in formal notation. This is an awful mess of three languages mushed into one, and I am of the opinion that the non-synthesisable constructs of SystemVerilog should be stripped out, and it reserved purely for hardware description.

Tests are *software*. They run procedurally, albeit with multiple threads. It stands to reason that they ought to be written in a conventional programming language. This is where CocoTB comes in: a Python package that provides the means to drive and monitor signals in an RTL design. This is invaluable for verification -- all the cumbersome syntax and infrastructural overhead of SystemVerilog is replaced by a Python script.

Of course, I am biased because I know Python extremely well and know very little about using SystemVerilog for verification. Nonetheless, I see the following objective advantages of using CocoTB:

* Access to the Python ecosystem of package to aid in modelling the DUT (e.g. DSP is very easy in Python)

* Access to the Python ecosystem for infrastructural tools like linting, test frameworks, etc.

* Increased object-oriented programming capabilities when compared to SystemVerilog

* Behavioural modelling of your DUT is better done in a language other than SystemVerilog to prevent the same bug from being introduced in both the DUT and the model. This is possible in SystemVerilog using the C DPI, but not straightforward.

# Test your tests for reproducibility
Reproducibility is vital -- given the same random seed, the same test needs to be able to be recreated.

During the later stages of my Ethernet project I was starting to feel relatively confident in design, when I encountered an unexpected failing test. Praying it was something I could simply defeature, I copied the seed, enabled tracing, and re-ran the test.

It passed.

Panic mode. I now know that there is a bug somewhere in my code -- hopefully in a test, but maybe in the design itself -- and I have no idea where or how to recreate it. What's worse, the re-run had overwritten the log files from the previous failed run, so I had nothing to go on.

At a loss for alternatives, I set up a script to run that *single* test on loop until it failed again, then went to bed.

The next morning I saw, fortunately, that it had failed again within an hour -- I was able to identify the bug (it was, indeed, with the test, not the design) and correct it. Still, I was concerned: what if the next bug is a one-in-a-billion edge case? It's not an unreasonable possibility.

So, my lesson was learned: it's not enough to dump a seed out at the start of your test run, you need to make sure that seed is used everywhere there is RNG, and not accidentally replaced anywhere in the flow.

This is a form of what I'm calling "meta-testing" -- that is, testing your tests.

# Meta-testing
The other, more obvious, form of meta-testing is testing that design *fail* when the dzesign they are testing is broken.

I am still brainstorming clean ways of doing this -- of course there are obvious options like injecting errors into input/output data, but the trickier question is in how to implement the *flow* to do that. Ideally, you want the bad behaviour to be implemented in the source code of your design rather than 'patched on'; that is to avoid introducing a new complication that needs testing.

You could, for example, use 'diff' (or 'git diff') to store some 'breaks'. Then create a simple script to apply to those diffs, run the tests, and expect the appropriate failures.

# Using AXI
This was my first time using AXI, and








Lessons learned:
    - CocoTB is excellent
    - Reproducibility is vital
    - Trial synthesis is part of your regression suite
    - Design is not even half the battle
    - Go Karting
    - Leadership transparency
    - FPGA's for test and development
    - Scope for technical ownership
    - Staving off technical debt
    - Learning opportunities and mentorship
    - Creating templates is useful
    - Benefits and disadvantages of sitting in a room with a different team
    - Sign-off checklists (there's a lot of little things to double-check that are easy to overlook)
    - The disconnect between design effort and realised cost
    - The importance of resource utilisation
    - FuseSoC
    - Musings on version control, package management, FuseSoC cores, and hashing
    - Loopback multiplexor
    - AXI is cool
    - AXI Stream is cool
    - Boilerplate assertions for those protocols would be good
    - Thoughts on coverage: where to place collectors, pairwise cross-coverage, and why bins come in threes
    - Idea: you should have zero pipeline stages in a design if at all possible - if you need them for timing, introduce them separately, but keep the pipelining decoupled from the design itself
    - Memory is hard
    - lowRSIC code is very readable, take a look
    - Automating SystemVerilog stuff - why isn't there a good IDE for this?
