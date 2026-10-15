"""Projektpfade für die mit ``uv sync`` installierte Arbeitskopie."""

from pathlib import Path


def projektwurzel() -> Path:
    """Liefert die Projektwurzel unabhängig vom Notebook-Startverzeichnis.

    ``uv sync --locked`` installiert das Paket editierbar aus ``src/``.
    Deshalb gehört dieser Pfad zur gewählten Projektumgebung und wird nicht
    aus einem persönlichen Benutzerpfad oder dem Arbeitsverzeichnis abgeleitet.
    """
    wurzel = Path(__file__).resolve().parents[2]
    if not (wurzel / "pyproject.toml").is_file() or not (wurzel / "app.py").is_file():
        raise FileNotFoundError(
            "Die LearnerCue-Projektdateien fehlen neben dem installierten Paket. "
            "Führe im Projektordner 'uv sync --locked' aus und wähle im "
            "Notebook die Python-Umgebung dieses Projekts (.venv)."
        )
    return wurzel
