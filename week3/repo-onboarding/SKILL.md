---
name: repo-onboarding
description: Orient a developer to an unfamiliar repository before they build a specific feature. Finds and summarizes only the files, conventions, and commands relevant to that feature, judges whether the feature fits the codebase, and proposes similar feasible features if it doesn't. Use when someone asks "where would I add X", "how would I implement X in this repo", "what do I need to understand to build X", "is X possible here", or "onboard me to this codebase for X". Do not use for implementing the change, explaining a single function, or general code review.
---

# Repo Onboarding for a Feature

The goal is a **targeted briefing**, not a tour of the repo. Only summarize what the
developer needs in order to make *this* change. Do not write the feature.

## 1. Pin down the request

Restate the feature in one line as: **what it takes in → what it produces → what kind
of change it is** (new module / extend existing code / something that *uses* the repo
from outside). If the request can be read two materially different ways, ask one
clarifying question before searching. Otherwise state your interpretation and go on.

## 2. Map the repo (deterministic)

Run these and read the results before opening any source file:

    git ls-files | sed 's|/[^/]*$||' | sort | uniq -c | sort -rn | head -40   # where code lives
    ls
    cat README.md CONTRIBUTING.md 2>/dev/null | head -200
    ls DIRECTORY.md docs/ 2>/dev/null                                      # indexes, if any
    cat pyproject.toml package.json setup.cfg requirements*.txt 2>/dev/null # deps, test/lint cmds

From these, write down: what the repo *is for*, the build, test, and lint commands,
and the rules contributors must follow (allowed dependencies, file conventions, test style).

## 3. Locate the change point (the judgment step)

Search for the feature's key terms **and at least 2–3 synonyms**. For example, a request
for "shortest path" should also search "dijkstra", "bfs", and "graph":

    git grep -il "<term>" -- '*.py' | head -30
    git ls-files | grep -i "<term>"

Then decide:
- **One clear home**: a directory already holds similar code. That is the change point.
- **Several candidates**: choose the one whose existing files most look like what the
  new code would be (same inputs and abstractions). Name the runner-up and explain why it lost.
- **No matches even after synonyms**: treat the functionality as absent. Say so
  plainly and don't stretch a weak match to make it fit.

Open only the chosen files, **one neighboring file** (to learn the conventions), and
the tests for them. Don't read files you won't cite.

## 4. Judge feasibility

Give one verdict: **Fits**, **Fits with adaptation**, or **Doesn't fit**.
Use [feasibility-guide.md](feasibility-guide.md) for the criteria. The most common
mistake is not noticing that a feature conflicts with the repo's purpose or dependency
rules even though it's technically possible.

## 5. If it doesn't fit, propose alternatives

Suggest 1–3 similar features that *do* fit. Each one must be grounded in a specific file
or directory you actually looked at, and it must keep the user's underlying intent. See
[feasibility-guide.md](feasibility-guide.md). Present them as options for the user to
choose from. **Never silently swap in an alternative and carry on as if the user asked
for it.**

## 6. Report

Fill in [report-template.md](report-template.md). Every claim about the code cites a
`path:line`.

## Don'ts
- Don't implement the feature or write code beyond a ≤10-line illustrative snippet.
- Don't describe a file you haven't opened.
- Don't summarize parts of the repo the feature won't touch.
- Don't invent commands. Only list ones found in the config files, README, or CI.
