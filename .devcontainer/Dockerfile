FROM python:3.12-bookworm

COPY --from=ghcr.io/astral-sh/uv:0.7.14 /uv /bin/uv

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy
