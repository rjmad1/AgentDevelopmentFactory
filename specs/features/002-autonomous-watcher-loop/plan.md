# Implementation Plan: Autonomous Watcher Loop & Fleet Protocols

**Feature Branch:** `002-autonomous-watcher-loop`  
**Feature ID:** FEAT-002  
**Created:** 2026-11-20  
**Status:** Baselined  

---

## 1. Technical Architecture

The feature is implemented in pure Node.js scripts in `scripts/`:
* `scripts/autonomous-loop.js`: File watcher using `fs.watch` with a 300ms debounce timer.
* `scripts/bundle-critic-packet.js`: Extracts git diff, AST changes, and security surfaces into `.hermes/packets/critic_packet.json`.
* `scripts/bundle-verifier-packet.js`: Gathers test outcomes and failure traces into `.hermes/packets/verifier_packet.json`.
* `scripts/bundle-doc-packet.js`: Compiles exported API docstrings into `.hermes/packets/doc_packet.json`.
* `scripts/setup-hooks.js`: Installs git pre-commit hook running `npm run ci`.
