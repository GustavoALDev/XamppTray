import logging
import threading
from collections.abc import Callable

from xampp_tray.constants import POLL_INTERVAL
from xampp_tray.service import ServiceState, ServiceStatus, XamppService

logger = logging.getLogger(__name__)

OnChangeCallback = Callable[[ServiceStatus], None]


class StatusPoller:
    def __init__(
        self,
        service: XamppService,
        on_change: OnChangeCallback,
        interval: int = POLL_INTERVAL,
    ) -> None:
        self._service = service
        self._on_change = on_change
        self._interval = interval
        self._current = ServiceStatus(apache=ServiceState.STOPPED, mysql=ServiceState.STOPPED)
        self._lock = threading.Lock()
        self._stop_event = threading.Event()

    @property
    def current(self) -> ServiceStatus:
        with self._lock:
            return self._current

    def update(self, status: ServiceStatus) -> None:
        with self._lock:
            self._current = status

    def is_transitioning(self) -> bool:
        with self._lock:
            return self._current.apache in (ServiceState.STARTING, ServiceState.STOPPING) or \
                   self._current.mysql in (ServiceState.STARTING, ServiceState.STOPPING)

    def start(self) -> None:
        thread = threading.Thread(target=self._loop, daemon=True)
        thread.start()

    def stop(self) -> None:
        self._stop_event.set()

    def _loop(self) -> None:
        while not self._stop_event.wait(self._interval):
            if self.is_transitioning():
                continue
            try:
                output = self._service.status(silent=True)
                new_status = self._service.parse_status(output)
                with self._lock:
                    changed = (
                        new_status.apache != self._current.apache
                        or new_status.mysql != self._current.mysql
                    )
                    if changed:
                        self._current = new_status
                if changed:
                    self._on_change(new_status)
            except Exception:
                logger.exception("Erro no poll de status.")
