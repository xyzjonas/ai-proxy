# ai-proxy

Single-file FastAPI service that sends one fixed OpenAI prompt (Responses API) per request and
returns JSON that is guaranteed to match a schema you define.

- `GET /` – configuration info (model, system prompt, schema)
- `POST /` – body `{"input": "..."}`; returns the model's JSON output verbatim (HTTP 502 if it doesn't validate)

Both require `Authorization: Bearer $AUTH_SECRET`. If `AUTH_SECRET` is unset, everything returns 401.

## Config (env)

| var | |
|---|---|
| `AUTH_SECRET` | shared secret |
| `OPENAI_API_KEY`, `OPENAI_MODEL` | required |
| `SYSTEM_PROMPT` | required |
| `RESPONSE_SCHEMA` / `RESPONSE_SCHEMA_FILE` | JSON Schema, inline or a mounted file path |
| `RESPONSE_SCHEMA_NAME` | optional, default `response` |
| `PORT` | optional, default `8000` |

Schema is sent with `strict: true` (OpenAI requires `additionalProperties: false` and all properties
in `required`) and re-validated locally with `jsonschema`.

## Run

```sh
docker run -p 8000:8000 -e AUTH_SECRET=... -e OPENAI_API_KEY=... -e OPENAI_MODEL=gpt-4.1-mini \
  -e SYSTEM_PROMPT="..." -v $PWD/schema.json:/schema.json -e RESPONSE_SCHEMA_FILE=/schema.json \
  scotch3840/ai-proxy
curl -H "Authorization: Bearer ..." -d '{"input":"hi"}' -H 'content-type: application/json' localhost:8000/
```

`just docker` builds and pushes `scotch3840/ai-proxy:latest`.
