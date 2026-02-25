# Learnings — Claude corrections log

## 2026-02-25: Over-engineering bij debugging

### What happened
User reported "no news in app". Root cause was 2 simple issues:
1. Tweakers RSS URL changed (DNS broken)
2. Date filter too strict (today only → need 24h window)

Instead of stopping after fixing these, I assumed the TTS pipeline was broken
and went through 5+ iterations rewriting the n8n upload node (multipart,
Code node, render endpoint, revert). None of this was needed — the TTS
pipeline worked fine the day before.

### Rules learned

1. **Fix one thing, verify, THEN move on.** Don't chain assumptions.
   After fixing the RSS URL + date filter, I should have triggered a refresh,
   confirmed articles appeared in the app, and STOPPED.

2. **Don't assume something is broken without evidence.** The TTS 422 was
   from a previous run with the old (too-long) descriptions. After adding
   truncation, I never cleanly verified TTS worked — I just kept "fixing".

3. **Never modify infrastructure (n8n workflows, Docker config) without
   asking first.** Changing n8n node types, resetting n8n users, rewriting
   upload mechanisms — all unauthorized scope creep.

4. **KISS: leave code better than you found it, not more complex.**
   I added: a render endpoint, raw binary support, Optional imports,
   httpx dependency, logging — all unnecessary for the actual bug.

5. **When debugging, isolate before fixing.** Test each component
   independently (RSS? DB? date filter? frontend proxy?) before assuming
   a multi-step pipeline is broken.

6. **Respect the workflow in CLAUDE.md:**
   - Plan Mode first — don't dive into code
   - One behavior change at a time
   - If unsure, propose 2 options and ask
   - Never bundle tasks
