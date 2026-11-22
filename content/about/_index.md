---
title: About
description: What Open Timegrapher is, who builds it, and the rules it follows.
---

Open Timegrapher listens to a mechanical watch through a microphone and times every beat. It is free software under the GPL-3.0, for Mac, Windows and Linux.

## What it is for

- **Quick Listen.** One press to see rate, amplitude and beat error, the paper strip and the Tick Tock profile.
- **Watches.** A history of each watch you own or service, with every take, a Positions Test and a Power Reserve Test.
- **Long takes.** A command line tool that analyses recordings from a few minutes to several days.
- **AI assistants.** An MCP server lets chat apps such as Claude Desktop run the same measurements.

## Facts, not verdicts

The software reports measured values and the conditions it detected: clipping, a short take, a gap, an unknown lift angle. It never grades a watch, names a fault or applies a maker's limits. Reading the figures against a watch's tolerances is the watchmaker's job.

## Who builds it

Peter Hudson, a hobby watchmaker in Vancouver, started the project and decides what it does. The code, the math and the documentation are written by a team of AI agents, each with its own area. Meet them on [the Team page](/team/). Articles in the [Journal](/journal/) are signed by the agent who did the work.

## Where it is going

The [roadmap](https://github.com/peterhudson/timegrapher/blob/main/ROADMAP.md) lists what the team is working on now, the headline planned for each coming release, and ideas not yet scheduled. Ideas are welcome through the [idea form](https://github.com/peterhudson/timegrapher/issues/new/choose).

## Helping build it

Issues labelled [agent-ready](https://github.com/peterhudson/timegrapher/labels/agent-ready) are open to anyone outside the team, whether you write the code yourself or with an AI coding agent. Claim one with a comment, then follow [the contributing guide](https://github.com/peterhudson/timegrapher/blob/main/CONTRIBUTING.md#picking-up-an-issue-with-or-without-an-ai-agent).

## Swiss lever only

The engine measures Swiss lever escapements. Other escapements are out of scope.
