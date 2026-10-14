"""Docker-based sandbox for generated code.

This module never executes generated code on the host. When Docker is unavailable
it raises ``DockerUnavailableError`` instead of falling back.
"""

import os
import shutil
import subprocess
import tarfile
import tempfile
import time
from io import BytesIO
from pathlib import Path

from utils.config import (
    SANDBOX_CPU_LIMIT,
    SANDBOX_IMAGE,
    SANDBOX_MEMORY_LIMIT,
    SANDBOX_PIDS_LIMIT,
    SANDBOX_TIMEOUT_SECONDS,
)
from observability.logging import get_logger

log = get_logger("sandbox")


class SandboxError(Exception):
    """Base sandbox error."""


class DockerUnavailableError(SandboxError):
    """Raised when Docker cannot be used."""


class SandboxTimeoutError(SandboxError):
    """Raised when execution exceeds the configured timeout."""


def docker_available() -> bool:
    """Return True only when the Docker CLI responds successfully."""
    if not shutil.which("docker"):
        return False
    try:
        result = subprocess.run(
            ["docker", "version"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        return result.returncode == 0
    except Exception:
        return False


class DockerSandbox:
    """Execute a command inside an isolated, network-disabled container."""

    def __init__(
        self,
        image=SANDBOX_IMAGE,
        timeout=SANDBOX_TIMEOUT_SECONDS,
        cpu_limit=SANDBOX_CPU_LIMIT,
        memory_limit=SANDBOX_MEMORY_LIMIT,
        pids_limit=SANDBOX_PIDS_LIMIT,
    ):
        self.image = image
        self.timeout = timeout
        self.cpu_limit = cpu_limit
        self.memory_limit = memory_limit
        self.pids_limit = pids_limit

    def execute(self, files, command, env=None, timeout=None):
        """Run *command* against *files* in an isolated container.

        ``files`` is a mapping of relative path -> content. The files are sent
        through stdin as a tar archive instead of mounting a host directory.
        """
        if not docker_available():
            raise DockerUnavailableError(
                "Docker is not available; generated code was not executed."
            )

        timeout = timeout or self.timeout
        container_name = f"buildwithcrew-sandbox-{os.getpid()}-{int(time.time())}"

        # Build a tar archive in memory.
        archive = BytesIO()
        with tarfile.open(fileobj=archive, mode="w") as tar:
            for relative, content in (files or {}).items():
                data = content.encode("utf-8")
                info = tarfile.TarInfo(name=relative)
                info.size = len(data)
                info.mode = 0o644
                tar.addfile(info, BytesIO(data))
        archive_bytes = archive.getvalue()

        shell_command = (
            "mkdir -p /workspace && cd /workspace && "
            "tar -xf - && "
            " ".join(_shell_quote(part) for part in command)
        )

        docker_args = [
            "docker",
            "run",
            "--rm",
            "-i",
            "--name",
            container_name,
            "--network",
            "none",
            "--cpus",
            str(self.cpu_limit),
            "--memory",
            str(self.memory_limit),
            "--pids-limit",
            str(self.pids_limit),
            "--read-only",
            "--tmpfs",
            "/tmp:rw,noexec,nosuid,size=64m",
            "--user",
            "1000:1000",
            self.image,
            "sh",
            "-c",
            shell_command,
        ]

        log.info("sandbox_execute_start", extra={"event_data": {"command": command}})
        started = time.time()
        try:
            result = subprocess.run(
                docker_args,
                input=archive_bytes,
                capture_output=True,
                timeout=timeout,
            )
            duration = time.time() - started
            stdout = result.stdout.decode("utf-8", errors="replace")
            stderr = result.stderr.decode("utf-8", errors="replace")
            log.info(
                "sandbox_execute_done",
                extra={
                    "event_data": {
                        "exit_code": result.returncode,
                        "duration": duration,
                        "timed_out": False,
                    }
                },
            )
            return {
                "status": "passed" if result.returncode == 0 else "failed",
                "exit_code": result.returncode,
                "stdout": stdout,
                "stderr": stderr,
                "timed_out": False,
                "duration_seconds": duration,
                "command": command,
            }
        except subprocess.TimeoutExpired:
            # Best-effort cleanup.
            try:
                subprocess.run(
                    ["docker", "kill", container_name],
                    capture_output=True,
                    timeout=5,
                )
            except Exception:
                pass
            log.warning("sandbox_execute_timeout", extra={"event_data": {"command": command}})
            return {
                "status": "timeout",
                "exit_code": None,
                "stdout": "",
                "stderr": f"Execution exceeded {timeout} seconds.",
                "timed_out": True,
                "duration_seconds": timeout,
                "command": command,
            }
        except Exception as exc:
            log.error("sandbox_execute_error", extra={"event_data": {"error": str(exc)}})
            return {
                "status": "error",
                "exit_code": None,
                "stdout": "",
                "stderr": str(exc),
                "timed_out": False,
                "duration_seconds": time.time() - started,
                "command": command,
            }


def _shell_quote(value):
    # Minimal single-quote escaping for shell fragments. Values are validated
    # by callers before reaching this point.
    return "'" + str(value).replace("'", "'\\''") + "'"
