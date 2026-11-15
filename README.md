# TrustDesk

AI agent that drafts cited answers to security questionnaires and RFPs from a client's own policies, and routes anything uncertain to a human reviewer.

Stack: Python 3.12 · FastAPI · LangGraph/LangChain · Amazon Bedrock · Aurora pgvector · React · Terraform.

## Layout

| Path | Purpose |
|---|---|
| `backend/trustdesk/api/` | FastAPI service: uploads, review queue, approvals (resume the graph), exports, progress stream |
| `backend/trustdesk/worker/` | SQS consumer: runs and resumes the agent graphs, retries, dead-letter handling |
| `backend/trustdesk/agent/` | **Orchestration (LangGraph):** document graph, per-question graph, state models, checkpointing |
| `backend/trustdesk/knowledge/` | Policy ingestion, chunking, embeddings, hybrid retrieval, answer library |
| `backend/trustdesk/questionnaire/` | Readers and writers for xlsx, docx, csv, pdf questionnaires |
| `backend/trustdesk/guardrails/` | Grounding verifier, prompt-injection fence, redaction |
| `backend/trustdesk/llm/` | Bedrock clients, pinned model versions, prompts, structured output, fallback |
| `backend/trustdesk/saas/` | Tenancy, licensing, metering, vendor admin |
| `backend/trustdesk/platform_ops/` | Tracing, audit trail, notifications, shared settings |
| `backend/migrations/` | Database schema and migrations |
| `backend/tests/` | Unit, integration and tenant-isolation tests |
| `frontend/` | React reviewer and admin UI |
| `evals/` | Test pack, answer key, scorer, bake-off report |
| `infra/` | Terraform and per-environment configuration |
| `docs/` | Design notes and decisions |
| `scripts/` | Dev and ops helper scripts |
