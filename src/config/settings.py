import configparser
import sys
from pathlib import Path

DEFAULT_INI = """\
[llm]
model = gpt-5-mini

[paths]
output_dir = .

[files]
cover_letter_out = Template_cover_letter.docx
resume_out = Template_resume.docx
"""


class AppSettings:
    def __init__(self):
        # Determine the base project directory
        if getattr(sys, 'frozen', False):
            # Running as PyInstaller exe
            self.project_dir = Path(sys.executable).parent.resolve()
        else:
            # Running as script
            self.project_dir = Path(__file__).resolve().parents[2]

        self.config_path = self.project_dir.joinpath("settings.ini").resolve()

        if not self.config_path.exists():
            self._create_default()

        self.config = configparser.ConfigParser()
        self.config.read(self.config_path)

        self.model = self.config["llm"]["model"]
        self.output_dir = Path(self.config["paths"]["output_dir"]).resolve()
        self.cover_letter_name = self.config["files"]["cover_letter_out"]
        self.resume_name = self.config["files"]["resume_out"]

    def _create_default(self):
        print("No settings.ini found. Creating default.")
        self.config_path.write_text(DEFAULT_INI)
