from __future__ import annotations

import argparse
import json
import os
from dataclasses import dataclass
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any
from urllib import error, request
from urllib.parse import urlparse


MANAGED_LABEL_PREFIXES = ("status:", "severity:", "field:")


@dataclass
class BridgeConfig:
    repo: str
    token: str
    api_base: str
    host: str
    port: int
    allowed_origins: tuple[str, ...]


class GitHubIssueClient:
    def __init__(self, config: BridgeConfig) -> None:
        self.config = config

    def _repo_url(self, path: str) -> str:
        return f"{self.config.api_base.rstrip('/')}/repos/{self.config.repo}{path}"

    def _request(self, method: str, path: str, payload: dict[str, Any] | None = None) -> dict[str, Any]:
        data = json.dumps(payload).encode("utf-8") if payload is not None else None
        req = request.Request(
            self._repo_url(path),
            data=data,
            method=method,
            headers={
                "Accept": "application/vnd.github+json",
                "Authorization": f"Bearer {self.config.token}",
                "User-Agent": "NHI-Heme-Calculator-Issue-Bridge",
                "X-GitHub-Api-Version": "2022-11-28",
                "Content-Type": "application/json",
            },
        )
        try:
            with request.urlopen(req, timeout=30) as resp:
                body = resp.read().decode("utf-8")
                return json.loads(body) if body else {}
        except error.HTTPError as exc:
            body = exc.read().decode("utf-8", errors="replace")
            try:
                detail = json.loads(body)
            except json.JSONDecodeError:
                detail = {"message": body or str(exc)}
            raise RuntimeError(detail.get("message") or str(exc)) from exc
        except error.URLError as exc:
            raise RuntimeError(str(exc.reason)) from exc

    def get_issue(self, number: int) -> dict[str, Any]:
        return self._request("GET", f"/issues/{number}")

    def create_issue(self, *, title: str, body: str, labels: list[str] | None = None) -> dict[str, Any]:
        payload: dict[str, Any] = {"title": title, "body": body}
        if labels:
            payload["labels"] = labels
        return self._request("POST", "/issues", payload)

    def update_issue(
        self,
        *,
        number: int,
        state: str | None = None,
        title: str | None = None,
        body: str | None = None,
        labels: list[str] | None = None,
    ) -> dict[str, Any]:
        payload: dict[str, Any] = {}
        if state:
            payload["state"] = state
        if title:
            payload["title"] = title
        if body:
            payload["body"] = body
        if labels is not None:
            current = self.get_issue(number)
            current_labels = [item.get("name", "") for item in current.get("labels", []) if item.get("name")]
            payload["labels"] = self._merge_labels(current_labels, labels)
        return self._request("PATCH", f"/issues/{number}", payload)

    def add_comment(self, *, number: int, body: str) -> dict[str, Any]:
        return self._request("POST", f"/issues/{number}/comments", {"body": body})

    @staticmethod
    def _merge_labels(current: list[str], desired: list[str]) -> list[str]:
        keep = [
            label
            for label in current
            if label != "drug-data" and not any(label.startswith(prefix) for prefix in MANAGED_LABEL_PREFIXES)
        ]
        merged: list[str] = []
        for label in [*keep, *desired]:
            if label and label not in merged:
                merged.append(label)
        return merged


def make_handler(client: GitHubIssueClient):
    class Handler(BaseHTTPRequestHandler):
        server_version = "NHIHemeIssueBridge/1.0"

        def log_message(self, format: str, *args: Any) -> None:
            return

        def _is_allowed_origin(self, origin: str | None) -> bool:
            if not origin:
                return False
            if origin == "null":
                return True
            parsed = urlparse(origin)
            hostname = (parsed.hostname or "").lower()
            if parsed.scheme in {"http", "https"} and hostname in {"127.0.0.1", "localhost"}:
                return True
            normalized = origin.rstrip("/")
            return normalized in client.config.allowed_origins

        def _cors_origin(self) -> str | None:
            origin = self.headers.get("Origin")
            if origin and self._is_allowed_origin(origin):
                return origin
            return None

        def _set_headers(self, status: int = 200, cors_origin: str | None = None) -> None:
            self.send_response(status)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            if cors_origin:
                self.send_header("Access-Control-Allow-Origin", cors_origin)
                self.send_header("Vary", "Origin")
                self.send_header("Access-Control-Allow-Methods", "GET, POST, PATCH, OPTIONS")
                self.send_header("Access-Control-Allow-Headers", "Content-Type")
            self.end_headers()

        def _read_json(self) -> dict[str, Any]:
            length = int(self.headers.get("Content-Length", "0"))
            raw = self.rfile.read(length).decode("utf-8") if length else "{}"
            return json.loads(raw or "{}")

        def _write_json(self, payload: dict[str, Any], status: int = 200, cors_origin: str | None = None) -> None:
            self._set_headers(status, cors_origin=cors_origin)
            self.wfile.write(json.dumps(payload, ensure_ascii=False).encode("utf-8"))

        def do_OPTIONS(self) -> None:
            cors_origin = self._cors_origin()
            if not cors_origin:
                self._write_json({"error": "Origin not allowed"}, status=403)
                return
            self._set_headers(204, cors_origin=cors_origin)

        def do_GET(self) -> None:
            cors_origin = self._cors_origin()
            if self.path == "/health":
                self._write_json(
                    {
                        "ok": True,
                        "repo": client.config.repo,
                        "api_base": client.config.api_base,
                    }
                    ,
                    cors_origin=cors_origin,
                )
                return
            self._write_json({"error": "Not found"}, status=404, cors_origin=cors_origin)

        def do_POST(self) -> None:
            try:
                cors_origin = self._cors_origin()
                if self.headers.get("Origin") and not cors_origin:
                    self._write_json({"error": "Origin not allowed"}, status=403)
                    return
                if self.path == "/issues":
                    payload = self._read_json()
                    created = client.create_issue(
                        title=payload["title"],
                        body=payload.get("body", ""),
                        labels=payload.get("labels") or [],
                    )
                    self._write_json(
                        {
                            "number": created.get("number"),
                            "state": created.get("state"),
                            "html_url": created.get("html_url"),
                            "url": created.get("url"),
                        },
                        status=201,
                        cors_origin=cors_origin,
                    )
                    return
                if self.path.startswith("/issues/") and self.path.endswith("/comments"):
                    number = int(self.path.split("/")[2])
                    payload = self._read_json()
                    created = client.add_comment(number=number, body=payload.get("body", ""))
                    self._write_json(
                        {
                            "id": created.get("id"),
                            "html_url": created.get("html_url"),
                            "url": created.get("url"),
                        },
                        status=201,
                        cors_origin=cors_origin,
                    )
                    return
                self._write_json({"error": "Not found"}, status=404, cors_origin=cors_origin)
            except Exception as exc:  # noqa: BLE001
                self._write_json({"error": str(exc)}, status=500, cors_origin=self._cors_origin())

        def do_PATCH(self) -> None:
            try:
                cors_origin = self._cors_origin()
                if self.headers.get("Origin") and not cors_origin:
                    self._write_json({"error": "Origin not allowed"}, status=403)
                    return
                if self.path.startswith("/issues/"):
                    number = int(self.path.split("/")[2])
                    payload = self._read_json()
                    updated = client.update_issue(
                        number=number,
                        state=payload.get("state"),
                        title=payload.get("title"),
                        body=payload.get("body"),
                        labels=payload.get("labels"),
                    )
                    self._write_json(
                        {
                            "number": updated.get("number"),
                            "state": updated.get("state"),
                            "html_url": updated.get("html_url"),
                            "url": updated.get("url"),
                        },
                        cors_origin=cors_origin,
                    )
                    return
                self._write_json({"error": "Not found"}, status=404, cors_origin=cors_origin)
            except Exception as exc:  # noqa: BLE001
                self._write_json({"error": str(exc)}, status=500, cors_origin=self._cors_origin())

    return Handler


def parse_args() -> BridgeConfig:
    parser = argparse.ArgumentParser(description="Local GitHub Issues bridge for the static site.")
    parser.add_argument("--repo", default=os.environ.get("GITHUB_REPO"), help="GitHub repo in owner/name format.")
    parser.add_argument("--token", default=os.environ.get("GITHUB_TOKEN"), help="GitHub token with issue write access.")
    parser.add_argument("--api-base", default=os.environ.get("GITHUB_API_BASE", "https://api.github.com"))
    parser.add_argument("--host", default=os.environ.get("ISSUE_BRIDGE_HOST", "127.0.0.1"))
    parser.add_argument("--port", type=int, default=int(os.environ.get("ISSUE_BRIDGE_PORT", "8765")))
    parser.add_argument(
        "--allowed-origins",
        default=os.environ.get("ISSUE_BRIDGE_ALLOWED_ORIGINS", ""),
        help="Comma-separated extra allowed Origins, e.g. https://your-site.example",
    )
    args = parser.parse_args()

    if not args.repo:
        raise SystemExit("Missing --repo or GITHUB_REPO")
    if not args.token:
        raise SystemExit("Missing --token or GITHUB_TOKEN")

    allowed_origins = tuple(
        origin.rstrip("/")
        for origin in (item.strip() for item in args.allowed_origins.split(","))
        if origin
    )

    return BridgeConfig(
        repo=args.repo,
        token=args.token,
        api_base=args.api_base,
        host=args.host,
        port=args.port,
        allowed_origins=allowed_origins,
    )


def main() -> int:
    config = parse_args()
    client = GitHubIssueClient(config)
    server = ThreadingHTTPServer((config.host, config.port), make_handler(client))
    print(f"GitHub issue bridge listening on http://{config.host}:{config.port} for {config.repo}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
