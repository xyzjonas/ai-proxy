"""ai-proxy: a single-endpoint HTTP wrapper around one OpenAI Responses API prompt.

Environment:
  AUTH_SECRET            optional; if set, clients must send `Authorization: Bearer <secret>`
                         (if unset, requests are NOT authenticated)
  OPENAI_API_KEY         required
  OPENAI_MODEL           required (e.g. gpt-4.1-mini)
  SYSTEM_PROMPT          required
  RESPONSE_SCHEMA        JSON schema (inline JSON) ...
  RESPONSE_SCHEMA_FILE   ... or path to a JSON schema file (e.g. a mounted file)
  RESPONSE_SCHEMA_NAME   optional, default "response"
  OPENAI_BASE_URL / OPENAI_ORG_ID / OPENAI_PROJECT_ID   optional, read by the SDK
"""

import hmac
import json
import os

from fastapi import Depends, FastAPI, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jsonschema import Draft202012Validator, ValidationError
from openai import APIError, OpenAI
from pydantic import BaseModel


def _load_schema() -> dict:
    raw = os.environ.get("RESPONSE_SCHEMA")
    path = os.environ.get("RESPONSE_SCHEMA_FILE")
    if raw:
        schema = json.loads(raw)
    elif path:
        with open(path) as f:
            schema = json.load(f)
    else:
        raise RuntimeError("Set RESPONSE_SCHEMA or RESPONSE_SCHEMA_FILE")
    Draft202012Validator.check_schema(schema)
    return schema


AUTH_SECRET = os.environ.get("AUTH_SECRET", "")
MODEL = os.environ["OPENAI_MODEL"]
SYSTEM_PROMPT = os.environ["SYSTEM_PROMPT"]
SCHEMA = _load_schema()
SCHEMA_NAME = os.environ.get("RESPONSE_SCHEMA_NAME", "response")
VALIDATOR = Draft202012Validator(SCHEMA)

client = OpenAI()  # reads OPENAI_API_KEY (+ optional base url/org/project) from env
app = FastAPI(title="ai-proxy", redoc_url=None)  # Swagger UI at /docs


bearer = HTTPBearer(auto_error=False)  # also makes Swagger show an "Authorize" button


def require_auth(creds: HTTPAuthorizationCredentials | None = Depends(bearer)) -> None:
    if not AUTH_SECRET:  # auth disabled
        return
    if creds is None or not hmac.compare_digest(creds.credentials.encode(), AUTH_SECRET.encode()):
        raise HTTPException(401, "Unauthorized", headers={"WWW-Authenticate": "Bearer"})


class Query(BaseModel):
    input: str


@app.get("/", dependencies=[Depends(require_auth)])
def info() -> dict:
    return {
        "model": MODEL,
        "system_prompt": SYSTEM_PROMPT,
        "schema_name": SCHEMA_NAME,
        "response_schema": SCHEMA,
    }


@app.post("/", dependencies=[Depends(require_auth)])
def run(query: Query):
    try:
        response = client.responses.create(
            model=MODEL,
            instructions=SYSTEM_PROMPT,
            input=query.input,
            store=False,
            text={
                "format": {
                    "type": "json_schema",
                    "name": SCHEMA_NAME,
                    "schema": SCHEMA,
                    "strict": True,
                }
            },
        )
    except APIError as e:
        raise HTTPException(502, f"OpenAI error: {e.message}")

    if response.status != "completed":
        raise HTTPException(502, f"OpenAI response {response.status}: {response.incomplete_details or response.error}")
    try:
        result = json.loads(response.output_text)
        VALIDATOR.validate(result)
    except (json.JSONDecodeError, ValidationError) as e:
        raise HTTPException(502, f"Model output does not match schema: {e}")
    return result


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", "8000")))
