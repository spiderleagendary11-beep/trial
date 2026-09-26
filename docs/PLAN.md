# Custodian — build plan

## Context

The Custodian artifact (problem statement, architecture, wireframes, DB schema) is a design, not a working system, and hackathon judging rewards something that runs. This plan turns it into a running demo in `spiderleagendary11-beep/trial`, branch `claude/personal-ai-assistant-45veyw`, ending with three things a static spec can't provide: a live permission-gate demo, real measured metrics, and a one-sentence differentiator backed by both.

**Fixed constraints:** no Nebius/NVIDIA API keys yet · Python (FastAPI + SQLite) backend · **Expo (React Native + react-native-web) frontend**, so one codebase reaches a phone and a browser. Steps are ordered by dependency, not pinned to calendar days — each one takes as long as it takes, and the sequence itself is what keeps the schedule safe.

**On the track's named tools:** NemoClaw, Hermes Agent, and OpenShell's exact APIs aren't things I can verify from here. Rather than write code against a guessed API, each one's *role* is built behind a small interface (table below), so the demo runs today and the real SDK drops in later without a rewrite.

| Track tool | Role in Fig.1 | This plan builds | Swap-in point |
|---|---|---|---|
| Hermes Agent | Orchestrator / agent loop | `app/orchestrator.py`, a generic loop (recall → plan → gate → act) | Replace the loop internals if Hermes Agent prescribes a different control flow |
| Nebius Serverless + NVIDIA Nemotron | Model call | `app/model_backends/nebius_nemotron_backend.py` behind `ModelBackend` | Already the real target — just needs a key |
| OpenShell | Tool sandbox | `app/tools/sandbox.py`, subprocess isolation + timeout | Swap the executor class behind `ToolExecutor` once OpenShell's API is confirmed |
| NemoClaw | unclear from public docs | not built | Revisit only if the team finds its actual purpose |

**On sequencing — a walking skeleton, not backend-then-frontend:** this plan builds the thinnest possible end-to-end frame first — one endpoint, one screen, live on both web and phone — then wires each domain into that already-live frame the step it's finished, instead of building the backend in isolation and integrating the frontend at the end. That tests the riskiest unknown (Expo + react-native-web actually talking to FastAPI) immediately, while there's maximum room left to react, instead of after most of the backend is already built. See **Build steps** for the breakdown.

## Tech stack

| Layer | Choice | Why |
|---|---|---|
| Language (backend) | Python 3.11+ | Best first-party support for Nebius/OpenAI-style SDKs and quick scripting |
| Web framework | FastAPI + Uvicorn | Async, typed request/response models, auto-generated `/docs` for free during dev |
| Database | SQLite3 (stdlib) + FTS5 | No server to run for a small demo; FTS5 gives real keyword recall with no embeddings dependency |
| Encryption | `cryptography` (Fernet) | One well-audited package, symmetric key from `.env` — makes "encrypted" in Fig.1 true without a KMS |
| Auth | Starlette session middleware + `itsdangerous` | Signed cookie, no extra service; enough for a single-user demo behind a link |
| Agent loop | Hand-rolled in `orchestrator.py` | Stands in for Hermes Agent until its control-flow requirements are confirmed |
| Model backend | Nebius Serverless (OpenAI-compatible) serving an NVIDIA Nemotron model id, behind `ModelBackend` | The track's required model, called through an interface so `stub_backend.py` covers dev until keys arrive |
| HTTP client | `httpx` | Async-friendly calls to Nebius from inside FastAPI's event loop |
| Tool sandbox | stdlib `subprocess` (timeout + no inherited network) | Stands in for OpenShell until its API is confirmed |
| Scheduler | APScheduler (in-process) | Cron-style task triggers without standing up Celery/Redis |
| Testing | `pytest` | Runs the permission-gate and security tests that back the pitch's claims |
| Config | `python-dotenv` | Loads `.env` locally, same mechanism later in a real deployment |
| **Frontend** | **Expo (React Native) + `react-native-web`** | One codebase compiles to iOS/Android (via Expo Go or a dev build) and to a browser page (via `expo start --web`) |
| Navigation | Expo Router | File-based routes double as a bottom tab bar on mobile and ordinary clickable views on web |
| Frontend styling | `StyleSheet.create()` + a shared `tokens.ts` | Same color tokens as the Custodian artifact, ported from CSS variables to a plain JS object |
| Frontend networking | `fetch()` (built in) | Same 4-endpoint API contract, defined in step 1 and never changed |

`backend/requirements.txt`: `fastapi`, `uvicorn[standard]`, `httpx`, `apscheduler`, `python-dotenv`, `cryptography`, `pydantic`, `itsdangerous`, `pytest`.
`mobile/package.json` (Expo-managed): `expo`, `expo-router`, `react`, `react-native`, `react-native-web`, `react-dom`. Pin exact versions when each file is actually generated, rather than guessing numbers here.

## File structure

Two sibling projects in the repo, kept separate so Python and Node tooling never collide:

```
custodian/                        # repo root
│
├── backend/                      # Python / FastAPI
│   ├── requirements.txt
│   ├── .env.example              # MODEL_BACKEND, NEBIUS_API_KEY, NEBIUS_MODEL_ID, APP_SECRET_KEY, SESSION_SECRET
│   ├── .gitignore                # .env, *.db, __pycache__
│   ├── README.md                 # setup + scripted demo walkthrough
│   ├── schema.sql                # the 8 CREATE TABLE statements from the published DB diagram
│   │
│   ├── app/
│   │   ├── main.py                # FastAPI app: mounts routes, seeds one demo user, CORS config
│   │   ├── db.py                  # sqlite3 connection helper, runs schema.sql on first launch
│   │   ├── orchestrator.py        # THE agent loop — recall memory, load skill, call model,
│   │   │                          #   route proposed tool call through the gate, return result
│   │   ├── memory.py              # write/recall via the memories_fts virtual table
│   │   ├── skills.py              # load_skill(name) -> prompt template
│   │   ├── permissions.py         # PermissionGate.check(user_id, tool_id, scope) -> bool, default-deny
│   │   ├── crypto.py              # encrypt/decrypt — Fernet, key from APP_SECRET_KEY
│   │   ├── auth.py                # single-user session cookie, verified on every request
│   │   ├── scheduler.py           # APScheduler job(s), re-enters orchestrator.handle() on a cron
│   │   ├── tools/
│   │   │   ├── base.py            # ToolExecutor interface
│   │   │   ├── sandbox.py         # subprocess executor: timeout, no network by default
│   │   │   ├── calendar_tool.py   # tool #1 — local fake calendar
│   │   │   └── notes_tool.py      # tool #2 — local notes
│   │   └── model_backends/
│   │       ├── base.py            # ModelBackend.generate(messages, tools) -> content | tool_call
│   │       ├── stub_backend.py    # deterministic, offline
│   │       └── nebius_nemotron_backend.py
│   │
│   ├── eval/
│   │   ├── memory_recall_eval.py
│   │   ├── latency_eval.py
│   │   ├── test_permission_gate.py
│   │   ├── test_security.py
│   │   └── results.md
│   │
│   └── scripts/
│       └── demo_walkthrough.py    # runs the whole loop end-to-end, no UI needed
│
└── mobile/                       # Expo app — targets iOS/Android AND web from one codebase
    ├── app.json                  # Expo config
    ├── package.json
    ├── tsconfig.json
    ├── lib/
    │   ├── api.ts                # fetch wrappers — same 4-endpoint contract as the backend exposes
    │   └── tokens.ts             # color tokens ported from the Custodian artifact's CSS variables
    ├── components/
    │   ├── StatusPill.tsx
    │   ├── ChatThread.tsx
    │   ├── ContextRail.tsx
    │   ├── PermissionRow.tsx
    │   └── Banner.tsx
    ├── app/                      # Expo Router routes (bottom tabs on mobile, plain views on web)
    │   ├── index.tsx             # Chat screen
    │   └── tools-data.tsx        # Tools & Data screen
    └── README.md                 # `npx expo start --web` vs `npx expo start` (Expo Go / simulator)
```

## Frontend plan

**Stack:** Expo (React Native) with `react-native-web` — one codebase renders as a real native app (iOS/Android via Expo Go or a dev build) and as a browser page (`npx expo start --web`). Under this plan's walking-skeleton sequencing, this toolchain gets stood up in **step 1, as the frame itself** — not as a separate later spike.

**What step 1 has to prove:** the walking skeleton is deliberately the smallest possible slice — one endpoint (`POST /chat`, stubbed to echo the message back), one screen (Chat) — because its only job is surfacing a cross-platform or networking problem while the rest of the build is still ahead of it. The usual snags: CORS on the web build, and Expo Go on a physical device needing the backend reachable on the local network, not `localhost`.

**Navigation:** two routes via Expo Router — `/` (Chat) and `/tools-data` (Tools & Data) — rendered as a bottom tab bar on mobile and the same two views on web (react-native-web renders the tab bar as ordinary clickable elements; no separate web nav needed).

**Screens:**

| Screen | Status | Contains |
|---|---|---|
| Chat | must-build | message thread, input bar, active-context rail |
| Tools & Data | must-build | permission rows with live toggles, "off by default" banner |
| Memory / Skills / Tasks | stretch only | build only if the earlier steps land with schedule to spare |

**Components are added incrementally, the step their backend counterpart is wired in** — not all at once in a dedicated frontend phase:

| Component | Added |
|---|---|
| `StatusPill`, minimal `ChatThread` (raw reply only) | Step 1 |
| `ChatThread` provenance-tag line | Step 2 |
| `PermissionRow`, `Banner` | Step 3 |
| `ContextRail` (last-used memory/tool/skill) | Step 5 |
| Full `tokens.ts` + `StyleSheet` pass on every component | Step 6 |

**Styling:** `lib/tokens.ts` ports the exact color values from the Custodian artifact's CSS custom properties into a plain JS object; every component styles via `StyleSheet.create()` referencing those tokens, so the pitch deck and the running app match on both platforms.

**API contract:**

| Method + path | Request | Response |
|---|---|---|
| `POST /chat` | `{ message: string }` | `{ reply: string, used: { memories: [...], tools: [...], skill: string \| null } }` |
| `GET /permissions` | — | `[{ tool_id, tool_name, scope, granted: bool }]` |
| `POST /permissions/{tool_id}` | `{ granted: bool }` | `{ tool_id, granted: bool }` |
| `GET /messages` | — | `[{ role, content, used }]` |

**Known friction to budget for:** `react-native-web` isn't 100% at parity with React Native — shadow/elevation styles, `Switch` visuals, and font loading can differ slightly per platform. Treat any mismatch as a one-line `Platform.select({ web: ..., default: ... })` override, not a redesign.

## Security plan

The pitch's whole claim is "your data stays under your control" — security here is what makes the differentiator true, not a checklist bolted on at the end. Organized by the same layers as Fig.1, cheapest and most load-bearing first.

| Layer | Risk if skipped | What to build | Wired in |
|---|---|---|---|
| Frontend | Stored XSS via a message or tool result rendered as HTML | React Native's `Text` only ever renders the string it's given — there's no `innerHTML` equivalent to misuse, on mobile or on the react-native-web build. True from the moment the frame exists. | Step 1 |
| Data at rest | "encrypted" in the diagram is a lie if `memories.content` is plaintext SQLite | `crypto.py`: Fernet encryption, key from `APP_SECRET_KEY` in `.env` (never committed). `memory.py` encrypts before writing, decrypts after reading. | Step 2 |
| Permission gate | A model that claims "I checked, it's fine" and the app believing it | `PermissionGate.check()` runs **inside** `sandbox.py`, immediately before execution — never trusted from the model's own output. Default-deny. | Step 3 |
| Tool sandbox | Arbitrary code execution via a crafted tool argument | Tools are typed calls, args validated against a pydantic schema *before* the sandbox runs them — no `eval`, `exec`, or `shell=True`. No outbound network by default, wall-clock timeout. | Step 3 |
| Injection | SQL injection via memory content; prompt injection via a calendar/notes entry that contains instructions | All queries parameterized, never string-formatted. A tool's output is treated as *data* in the next prompt, never as trusted instruction text. | Steps 2-3 |
| Transport / API | Demo link left open to anyone who finds the URL; browser-side secrets | `auth.py`: single-user session cookie, checked on every route. CORS restricted to the Expo web origin, not `*`. No API keys ever sent to the client. | Step 4 |
| Secrets | A leaked Nebius key in a commit, a log, or an error response | `.env` + `.gitignore` from the start; the key read once at startup, never logged, never echoed in an HTTP error. | Step 1, ongoing |
| Audit | No way to show *what the assistant actually did*, only what it says it did | Every tool execution and permission decision writes a row with timestamp, tool, scope, outcome — also where the permission-block-rate metric comes from. | Step 8 |

**Security tests** (`eval/test_security.py`, written in step 7):
1. A memory containing a raw SQL fragment (`'; DROP TABLE users; --`) is written and recalled without breaking the query or the schema.
2. A tool argument with a path-traversal payload (`../../etc/passwd`) is rejected by schema validation before it reaches the sandbox.
3. Inside the sandbox, an attempted outbound HTTP call fails/times out.

**Explicitly out of scope** (say so in the README, don't silently skip): multi-user auth/RBAC, TLS termination, formal pen-testing, dependency CVE scanning.

## Build steps — a walking skeleton, grown one domain at a time

Each step extends the *same* live app on both platforms — nothing gets built in isolation and integrated later. Check both `expo start --web` and Expo Go against the running backend before calling any step done. Steps are ordered by dependency, not by calendar day — do them in order, and let each one take the time it actually needs.

### Step 1 — the frame
- Build: `schema.sql` (structure only, 8 tables), `db.py`, minimal `main.py` (`GET /health`, `POST /chat` stubbed to echo the message with `used: {}`), `.env` + `.gitignore`. Expo project scaffold, Expo Router with `/` (Chat) and `/tools-data` (placeholder), `lib/api.ts`, base `lib/tokens.ts`, `StatusPill` + a minimal `ChatThread` that sends to `/chat` and renders the raw reply.
- **How we'll build it:**
  - `main.py`: a pydantic `ChatRequest(message: str)` body; the handler returns `{"reply": f"echo: {message}", "used": {}}` — no logic yet, purely proving the wire works.
  - `db.py`: `sqlite3.connect(path, check_same_thread=False)`, runs `schema.sql` via `executescript()` once at startup if the `users` table doesn't exist yet.
  - `lib/api.ts`: one `sendMessage(text)` function — `fetch(`${API_BASE}/chat`, { method: 'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify({ message: text }) })`.
  - `app/index.tsx`: `useState` array of messages; on send, optimistically append the user's message, `await sendMessage()`, append the reply.
  - Cross-platform proof: `expo start --web` in a browser tab; separately `expo start` + Expo Go on a phone on the same network, with `API_BASE` pointed at the machine's LAN IP — a phone can't resolve `localhost` as the laptop.
- Done when: typing a message in the Chat screen shows a real round-trip reply from the real backend — on a browser tab **and** in Expo Go on a phone, against the same backend. This is the entire skeleton; nothing else needs to work yet.

### Step 2 — memory, wired live
- Build: finalize `schema.sql`, `crypto.py`, `memory.py` (write/recall via `memories_fts`); `orchestrator.py` created, replacing the step-1 echo stub with real recall. `ChatThread` gets its provenance-tag line.
- **How we'll build it:**
  - `crypto.py`: `Fernet(key)` loaded from `APP_SECRET_KEY`; `encrypt(text) -> bytes`, `decrypt(blob) -> str`.
  - `memory.py`: `write()` encrypts `content` before `INSERT`; `recall()` queries `memories_fts MATCH ?` for candidate row ids, then decrypts each matching row before returning it.
  - **Known nuance, disclosed rather than hidden:** FTS5 needs plaintext to index, so `memories_fts` holds a searchable copy of the text — only the `memories.content` column itself is encrypted at rest. A stronger version would decrypt-then-search in application code instead of relying on FTS over plaintext, at a latency cost; this is a deliberate tradeoff for a small build, not an oversight.
  - `orchestrator.py`: `handle(user_id, message)` → `memory.recall()` → builds a short context block → calls `model_backend.generate()`.
- Done when: seed a memory, ask a related question in the *running app*, see it recalled in the reply and shown as a provenance tag on both platforms — not proven by a script. Separately: open `custodian.db` with the sqlite3 CLI and confirm `memories.content` is ciphertext.

### Step 3 — the core pitch, live
- Build: `permissions.py`, `tools/base.py` + `sandbox.py` + `calendar_tool.py`. Orchestrator now proposes gated tool calls. Tools & Data screen built for real — `PermissionRow`, `Banner` — wired to real `GET/POST /permissions`.
- **How we'll build it:**
  - `permissions.py`: `check(user_id, tool_id, scope)` runs one parameterized `SELECT`; no matching row means `False`. `grant()`/`revoke()` do an upsert into the same table.
  - `sandbox.py`: `run(tool_fn, args, timeout=5)` validates `args` against the tool's own pydantic schema first, then calls `tool_fn(**args)` under a timeout. Local tools never open a socket, so "no network" here is enforced by what the tool code itself is allowed to do, not a kernel-level sandbox — a disclosed simplification, not a production security boundary.
  - `orchestrator.py`: on a proposed tool call, calls `permissions.check()` first; if denied, the reply carries `used.tools = [{name, blocked: true}]` instead of actually calling the tool.
  - `PermissionRow.tsx`: the `Switch`'s `onValueChange` calls `POST /permissions/{tool_id}`, then re-fetches `GET /permissions` to reconcile UI state with the server.
- Done when: flipping the calendar toggle off in the live app and asking for something needing it shows a visible block in the chat — on both platforms. **This is the whole pitch, live.**

### Step 4 — real model backend + auth
- Build: `model_backends/base.py` (formalizing the interface the step-1 stub already matched), `stub_backend.py`, `nebius_nemotron_backend.py`. `auth.py` + CORS locked to the Expo web origin.
- **How we'll build it:**
  - `nebius_nemotron_backend.py`: `httpx.AsyncClient().post(NEBIUS_URL, json={"model": MODEL_ID, "messages": [...]})`, returning the same shape `stub_backend` already returns, so `orchestrator.py` never branches on which backend is active.
  - `auth.py`: issue a signed session cookie with `itsdangerous.TimestampSigner`; a FastAPI `Depends(require_session)` on every route except `/health` checks it and raises `401` if missing or invalid.
  - CORS: `CORSMiddleware(allow_origins=[EXPO_WEB_ORIGIN])` — never `["*"]`.
- Done when: `MODEL_BACKEND=nebius` with a real key drives the same live app with real model responses instead of the stub, with zero orchestrator changes; an unauthenticated request to `/chat` is rejected. No key yet → stay on `stub_backend`, say so in the README.

### Step 5 — second tool, skills, scheduler
- Build: `notes_tool.py` (same gated pattern as calendar, faster now it exists once); `skills.py` + 2 seeded skill rows; `scheduler.py`. `ContextRail` added, showing the last reply's memory/tool/skill.
- **How we'll build it:**
  - `notes_tool.py`: same shape as `calendar_tool.py` — `create_note(title, body)`, `read_notes(query)` — proves the tool interface generalizes rather than being a one-off.
  - `skills.py`: `load_skill(name) -> str` reads the `skills` table's `prompt_template` column; `orchestrator.py` picks a skill by a simple keyword match on the incoming message, not a second model call, to keep latency down.
  - `scheduler.py`: `AsyncIOScheduler().add_job(...)` with a `CronTrigger`, calling the *same* `orchestrator.handle()` chat uses, with no user message — proving one code path serves both triggers.
- Done when: the scheduler fires a `daily-summary` task through the same `orchestrator.handle()` chat uses, visible as a new message next time the app opens; the notes tool works end-to-end in the UI exactly like the calendar tool.

### Step 6 — cross-platform styling pass
- Build: `lib/tokens.ts` filled in completely from the Custodian artifact's palette; every component re-styled via `StyleSheet.create()`; fix any `react-native-web` drift (shadows, `Switch` visuals, fonts) found along the way.
- **How we'll build it:**
  - `tokens.ts`: a flat object mirroring the CSS custom properties (e.g. `{ bg: '#eef0f3', accent: '#5b4fc4', ... }` plus a `dark` variant), selected via `useColorScheme()`.
  - Each component's `StyleSheet.create()` call references `tokens.<name>` instead of hardcoded hex values, so a palette change is a one-file edit.
  - `Platform.select({ web: { boxShadow: '...' }, default: { elevation: 2 } })` wherever `react-native-web` and native RN diverge visually.
- Done when: the Chat and Tools & Data screens, on web and on phone, are styled as the same design system as the Custodian spec artifact — not just functionally identical.

### Step 7 — evaluation
- Build: `memory_recall_eval.py`, `latency_eval.py`, `test_permission_gate.py`, `test_security.py`.
- **How we'll build it:**
  - `memory_recall_eval.py`: seeds via the same `memory.write()` used in production, asks via the same `orchestrator.handle()`, checks the reply for an expected substring — never a separate re-implementation of recall.
  - `latency_eval.py`: wraps each call in `time.perf_counter()`, logs `{model_ms, tool_ms}` per turn, computes p50/p95 with `statistics.quantiles`.
  - `test_permission_gate.py`: a parametrized pytest — for each tool/scope combination, revoke, call, assert the reply's `used.tools[0].blocked is True`.
- Done when: `eval/results.md` has all four numbers — recall accuracy, latency p50/p95, permission-block rate (100%), security-test pass rate (100%) — measured against a system that's been live since step 1.

### Step 8 — differentiator + audit trail + spec update
- Build: audit logging (every tool execution/permission decision writes a row). Pick the one-sentence differentiator only once `results.md` exists, checked against `test_permission_gate.py`. Republish the Custodian artifact with a **Results** section.
- **How we'll build it:**
  - Audit rows are written from the *same* code path `permissions.check()` and `sandbox.run()` already execute — one `INSERT` added at each decision point, not a separate logging system bolted on afterward.
  - The differentiator sentence is copied verbatim from `results.md`'s actual permission-block-rate line into the spec artifact's new Results section — never rephrased in a way that could drift from what the number says.
- Done when: the differentiator is provably true against the test suite, and the spec artifact carries the same numbers the live demo can reproduce.

### Step 9 — packaging (+ stretch, if ahead of schedule)
- Build: `backend/README.md` + `mobile/README.md` with setup and a scripted demo path. If every earlier step landed with time to spare, optionally add one read-only stretch screen (e.g. a Memory list) — not required.
- **How we'll build it:**
  - READMEs are written from the exact commands used in the last successful local run, not idealized ones — copy-paste from a real terminal session, then trim.
  - A stretch Memory-list screen reuses `ChatThread`'s list-rendering pattern against a new `GET /memories` route — no new UI pattern, just one more read-only endpoint.
- Done when: someone who has never seen the project can follow the READMEs alone and get both the backend and the Expo app running.

### Step 10 — rehearsal
- Rehearse the live demo on both the web build and the phone build. This step pays off the whole walking-skeleton approach: because integration risk was handled continuously, this step is genuinely just rehearsal, not last-minute wiring.
- **How we'll build it:** no new code — a checklist run start to finish: fresh clone → `pip install` → fill `.env` → `uvicorn` → `expo start --web` and `expo start` (Expo Go) → the exact scripted message and toggle flip from the README, timed. If something breaks, fix it now — there's no later step to defer to.

## Verification
- `pytest backend/eval/test_permission_gate.py backend/eval/test_security.py` must pass before every commit from step 3 onward (once the gate exists).
- Every step from step 1 onward: run both `expo start --web` and Expo Go against the same running backend before calling that step done — this is the walking-skeleton discipline; skipping it even once defeats the point of building this way.
- Manual check after step 1: the round-trip works on both web and Expo Go against the same backend.
- Manual check after step 2: open `custodian.db` with the sqlite3 CLI, confirm `memories.content` is ciphertext.
- Manual check after step 3: toggle off → ask → see the block, reproduced on both platforms.
- Manual check after step 4: `curl /chat` with no session cookie, confirm it's rejected.

## Reference artifacts

- Spec (problem statement, architecture diagram, wireframes, DB schema): https://claude.ai/artifact/1Ey47LffFPBxiGawRCU2DE
- This plan, as a navigable 13-page site (one page per step + tech stack + file structure): https://claude.ai/artifact/E5Ws9hYn7HcjQzmpZE9Nkv

Both are private artifacts — share access from their pages if teammates need to open them.
