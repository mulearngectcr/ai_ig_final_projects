from contextlib import asynccontextmanager
from typing import List
from fastapi import FastAPI, File, HTTPException, Request, UploadFile
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, RedirectResponse
from slowapi import Limiter
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from app import agent, rag
from app.schemas import (
    AgentRequest,
    AgentResponse,
    DocumentListResponse,
    ErrorResponse,
    SourceItem,
    ToolTraceItem,
    UploadResponse,
)

MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB
ALLOWED_EXTENSIONS = {".txt", ".md", ".pdf"}


def get_forwarded_or_client_ip(request: Request) -> str:
    """Extract first IP from X-Forwarded-For header, falling back to direct client host."""
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "127.0.0.1"


limiter = Limiter(key_func=get_forwarded_or_client_ip)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup ingestion of ./data if collection is empty
    rag.startup_ingest_data_folder()
    yield


app = FastAPI(
    title="CampusPrep AI",
    description="Placement and study prep assistant backend with RAG and multi-tool agent.",
    version="1.0.0",
    lifespan=lifespan,
)

app.state.limiter = limiter

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Exception handlers
@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(
        status_code=429,
        content={"detail": f"Rate limit exceeded: {exc.detail}", "error_type": "rate_limit_exceeded"},
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail, "error_type": "http_error"},
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={"detail": str(exc.errors()), "error_type": "validation_error"},
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    # Never expose raw stack traces to clients
    return JSONResponse(
        status_code=500,
        content={"detail": "An internal server error occurred.", "error_type": "internal_error"},
    )


@app.get("/", include_in_schema=False)
async def root():
    return RedirectResponse(url="/docs", status_code=307)


@app.get("/health", response_model=dict)
async def health_check():
    return {"status": "ok", "app": "CampusPrep AI"}


@app.get("/documents", response_model=DocumentListResponse)
async def list_documents():
    docs = rag.list_documents()
    return DocumentListResponse(documents=docs, total_count=len(docs))


@app.get("/logs", response_model=dict)
async def get_logs():
    logs = agent.get_recent_logs(limit=20)
    return {"logs": logs, "count": len(logs)}


@app.post("/upload", response_model=UploadResponse)
@limiter.limit("5/minute")
async def upload_files(request: Request, files: List[UploadFile] = File(...)):
    if not files:
        raise HTTPException(status_code=400, detail="No files provided.")

    uploaded_names: List[str] = []
    total_chunks = 0

    for file in files:
        filename = file.filename or "unknown"
        ext = "." + filename.split(".")[-1].lower() if "." in filename else ""

        if ext not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid file type for '{filename}'. Only .txt, .md, and .pdf files are supported.",
            )

        content = await file.read()
        if len(content) > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=413,
                detail=f"File '{filename}' exceeds maximum allowed size of 5 MB.",
            )

        try:
            chunks = rag.ingest_file(filename, content)
            uploaded_names.append(filename)
            total_chunks += chunks
        except Exception as e:
            raise HTTPException(
                status_code=400,
                detail=f"Failed to process '{filename}': {str(e)}",
            )

    return UploadResponse(
        uploaded=uploaded_names,
        chunk_count=total_chunks,
        message=f"Successfully ingested {len(uploaded_names)} document(s) with {total_chunks} chunk(s).",
    )


@app.post("/agent", response_model=AgentResponse)
@limiter.limit("10/minute")
async def chat_agent(request: Request, payload: AgentRequest):
    try:
        result = agent.run_agent(payload.message, payload.history)
        sources = [SourceItem(**s) for s in result.get("sources", [])]
        tool_trace = [ToolTraceItem(**t) for t in result.get("tool_trace", [])]
        return AgentResponse(
            answer=result.get("answer", ""),
            sources=sources,
            tool_trace=tool_trace,
        )
    except ValueError as ve:
        raise HTTPException(status_code=500, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agent execution encountered an error: {str(e)}")
