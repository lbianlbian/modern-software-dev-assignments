# Feasibility Guide

## Verdicts
- **Fits**: matches the repo's purpose, needs no new disallowed dependencies, and has
  an obvious home that follows existing conventions.
- **Fits with adaptation**: the core logic belongs here, but part of the request
  (UI, I/O, a heavy dependency) doesn't. Split it: say what goes in the repo and what
  lives outside it.
- **Doesn't fit**: it conflicts with the repo's stated purpose or contribution rules,
  or the needed functionality is absent and out of scope.

## Questions to ask
1. Does CONTRIBUTING/README say what kinds of contributions are accepted?
2. Would it add a dependency? Check whether similar files import anything beyond the
   stdlib or the existing deps.
3. Does the repo have any infrastructure of the needed kind (web server, CLI, DB)? If
   not, building it is a new subsystem, not a feature.
4. Does the existing code expose a usable entry point (a pure function, a class) that
   the feature could call from outside?

## Picking alternatives
Good alternatives keep the user's *intent* and change the *shape*:
- **Same goal, different scope**: a standalone script/app that imports from the repo
  instead of a change inside it.
- **Same shape, different target**: the same kind of feature built on a module that
  does exist.
- **Smaller slice**: the in-scope part only (e.g., the algorithm plus doctests, without
  the UI).

Rank them by how much of the original intent they keep. Reject any alternative you
can't point to a file for.

## Example (TheAlgorithms/Python)
Request: "add a web app that visualizes a sorting algorithm."
- Repo purpose: standalone educational implementations with doctests and no web
  framework, so a web app inside the repo is **Doesn't fit**.
- Alternatives:
  1. A separate Flask/Streamlit app outside the repo that imports
     `sorts/bubble_sort.py`.
  2. Add a step-yielding generator variant of a sort, which fits the repo's style and
     could drive a visualization.
  3. Improve doctests for an under-tested sort.
