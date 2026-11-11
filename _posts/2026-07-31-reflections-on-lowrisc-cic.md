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

## Keep a signoff checklist
There are a million little things to check and you will forget some -- functional correctness, documentation, CDC, RDC, power, timing, correct handling of primitives, protocol compliance checks, trial synthesis. In future projects I would like a sign-off checklist detailing which of these items should be checked and at what intervals.

In a similar vein, I think it would be valuable to me to start all my projects from a template moving forward. Setting up those flows is cumbersome, which makes it tempting to skip them, or do it manually 'from time to time'.

## Git is still amazing
Obviously I had used Git before, but more often for my own work than collaborative projects.

In particular, I find using fixups with an autosquashing interactive rebase to be excellent.

## CocoTB is excellent
I wrote a [whole post about it]({% post_url 2026-11-05-a-love-letter-to-cocotb %}).

## Test your tests for reproducibility
Reproducibility is vital -- given the same random seed, the same test needs to be able to be recreated.

During the later stages of my Ethernet project I was starting to feel relatively confident in design, when I encountered an unexpected failing test. Praying it was something I could simply defeature, I copied the seed, enabled tracing, and re-ran the test.

It passed.

Panic mode. I now know that there is a bug somewhere in my code -- hopefully in a test, but maybe in the design itself -- and I have no idea where or how to recreate it. What's worse, the re-run had overwritten the log files from the previous failed run, so I had nothing to go on.

At a loss for alternatives, I set up a script to run that *single* test on loop until it failed again, then went to bed.

The next morning I saw, fortunately, that it had failed again within an hour -- I was able to identify the bug (it was, indeed, with the test, not the design) and correct it. Still, I was concerned: what if the next bug is a one-in-a-billion edge case? It's not an unreasonable possibility.

So, my lesson was learned: it's not enough to dump a seed out at the start of your test run, you need to make sure that seed is used everywhere there is RNG, and not accidentally replaced anywhere in the flow.

This is a form of what I'm calling "meta-testing" -- that is, testing your tests.

## Meta-testing
The other, more obvious, form of meta-testing is testing that design *fail* when the dzesign they are testing is broken.

I am still brainstorming clean ways of doing this -- of course there are obvious options like injecting errors into input/output data, but the trickier question is in how to implement the *flow* to do that. Ideally, you want the bad behaviour to be implemented in the source code of your design rather than 'patched on'; that is to avoid introducing a new complication that needs testing.

You could, for example, use 'diff' (or 'git diff') to store some 'breaks'. Then create a simple script to apply to those diffs, run the tests, and expect the appropriate failures.

## Design is not even half the battle
Including integration with the SoC top, software integration, documentation, flow setup, maintaining a clean workspace, and (most of all) writing countless tests, I would say that actual RTL design occupied about a quarter of my time on the Ethernet project. The idea that the design work is only a small fraction of the overall effort was not new to me, but I certainly underestimated the extent!

## FPGA's for Testing are Amazing
One wonderufl feature of lowRISC's workflows is the use of FPGA's for regression tests. Every pull request submitted to the GitHub repo is put into the pipeline to build, and this pipeline runs on a server connected to an array of FPGA's! That mean all designs are portable for ASIC or FPGA retargeting, and it means tests run orders of magnitude faster!

Having designs portable for ASIC and FPGA does add some overhead -- however I would argue it enforces good, clean separation of design from primitives, which makes retargetting for a different ASIC library easier in future.
