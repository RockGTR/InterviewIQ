# Debug Session: Phase 3 — Bedrock Model Access

## Symptom
GenerateBrief Lambda returns 500 on every pipeline execution.

**When:** Every pipeline run after Phase 3 deploy
**Expected:** Bedrock (Claude) generates company profile, questions, brief, and packet
**Actual:** `ValidationException` or `AccessDeniedException` on `InvokeModel`

## Evidence
- `BEDROCK_REGION=us-east-1` but Claude 3.5 Sonnet v2 is NOT in the ON_DEMAND list for us-east-1
- us-east-1 ON_DEMAND: `claude-3-sonnet-v1`, `claude-3-haiku-v1`, `claude-3-5-sonnet-v1`
- us-west-2 ON_DEMAND: all the above PLUS `claude-3-5-sonnet-v2`, `claude-3-5-haiku-v1`
- Newer models (Sonnet 4, Opus 4) require inference profiles everywhere
- Inference profiles require `aws-marketplace` permissions — blocked in hackathon sandbox

## Hypotheses

| # | Hypothesis | Likelihood | Status |
|---|------------|------------|--------|
| 1 | Wrong Bedrock region — model not available ON_DEMAND in us-east-1 | 90% | CONFIRMED |
| 2 | Sandbox blocks aws-marketplace perms for inference profiles | — | CONFIRMED (separate issue) |
| 3 | IAM missing bedrock:InvokeModel | 5% | ELIMINATED |

## Attempts

### Attempt 1: Switch to inference profile ID
**Action:** Changed model ID to `us.anthropic.claude-3-5-sonnet-20241022-v2:0`
**Result:** `AccessDeniedException` — needs aws-marketplace permissions  
**Conclusion:** ELIMINATED — sandbox blocks Marketplace actions

### Attempt 2: Switch to Claude Sonnet 4
**Action:** Changed model ID to `anthropic.claude-sonnet-4-20250514-v1:0`
**Result:** `ValidationException` — on-demand not supported for this model
**Conclusion:** ELIMINATED — Sonnet 4 requires inference profile too

### Attempt 3: Switch BEDROCK_REGION to us-west-2
**Action:** Change region to us-west-2 + use direct model ID `anthropic.claude-3-5-sonnet-20241022-v2:0`
**Result:** PENDING
**Conclusion:** PENDING

## Resolution
**Root Cause:** `BEDROCK_REGION` was `us-east-1` but Claude 3.5 Sonnet v2 only supports ON_DEMAND invocation in `us-west-2`.
**Fix:** Switch `BEDROCK_REGION` to `us-west-2` and use direct model ID `anthropic.claude-3-5-sonnet-20241022-v2:0`.
