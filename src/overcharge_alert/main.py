from __future__ import annotations

import logging
import sys
import time

import psutil

from overcharge_alert.config import get_active_config_path, load_config
from overcharge_alert.notifier import show_overcharge_alert

logger = logging.getLogger(__name__)


def _should_alert(
    power_plugged: bool,
    percent: int | None,
    threshold: int,
    was_over: bool,
) -> tuple[bool, bool]:
    """
    Returns (should_fire_toast, new_was_over).
    Alert only on edge: plugged in, known percent, percent >= threshold,
    and previous state was not already over.
    """
    if not power_plugged or percent is None:
        return False, False
    over = percent >= threshold
    if over and not was_over:
        return True, True
    return False, over


def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(levelname)s: %(message)s",
        stream=sys.stderr,
    )
    cfg = load_config()
    logger.info(
        "Overcharge-Alert running (threshold=%s%%, poll=%ss)",
        cfg.threshold_percent,
        cfg.poll_interval_seconds,
    )
    logger.info("Config file: %s", get_active_config_path())

    was_over = False
    while True:
        try:
            bat = psutil.sensors_battery()
            if bat is None:
                logger.warning("No battery information available; retrying later.")
                time.sleep(cfg.poll_interval_seconds)
                continue

            pct = bat.percent
            plugged = bat.power_plugged
            if pct is None:
                logger.debug("Battery percent unknown; skipping comparison.")
                time.sleep(cfg.poll_interval_seconds)
                was_over = False
                continue

            fire, was_over = _should_alert(plugged, pct, cfg.threshold_percent, was_over)
            if fire:
                try:
                    show_overcharge_alert(cfg.threshold_percent, int(pct))
                except OSError as e:
                    logger.error("Toast failed: %s", e)

            time.sleep(cfg.poll_interval_seconds)
        except KeyboardInterrupt:
            logger.info("Exiting.")
            raise SystemExit(0)


if __name__ == "__main__":
    main()
