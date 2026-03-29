from __future__ import annotations

from winotify import Notification, audio


def show_overcharge_alert(threshold_percent: int, current_percent: int) -> None:
    toast = Notification(
        app_id="Overcharge-Alert",
        title="Battery threshold reached",
        msg=(
            f"Charge is at {current_percent}% while on AC power "
            f"(threshold {threshold_percent}%). Consider unplugging."
        ),
        duration="long",
    )
    toast.set_audio(audio.Default, loop=False)
    toast.show()
