import logging
import subprocess
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class ServiceState(str, Enum):
    RUNNING = "running"
    STOPPED = "stopped"
    STARTING = "starting"
    STOPPING = "stopping"


@dataclass
class ServiceStatus:
    apache: ServiceState
    mysql: ServiceState


class XamppService:
    def __init__(self, lampp_path: str = "/opt/lampp/lampp") -> None:
        self._lampp = lampp_path

    def start(self) -> str:
        return self._run_privileged("start")

    def stop(self) -> str:
        return self._run_privileged("stop")

    def restart(self) -> str:
        return self._run_privileged("restart")

    def start_apache(self) -> str:
        return self._run_privileged("startapache")

    def start_mysql(self) -> str:
        return self._run_privileged("startmysql")

    def status(self, silent: bool = False) -> str:
        return self._run_privileged("status", non_interactive=True, silent=silent)

    def parse_status(self, output: str) -> ServiceStatus:
        lower = output.lower()
        return ServiceStatus(
            apache=ServiceState.RUNNING if "apache is running" in lower else ServiceState.STOPPED,
            mysql=ServiceState.RUNNING if "mysql is running" in lower else ServiceState.STOPPED,
        )

    def _run_privileged(
        self,
        action: str,
        non_interactive: bool = False,
        silent: bool = False,
    ) -> str:
        if non_interactive:
            cmd = ["/usr/bin/sudo", "-n", self._lampp, action]
        else:
            cmd = ["/usr/bin/sudo", self._lampp, action]

        result = self._exec(cmd, silent=silent)

        if result.returncode != 0 and not non_interactive and not silent:
            logger.info("sudo falhou (code %d), tentando pkexec...", result.returncode)
            pk_cmd = ["/usr/bin/pkexec", self._lampp, action]
            result = self._exec(pk_cmd, silent=silent)

        return result.stdout or result.stderr

    def _exec(
        self,
        cmd: list[str],
        silent: bool = False,
    ) -> subprocess.CompletedProcess[str]:
        try:
            result = subprocess.run(cmd, capture_output=True, text=True)
            if not silent:
                logger.info("Executando: %s (Exit Code: %d)", " ".join(cmd), result.returncode)
                if result.stderr:
                    logger.warning("stderr: %s", result.stderr.strip())
            return result
        except Exception as exc:
            logger.error("Falha ao executar %s: %s", " ".join(cmd), exc)
            return subprocess.CompletedProcess(cmd, returncode=1, stdout="", stderr=str(exc))
