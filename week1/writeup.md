# Week 1 Write-up

## Part I: Capture

**Setup** (enough for a reader to reproduce your capture):
```
claude --version:  2.1.288
mitmproxy version: 12.2.3
proxy command:     mitmweb --listen-host 127.0.0.1 --listen-port 58888 \
        --web-open-browser --mode reverse:https://api.anthropic.com \
        -w session.flows
settings file:     donny_the_dealer_locus_hackathon/.claude/settings.json
```

**The session.** What task, against what repo, and how many `POST /v1/messages` requests did it produce?
I used a previous repo I submitted to a hackathon, anad I deleted a function that was imported by different modules, removed references to files, and purposefully broke a test. It produced 22 POST v1/messages requests. 

| Requirement | Evidence |
|---|---|
| Touched ≥ 2 files | index.html, script.js, test/script.test.js |
| Failed at least once | I broke a test that Claude Code ran and saw fail.  |
| Long enough to plan | I activated plan mode and this task had significant enough changes that a plan was generated. |
| Your own repo | https://github.com/lbianlbian/donny_the_dealer_locus_hackathon |

**What you redacted** from the excerpts quoted below, and why:
I redacted filepaths of my local device because that is private and I was instructed to do so and the full filepaths are not necessary to understand the code, only the filepaths starting from the repository root. I did not have a .env file in the repository so I did not have any secrets to redact. I also redacted my email address. 


## Part II: System Prompt Annotation

**a. Structure.** Major sections in order, one line each on what it does, and why this order.
### System prompt in messages
- Environment: Lists the current directory, operating system, scratchpad directory, and similar information. 
- Tools: Lists all tools available to the model without their schemas and description. 
- Agent Types for Agent Tool: Lists and describes the different agents available for the agent tool. 
- Skills for Skill Tool: Lists and describes the different skills available for the skill tool. 
- Miscellaneous: Describes auto-mode, the number of tokens left, and today's date. 

This order exists because tokens can only attend to those that come before it, so specific tool detailed descriptions like agent and skills come after the list of the tools. The tools may depend on the environment so they come after the environment. 

### System prompt in system
- Description of Identity: Describes to the LLM its job and guardrails to not perform dangerous tasks. 
- Harness: Description of how user will interact with Claude Code and also instructions to ask for approvals. 
- Session-specific guidance: Instructions on getting user to run shell commands and invoking skills. 
- Memory: Description of where memories are stored, how to store them, and how they will be used. 
- Environment: Describes model used and states Claude Code is used in a terminal. 
- Context Management: Description of summarization, instructions for no repetition and end chat, and tokens left. 

This order, like the other system prompt, exists so that information that depends on other information is ordered in a way such that the information it depends on comes first. 

**b. Tone and verbosity.** Quote the controlling instructions, then say what failure mode they defend against.
```
You are an agent working with the user toward their goals, using your own judgment along the way.

Write code that reads like the surrounding code: match its comment density, naming, and idiom.

```
These instructions defend against the agent refusing to help the user with their tasks and the agent writing code that the user isn't familiar with and can't understand. 

**c. When not to act.** Quote the destructive-operation gates, scope limits, or refusal conditions, and what each buys.
```
IMPORTANT: Assist with authorized security testing, defensive security, CTF challenges, and educational contexts. Refuse requests for destructive techniques, DoS attacks, mass targeting, supply chain compromise, or detection evasion for malicious purposes. Dual-use security tools (C2 frameworks, credential testing, exploit development) require clear authorization context: pentesting engagements, CTF competitions, security research, or defensive use cases.

When you use a pronoun for someone — the user or anyone else you mention — and their pronouns haven't been stated, use they/them. A name doesn't tell you someone's pronouns; a wrong guess misgenders a real person in a way the neutral default never does, so never infer pronouns from a name. This applies to all user-visible text, including visible thinking.

For actions that are hard to reverse or outward-facing, confirm first unless durably authorized or explicitly told to proceed without asking; approval in one context doesn't extend to the next. Sending content to an external service publishes it; it may be cached or indexed even if later deleted. Before deleting or overwriting, look at the target. Report outcomes faithfully: if tests fail, say so with the output; if a step was skipped, say that; when something is done and verified, state it plainly without hedging.

When you have enough information to act, act. Do not re-derive facts already established in the conversation, re-litigate a decision the user has already made, or narrate options you will not pursue. If you are weighing a choice, give a recommendation, not an exhaustive survey

EndConversation (deferred tool): use only for sustained user abuse directed at the assistant, or when the user explicitly asks to see it demonstrated. Load the full guidance via ToolSearch(\"select:EndConversation\") before using it.

```
The first one helps to prevent Claude Code from being used for illegal activity. The second one helps to prevent Claude Code from offending the user or anyone else by using the wrong pronouns. The third one helps to encourage Claude Code to confirm before taking actions that could have consequences outside of the sandbox of the local terminal and to not cover up any potential mistakes. The fourth one aims to avoid repetitive text which wastes the available context and is also inconvenient to read. The final one ensures that Claude does not prematurely end a conversation except when it should. 

**d. Environment context.** What the agent is told about machine/repo/session, and where it lives in the request (`system` field or a `role: "system"` message).
The agent is told if the directory it is in is a git repo, which platform, OS, shell, the name of the directory it is in, and the direcotry of its scratchpad. This lives in the role: "system" message, not in the system field.  

**e. `<system-reminder>`.** Where they appear (cite an example), two distinct purposes you can evidence, and why they are injected mid-conversation rather than stated once.
```
<system-reminder>\nAttribution for git commits and pull requests you create from here on (this replaces Claude Code's own earlier attribution guidance, such as a previous copy of this reminder; the user's own instructions about these lines, such as a CLAUDE.md or memory rule, take precedence over this reminder, but do not add attribution lines this reminder leaves out):\n- End git commit messages with:\nCo-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>\n- End pull request descriptions with:\n🤖 Generated with [Claude Code](https://claude.com/claude-code)\n</system-reminder>

"description": "Fetches full schema definitions for deferred tools so they can be called.\n\nDeferred tools appear by name in <system-reminder> messages. Until fetched, only the name is known — there is no parameter schema, so the tool cannot be invoked. This tool takes a query, matches it against the deferred tool list, and returns the matched tools' complete JSONSchema definitions inside a <functions> block. Once a tool's schema appears in that result, it is callable exactly like any tool defined at the top of the prompt.\n\nResult format: each matched tool appears as one <function>{\"description\": \"...\", \"name\": \"...\", \"parameters\": {...}}</function> line inside the <functions> block — the same encoding as the tool list at the top of this prompt.\n\nQuery forms:\n- \"select:Read,Edit,Grep\" — fetch these exact tools by name\n- \"notebook jupyter\" — keyword search, up to max_results best matches\n- \"+slack send\" — require \"slack\" in the name, rank by remaining terms",

```
The above `<system-reminder>` appears in the second user message, and the other `<system-reminder>` tags all appear in text descriptions, either inside user messages or system messages. Some agent tool call descriptions include `<system-reminder>` when instructing how to interact with it if seen elsewhere. The purpose of the `<system-reminder>` above is to instruct Claude Code to add itself as a contributor to git commits. Another distinct purpose of `<system-reminder>` is to hold deferred tools, as evidenced by the description of the ToolSearch tool. `<system-reminder>` is injected mid-conversation instead of stated once because it describes things that could change later but would belong in a system prompt if they did not ever change. 

## Part III: Tool Design Annotation

**Inventory.** Did the set change across requests? If so, what triggered it?

| Built-in | MCP | Deferred | **Total** | Changed mid-session? |
|---|---|---|---|---|
| 37 (18 loaded with full schemas at the start, 19 deferred; 19 loaded / 18 deferred after `ExitPlanMode` was loaded) | 42 from 21 claude.ai connectors (all deferred, an `authenticate` / `complete_authentication` pair per connector, none ever loaded) | 61 at the start (19 built-in + 42 MCP), listed by name only in the `role: "system"` message at `messages[1]`; 60 after the change | **79** | Yes, once. `ExitPlanMode` moved from deferred to loaded after `ToolSearch {"query": "select:ExitPlanMode"}` at msg 20 |

Evidence is from the plan-mode session (`session_with_plan_and_failure.json`, the final request body, 40 messages), cross-checked against the earlier sessions in `session.flows`.

- **At the start**, `tools[]` has 19 entries: 18 loaded built-ins plus a `DeferredToolPlaceholder` with `defer_loading: true` and the description "Reserved placeholder that keeps deferred tool loading active; never call this tool." I didn't count it as a real tool. The 18 loaded tools are Agent, Artifact, AskUserQuestion, Bash, Edit, Glob, Grep, ListAgents, PowerShell, Read, ReportFindings, ScheduleWakeup, SendFeedback, ShareOnboardingGuide, Skill, ToolSearch, Workflow, and Write. The 19 deferred built-ins include WebFetch, WebSearch, EnterPlanMode/ExitPlanMode, NotebookEdit, SendMessage, TaskStop, and CronCreate/CronDelete/CronList.
- **What triggered the change:** plan mode told the model it had to end its planning turn by calling `ExitPlanMode`, but that tool was only deferred. So at msg 20 the model called `ToolSearch {"query": "select:ExitPlanMode", "max_results": 1}`. The result at msg 21 isn't a schema in text. It's a structured block, `[{"type": "tool_reference", "tool_name": "ExitPlanMode"}]`, plus the text "Tool loaded." In the final request, `tools[]` has **20 entries**, with the full `ExitPlanMode` schema at index 5, and the model called it at msg 23.
- **The deferred list was never rewritten.** `messages[1]` still lists all 61 names, including `ExitPlanMode`, because earlier messages are replayed exactly as they were (see IV e). The change shows up only in `tools[]`.
- **No change in the earlier sessions.** In `session.flows`, `tools[]` is byte-identical across all 12 agent requests (requests 3–6 and 9–16), because those sessions never called ToolSearch. Requests 2 and 8 are short side calls that send 0 tools, so they aren't part of the agent loop.

**Two tools.** Pick tools that differ from each other.

| | Tool 1 | Tool 2 |
|---|---|---|
| Name | `Edit` | `Agent` |
| Key schema fields | `file_path` (absolute path), `old_string`, `new_string`, `replace_all` (boolean, default false) | `description` (3–5 words), `prompt`, `subagent_type` (`"fork"` or a named agent type), `model` (enum: sonnet/opus/haiku/fable), `isolation` (enum: `worktree` / `remote`) |
| Required vs. optional vs. not exposed, and why | Required: `file_path`, `old_string`, `new_string`. Optional: `replace_all`. Not exposed: line numbers or ranges, regex, or edits to several files in one call. Edits are addressed by content instead of by position, so an edit can't land on the wrong line after the file shifts. A non-unique match fails instead of guessing which occurrence was meant. | Required: `description`, `prompt`. Optional: `subagent_type`, `model`, `isolation`. Not exposed: a tool allowlist, a timeout, or any way to pass the parent's context. Everything the subagent knows has to be written into `prompt`, unless the parent uses `fork`. Tools, model, and effort come from the agent definition (`.claude/agents/*.md`), not from the call. |
| Description is defending against… (quote + the wrong behavior) | "Strip the Read line prefix (line number + tab) before matching." Read returns `cat -n`-style output, and models kept copying the line-number prefix into `old_string`, so the match failed. Also: "You must Read the file in this conversation before editing, or the call will fail." This stops edits made against a remembered or hallucinated version of the file. | "Never fabricate or predict a pending agent's results — the notification is never something you write yourself." Models were writing what they expected the subagent to return instead of waiting. Also: "Once you've delegated a search, don't also run it yourself," which stops duplicated work, and "The agent's final report is not shown to the user — relay what matters," which stops the model assuming the user already saw it. |
| Deliberately does *not* do… and what that implies | It doesn't read the file, and it doesn't return the new contents. That implies the harness tracks which files the model has read and how current they are. I observed this in the plan-mode session at msgs 27 and 30. All six Edit/Write results there say "(file state is current in your context — no need to Read it back)". The files had been Read at msg 5, so each Edit at msg 26 went through without the model reading the file again first. | It doesn't share the parent's context (except with `fork`), and it doesn't show its output to the user. That implies subagents are a way to manage context: their file dumps stay out of the parent's window, and only a summary comes back ("you keep the conclusion, not the file dumps"). Results arrive asynchronously as notifications. A separate SendMessage tool continues an agent, which means the harness keeps a registry of running agents. |

Why these two?
> They have very different failure contracts. `Edit` is a strict, synchronous file tool. It fails loudly when the model's picture of the file is wrong, such as a stale read, a non-unique match, or a copied line prefix, and it depends on the harness tracking what has been read. `Agent` is an asynchronous orchestration tool. Its failure modes are behavioral (making up results, duplicating delegated work, forgetting to pass results on to the user), so its description has to defend against them in prose because the schema can't. Note: `Edit` was called in my trace (plan-mode session, 4 calls at msg 26 and 2 at msg 29). `Agent` was never called, so the `Agent` column analyzes the schema and description, not behavior I observed. The trace does show the model deciding *not* to use it, even though the plan-mode instructions pointed it toward subagents (see IV d).


## Part IV: Behavioral Analysis

**Every answer must be labeled `[OBSERVED]` or `[INFERRED]` and cite its evidence. Unlabeled answers earn no credit.**

All evidence below is from `session_with_plan_and_failure.json` (the final request body of the plan-mode session, 40 messages; "msg N" means `messages[N]`), unless I say otherwise.

**a. Error recovery**: `[OBSERVED]` · evidence: msg 8 PowerShell `npm test` → msg 9 `tool_result` with `is_error: true` → diagnosis msgs 11–15 → plan msgs 17–24 → Edits msg 26 and msg 29 → re-run msg 29 → msg 30 `# fail 0`. Second failure: smoke test msg 35 → unexpected result msg 36 → reported in msg 38.

What the agent saw, verbatim (msg 9, the only `tool_result` in the session with `is_error: true`; TAP lines trimmed to the failures and the summary):
```
Exit code 1
  ...
# Subtest: handleInput reports network failures
not ok 9 - handleInput reports network failures
  ---
  ...
  error: 'handleInput is not defined'
# Subtest: handleInput handles an empty reply from the backend
not ok 10 - handleInput handles an empty reply from the backend
  ...
  error: 'handleInput is not defined'
...
# tests 11
# suites 0
# pass 2
# fail 9
```
What it tried next, and turns to recover:
> **Failure 1: the broken test suite.** Recovery took **7 assistant turns** from the failure (msg 9) to a green suite (msg 30).
> 1. **Find the root cause, not the symptom (msg 11, msg 14).** It ran `git show HEAD:script.js; git show --stat HEAD` to compare the working tree with the last commit, read the README, and checked for `node_modules`, `.env`, and `.gitignore`. It worked out that one deleted function, `handleInput`, caused 8 of the 9 failures, and that the 9th was a placeholder (`assert.equal(1, 2)`).
> 2. **Plan before fixing (msgs 17–24).** Plan mode was on, so it had to write the plan file and get approval first. The plan includes a rule for this exact situation: "If a test fails along the way, read the assertion diff and fix the code, not the test (except the placeholder test in step 3)."
> 3. **Fix (msg 26).** 4 Edits in one turn, across `index.html`, `script.js` (twice), and `test/script.test.js`. In msg 29: 2 more Edits to `index.js`, a Write of `.gitignore`, and the test re-run, all batched into the same turn.
> 4. **Verify (msg 30).** `# tests 11`, `# pass 11`, `# fail 0` on the first re-run.
>
> **Failure 2: the result didn't match the plan.** The plan's Verification section predicted that a real query with no `.env` "should return **500**". The smoke test (msg 36) printed `real query  -> 200 {"message":"Done",...}`. The agent didn't retry or change the test to force a 500. It reported the mismatch (msg 38): "**Didn't go as planned:** I expected `"pay judge 3 cents"` to return a 500 because there's no `.env`. It returned **200** instead. The agent SDK picked up Anthropic credentials already set in this shell, and with no `LOCUS_API_KEY` the Locus connection failed ("⚠️ MCP connection issue")… It also means the new 500 path hasn't been tested against a real failure."
>
> **How the harness reports failures.** PowerShell's `npm test 2>&1 | Select-Object -Last 60` passed through npm's exit code, so the harness set `is_error: true` and prepended `Exit code 1`. In my earlier Bash session (`session_with_failure.json`), `npm test 2>&1 | tail -60` exited with `tail`'s status, so a failing suite came back as `is_error: false`, and the model only noticed by reading `# fail 1`. The error flag depends on the shell pipeline, not on whether the tests failed.

**b. Planning**: `[OBSERVED]` · evidence: msg 1 (`role: "system"`, plan-mode instructions), msg 17 (Write to the plan file), msgs 20–21 (ToolSearch loads `ExitPlanMode`), msg 23 (`ExitPlanMode {}`), msg 24 (approval), msg 25 (exit notice); compare `session_with_failure.json`, which has no plan
> Here, planning came from **a mode (enforced by the harness and a prompt) plus a tool**, not from emergent behavior. I turned on plan mode myself, and the harness added this to the `role: "system"` message at msg 1: "Plan mode is active. The user indicated that they do not want you to execute yet -- you MUST NOT make any edits (with the exception of the plan file mentioned below), run any non-readonly tools… This supercedes any other instructions you have received." It then lays out a five-phase workflow (Initial Understanding → Design → Review → Final Plan → "Phase 5: Call ExitPlanMode"). It also prescribes the plan's structure: "Begin with a **Context** section… Include a verification section". The plan file at msg 17 follows that structure exactly (`## Context`, `## Changes`, `## Verification`). It also states: "your turn should only end with either using the AskUserQuestion tool OR calling ExitPlanMode."
>
> This separates the explanations because I ran the same kind of task without plan mode (`session_with_failure.json`, and requests 9–16 in `session.flows`). There, the agent never wrote a plan up front. It went straight from inspecting to running to editing, and only produced a numbered *after-the-fact* summary in its final message. The base system prompt and the default tool set don't create a plan for a small task. Plan mode does. Within plan mode, some behavior was still the model's own judgment: it skipped the Explore/Plan subagents the workflow recommends (see d) and asked no AskUserQuestion questions.

**c. Plans and task state**: `[OBSERVED]` for the plan file's lifecycle; `[INFERRED]` for task lists · evidence: msg 1 (plan-file path), msg 17 (Write), msg 24 (approved plan echoed back), msg 25 (exit notice); no TodoWrite or task tool in `tools[]` or in the deferred list \
How does one get created and advanced? What does the model see about task state each turn, and where does it live in the request:
> **Creation.** The harness picks the path and announces it in the plan-mode system message (msg 1): "No plan file exists yet. You should create your plan at `[REDACTED: local filepath].claude\plans\i-want-to-see-lexical-floyd.md` using the Write tool… NOTE that this is the only file you are allowed to edit". The plan lives in my home directory, not in the repo. The model creates it with an ordinary `Write` call (msg 17).
>
> **Approval.** `ExitPlanMode` takes **no parameters** (`{}` at msg 23). Its description says it "does NOT take the plan content as a parameter - it will read the plan from the file you wrote". The `tool_result` at msg 24 is "User has approved your plan. You can now start coding. Start with updating your todo list if applicable", followed by the plan path and the **full plan text** under `## Approved Plan:` (4,817 characters). The harness then adds a separate `role: "system"` message (msg 25): "## Exited Plan Mode … The plan file is located at … if you need to reference it."
>
> **Advancing.** After msg 25 the plan isn't advanced in any structured way. No message records which steps are done, and the model never edits the plan file again. Each turn, it "sees" the plan only as the approved text replayed in msg 24's `tool_result` and as its own earlier tool calls in the history. The model's own sense of progress shows up in its text, such as "Now the backend fixes and `.gitignore`." (msg 29) and "Next, the backend smoke test" (msg 32), and in its final report, which checks the results against the plan.
>
> **Task lists.** "Start with updating your todo list if applicable" points to a task-list mechanism, but no TodoWrite or task tool exists in either `tools[]` or the deferred list in this build. I infer that the message is shared with configurations that do have a task tool, and that the model correctly treated it as not applicable here.

**d. Subagents**: `[OBSERVED]` that it chose not to delegate; `[INFERRED]` for what a subagent would get and return · evidence: msg 1 (plan-mode Phase 1/2 instructions), msg 17 (the decision), the `Agent` tool schema and description in `tools[]`; no `Agent` `tool_use` appears in any of my captures
> **When it delegates (observed: it didn't).** The plan-mode instructions push toward delegation: Phase 1 says "Critical: In this phase you should only use the Explore subagent type", and Phase 2 says the agents it launches should get "comprehensive background context from Phase 1 exploration including filenames and code path traces". The model ignored that and said why in msg 17: "I have a full picture. The codebase is small, so I skipped the subagents. Writing the plan now." By that point it had already read every source file, the test file, the README, and the git diff itself in msgs 2–15. That matches the `Agent` description: "For a single-fact lookup where you already know the file, symbol, or value, search directly". It also suggests the model weighs a subagent's cost (a separate context and round trip) against the repo's size, rather than treating the instructions as mandatory.
>
> **What the subagent would be told (inferred from the schema).** Only what goes into `prompt`, plus its own agent definition. With any `subagent_type` other than `"fork"`, it "starts a fresh agent". The parent's conversation isn't passed on, which is why Phase 2 tells the model to pack "filenames and code path traces" into the prompt.
>
> **What would come back (inferred).** A final report, delivered asynchronously ("Subagents run in the background; you'll be notified when one completes"). Only the report comes back, not the subagent's tool output ("you keep the conclusion, not the file dumps"), and it isn't shown to the user ("relay what matters").

**e. Context management**: `[OBSERVED]` · evidence: requests 9–16 in `session.flows` (8 consecutive requests from one session), compared message by message; the `context_management` field in every request; the single request body in `session_with_plan_and_failure.json`
> **Earlier turns are replayed verbatim, and new turns are appended.** From request 9 to 16, `messages` grows 2 → 5 → 8 → 11 → 14 → 17 → 20 → 22. With the `cache_control` markers stripped, every earlier message is byte-identical in the next request, apart from one formatting change described below. Nothing is summarized, truncated, or dropped. Full tool results stay in the history, such as the `cat -n` dump of every source file, so the messages section grows from 22 KB to 68 KB over the session. `system` (7.0 KB) and `tools` (82.4 KB) don't change at all, so at the start of a session the tool schemas are most of the payload.
>
> **What does change: the cache breakpoint moves.** In each request, `cache_control` sits on the newest `tool_use` block and the newest message, plus 2 markers in `system`. In the next request, the older marker is removed. That message changes from array form `[{"type":"text","text":…}]` to a plain string, which is the only difference between the two copies. So the prompt prefix stays cacheable, and only the new turns are processed fresh.
>
> **Running out of room.** Each request carries `"context_management": {"edits": [{"type": "clear_thinking_20251015", "keep": "all"}]}`. That's a server-side setting that could clear old thinking blocks, but it is set to keep all of them. Earlier thinking blocks do come back in later requests (7 in the final plan-mode request, with `signature` fields; only 1 has visible text, consistent with `"thinking": {"display": "updates"}`). The harness also adds a `role: "system"` message after every tool result with the remaining budget, e.g. `<total_tokens>14959363 tokens left</total_tokens>`, which shrinks each turn (14,959,363 at msg 4 → 14,935,248 at msg 37). None of my sessions got anywhere near the limit, so I never saw compaction or summarization. I can't describe how the history looks after compaction from this trace.
>
> **State changes are appended, not edited.** When plan mode ended, the original plan-mode instructions at msg 1 were left as they were, and a new "## Exited Plan Mode" message was appended at msg 25. Likewise, loading `ExitPlanMode` changed `tools[]` but not the deferred-tool list in msg 1 (see Part III). Keeping the history append-only seems designed to protect the prompt cache.


## Part V: Reflection

**Two decisions you would copy**, and the problem each solves:
1. Many tools are deferred because loading all schemas and tool descriptions would fill the context up with irrelevant material and those should only be loaded if the tool is needed. 
2. Plan mode disables editing instead of simply telling in the prompt to not make edits which solves the problem that the model doesn't complete a structured plan before making edits. 

**One you would make differently** (engage with why it might be there):
> Old tool calls and their results are kept without compaction in my trace, even though they may not be useful for later activities such as if a file was read that was later determined to be irrelevant. I think it might be there because compaction is expected to happen across the context, not tool by tool. 

**One thing the trace changed** about how you will steer a coding agent:
This trace showed me that there are a lot more tools than I realized before so one thing I will change about steering a coding agent in the future is to leverage those tools when possible such as the google integration. 


## Submission
1. `Command (⌘) + F` for `TODO`. No results means you're done.
2. Confirm no credentials or `x-api-key` headers made it into your quoted excerpts.
3. Push all changes to your remote repository and submit via Gradescope.
4. Don't forget to remove `ANTHROPIC_BASE_URL` from your repo's `.claude/settings.json`!
