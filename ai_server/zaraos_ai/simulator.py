from __future__ import annotations

from .service import ZaraAiService


def run_voice_to_robot_scenario(command: str = "move forward") -> dict:
    return ZaraAiService().simulate(command)
