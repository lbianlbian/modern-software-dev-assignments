# Week 3 Write-up

**Skill name**, and the repo you targeted:
> repo-onboarding, TheAlgorithms/Python

## Part I: The Workflow

**What the workflow is**, and why it's worth encoding:
> Given a change that a new developer wants to make to a repo, the workflow finds and then summarizes the relevant parts of the repo so that the developer can understand what will be affected by the change and how to make the change.if the change isn't feasible, the workflow suggests a similar change that is possible based on the contents of the repo. This is worth encoding because many times in software development, developers must make a change to a repo they are not familiar with. 

**The decision point** in it (what the agent has to judge, not just execute):
> The agent has to judge which directory/files  could hold the requested function and are relevant, or if the specified function (may not exactly match the true function name) exists at all. 

**What you learned running it manually** that you would not have guessed:
> I learned by going through this process manually that one useful part of the skill could be to suggest similar tasks to do based on discoveries of the repo's content that the user may not have thought of if the user's specified task turns out to not be feasible. 


## Part II: The Skill

**Your description**, verbatim:
```
Orient a developer to an unfamiliar repository before they build a specific feature. Finds and summarizes only the files, conventions, and commands relevant to that feature, judges whether the feature fits the codebase, and proposes similar feasible features if it doesn't. Use when someone asks "where would I add X", "how would I implement X in this repo", "what do I need to understand to build X", "is X possible here", or "onboard me to this codebase for X". Do not use for implementing the change, explaining a single function, or general code review.
```

**Why it's worded that way** (what a user would type to trigger it):
> A new developer rarely types "onboard me." They ask a question about a specific feature, like "where would I add X" or "is X possible here," so the description quotes those phrases directly. The first sentence says what the skill does, including the alternate-feature suggestion, which sets it apart from a generic code explainer. The final "Do not use for..." sentence keeps it from firing on nearby requests that a different workflow should handle: actually implementing the feature, explaining a single function, or reviewing code.

**Judgment encoded in the body** (what it says to do when things are ambiguous, and what not to do):
> Ambiguous request: ask one clarifying question only if two readings would lead to materially different change points. Otherwise state the interpretation and continue. Locating the change point: search the key terms plus 2–3 synonyms. If one directory clearly holds similar code, use it. If there are several, pick the one whose existing files look most like the new code and name the runner-up with the reason it lost. If nothing matches, say the functionality is absent rather than stretching a weak match. Feasibility: give a three-level verdict (Fits / Fits with adaptation / Doesn't fit) that checks the repo's stated purpose and dependency rules, not just whether the feature is technically possible. Alternatives: each must point to a real file and keep the user's intent, and they are offered as options rather than silently swapped in. Don'ts: don't implement the feature, don't describe files you haven't opened, don't summarize unrelated parts of the repo, and don't invent commands.

**Supporting files**, if any, and why they aren't inline:

| File | Contents | Why it's separate |
|---|---|---|
| `repo-onboarding/feasibility-guide.md` | Verdict definitions, questions for judging fit, how to generate and rank alternatives, a worked TheAlgorithms/Python example | Only needed at steps 4–5, and only in depth when the feature doesn't fit, so it doesn't need to load every time the skill fires |
| `repo-onboarding/report-template.md` | The fixed output format for the briefing | It's a static template, not judgment, and it's only needed at the final step |


## Part III: Testing

**Triggering:**

| Prompt | Should fire? | Did it? |
|---|---|---|
| /repo-onboarding i want to add a web ui for the string is number function in the Python repository | Yes | Yes |
| I want to make a web UI for the string is number in the Python repo how should I do it? | Yes | Yes |
| I'm about to make a web UI for a levenshtein distance function in Python. What will be affected? | Yes | Yes |
| The number-ui/ directory has a Flask App that provides a web UI for one of the functions in the Python repo. I don't really understand the Python repo but it's OK. I just want to make the number-ui/ flask app show flashing red text when a string isn't a number instead of showing just plain red text | No (near-miss) | No |

**End-to-end run** on your repo, and the result:
```
> I want to make a web UI for the string is number in the Python repo how should I do it?

● Skill(repo-onboarding)
Successfully loaded skill

  Listed 1 directory, ran 4 shell commands

Here's the briefing.

Onboarding: Web UI for "string is valid number"

Interpretation: the user types a string in a browser → the page shows whether it's a valid number (and, ideally, why). This is something that uses the repo from outside, not a change to the algorithm.
Verdict: Fits with adaptation. The logic is already in the repo and easy to import, but a web app goes against the repo's purpose and its dependency list, so the UI should live outside it.

What this repo is (relevant to you)

This is TheAlgorithms/Python: a collection of standalone educational algorithms, each with doctests. Contributors should write functions that "return all calculation results" and have "minimal side effects" (CONTRIBUTING.md, "What is an Algorithm?"), and new files go inside an existing directory (AGENTS.md:34). There's no web framework among the dependencies: pyproject.toml lists numpy, pandas, httpx2 and similar, but not Flask, FastAPI or Streamlit.

Where the change goes

- Logic you'll call: strings/string_is_valid_number.py. It's the only real match after searching for isnumeric, isdigit, is_number and numeric.
- Runner-up: none worth considering. Other hits like maths/is_ip_v4_address_valid.py and strings/credit_card_validator.py only call isdigit() for other purposes.
- UI location: a separate folder outside Python/, for example modern/number_ui/, that imports from the repo.
- Files to read first:
  - strings/string_is_valid_number.py:99: is_valid_number(number_string: str) -> bool is the entry point.
  - strings/string_is_valid_number.py:28: state_machine is a module-level dict of DFA transitions.
  - strings/string_is_valid_number.py:54: classify_char() maps one character to a CharType, or None if the character isn't allowed.
  - strings/string_is_valid_number.py:108-151: the doctests give you ready-made valid and invalid examples to pre-fill the UI.

state_machine and classify_char are both public, so the UI can show the DFA's state after each character, not just True/False. That makes for a better educational demo:
from strings.string_is_valid_number import State, classify_char, state_machine
state, trace = State.INITIAL, []
for ch in text:
    t = classify_char(ch)
    state = state_machine[state].get(t) if t else None
    trace.append((ch, t, state))
    if state is None: break

Conventions to follow

These apply only if you change the repo. A UI outside the repo doesn't need them.
- Type hints on every function (AGENTS.md:27), plus doctests that cover valid and invalid input (AGENTS.md:29).
- One algorithm file per PR, and never change code and its doctests in the same PR (AGENTS.md:18-21).

Commands

┌───────────────┬────────────────────────────────────────────────────────────────┬────────────────────────────────┐
│    Purpose    │                            Command                             │             Source             │
├───────────────┼────────────────────────────────────────────────────────────────┼────────────────────────────────┤
│ Install       │ uv sync --group=test                                           │ .github/workflows/build.yml:23 │
├───────────────┼────────────────────────────────────────────────────────────────┼────────────────────────────────┤
│ Test one file │ uvx pytest strings/string_is_valid_number.py --doctest-modules │ AGENTS.md:46                   │
├───────────────┼────────────────────────────────────────────────────────────────┼────────────────────────────────┤
│ Full CI test  │ uv run --with=pytest-run-parallel pytest ...                   │ build.yml:34                   │
├───────────────┼────────────────────────────────────────────────────────────────┼────────────────────────────────┤
│ Lint/format   │ uvx pre-commit run --all-files                                 │ AGENTS.md:45                   │
└───────────────┴────────────────────────────────────────────────────────────────┴────────────────────────────────┘

What it will affect

- Watch out: there's an untracked Python/test_web_app.py at the repo root. It imports flask (test_web_app.py:1), which isn't a dependency, and it imports strings.pig_latin. Its name matches test_*.py, so plain pytest (the CI command at build.yml:34) will try to collect it and fail on the import. Ruff will probably flag it as well, because it's a root-level file outside any package. I'd move it out of the repo.
- A UI that lives outside the repo touches nothing in it: no DIRECTORY.md entry, no CI impact.

Options

1. Standalone app outside the repo (recommended). Write a small Flask, FastAPI or Streamlit app in a sibling folder that puts Python/ on sys.path and calls is_valid_number, optionally with the state trace above. This keeps 100% of what you asked for.
2. Same app, but contribute a trace_states() helper upstream. Add a function to string_is_valid_number.py that returns the list of states, with doctests. That part is a valid repo contribution, and the UI just displays its output.
3. Zero-dependency version. Write a single HTML page backed by http.server from the standard library, so you don't install a framework at all.

Next step: which framework do you want (Flask, Streamlit, or the standard library), and should the UI show just valid/invalid or the step-by-step DFA trace?

✻ Baked for 43s · done 5:55 PM

> Flask and UI should just show valid/invalid

  Ran 1 shell command

I'll build it in a new modern/number_ui/ folder next to the repo, so nothing inside Python/ changes.

● Write(app.py)
Wrote 48 lines to app.py
"""Minimal Flask UI for TheAlgorithms' strings/string_is_valid_number.py."""

import sys
from pathlib import Path

from flask import Flask, render_template_string, request

# Make the sibling TheAlgorithms repo importable without installing it.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "Python"))
… +38 lines

  Ran 1 shell command

I built the web UI as one Flask file, number_ui/app.py, in a new folder next to Python/, so the repo itself is unchanged.

It's a single page with a text box and a "Check" button. It passes your input to the repo's existing is_valid_number() and shows a green "is a valid number" or a red "is not a valid number" message.

Run it from modern/number_ui/:
uv run --no-project --with flask python app.py
Then open http://127.0.0.1:5000. This uses uv to fetch Flask into a throwaway environment, so nothing is installed globally. If you'd rather install Flask normally (pip install flask), python app.py works too.

Tested with Flask's test client: -123.456e789 and 4. came back valid, and 1e, abc and an empty string came back invalid, matching the repo's doctests. I also checked that input like <b>x</b> is shown as plain text rather than as HTML.

One leftover from before: the untracked Python/test_web_app.py still imports Flask. If you run pytest inside the repo it will try to collect that file and fail on the import, so I'd delete it or move it out of the repo. I didn't touch it.

✻ Churned for 58s · done 5:57 PM

```


## Submission
1. `Command (⌘) + F` for `TODO`. No results means you're done.
2. Confirm the skill directory itself is committed under `week3/`.
3. Push all changes to your remote repository and submit via Gradescope.
