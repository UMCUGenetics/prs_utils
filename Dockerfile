# Build the virtualenv from uv.lock so the image ships exactly the dependency set the tests ran
# against, rather than re-resolving at runtime the way `uv run --script` used to.
# The uv tag pins uv itself (pyproject requires >= 0.11.28) and the Python minor; the runtime stage
# must stay on the same Python minor and Debian release, because the venv is copied, not rebuilt.
FROM ghcr.io/astral-sh/uv:0.12.1-python3.13-trixie-slim AS builder

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy

WORKDIR /app

# Dependencies first, so this layer caches independently of source changes.
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-install-project --no-dev

# README.md is required by the build backend -- pyproject sets `readme = "README.md"`.
COPY README.md ./
COPY src ./src
# --no-editable copies the package into the venv instead of linking back to /app/src, so the
# runtime stage below only needs the venv.
RUN uv sync --frozen --no-dev --no-editable


FROM python:3.13-slim-trixie

COPY --from=builder /app/.venv /app/.venv
ENV PATH="/app/.venv/bin:$PATH"

CMD ["prs-utils", "--help"]
