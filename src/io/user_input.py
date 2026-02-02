import threading
import tkinter as tk
from tkinter import scrolledtext, font

from src.io import FileManager
from src.model import JobData
from src.workflow import ResumeWorkflow, CoverLetterWorkflow


class AppGUI:
    """
    Tkinter GUI for Resume & Cover Letter Generator
    """

    def __init__(self,
                 resume_workflow: ResumeWorkflow,
                 cover_letter_workflow: CoverLetterWorkflow,
                 file_manager: FileManager
                 ):
        # Inject dependencies
        self.resume_workflow = resume_workflow
        self.cover_workflow = cover_letter_workflow
        self.file_manager = file_manager

        # Build the UI form
        self.root = tk.Tk()
        self.root.tk.call("tk", "scaling", 1.25)
        self.root.title("Chat BDD: Resume Tailoring")
        icon_path = self.file_manager.project_dir / "bdd.ico"
        try:
            if icon_path.exists():
                self.root.iconbitmap(icon_path)
        except Exception as e:
            print(f"Warning: Could not load icon: {e}")
        default_font = font.nametofont("TkDefaultFont")
        default_font.configure(size=11)
        self.text_font = font.nametofont("TkTextFont")
        self.text_font.configure(size=11)
        self._build_form()

        # Initialize loading spinner variables
        self._loading = False
        self._spinner_chars = "⠁⠂⠄⡀⡈⡐⡠⣀⣁⣂⣄⣌⣔⣤⣥⣦⣮⣶⣷⣿⡿⠿⢟⠟⡛⠛⠫⢋⠋⠍⡉⠉⠑⠡⢁"
        self._spinner_index = 0
        self._spinner_text = "Generating..."

    def _build_form(self):
        """Build all input fields and buttons with left alignment"""

        pad_opts = {"padx": 5, "pady": 5}

        # Company
        tk.Label(self.root, text="Company", anchor="w").grid(row=0, column=0, sticky="w", **pad_opts)
        self.company_entry = tk.Entry(self.root, width=40)
        self.company_entry.grid(row=0, column=1, sticky="w", **pad_opts)
        self.company_err = tk.Label(self.root, text="", fg="red", anchor="w", justify="left")
        self.company_err.grid(row=0, column=2, sticky="w", **pad_opts)
        self.company_entry.bind(
            "<KeyRelease>",
            lambda e: self.company_err.config(text="")
        )

        # Position
        tk.Label(self.root, text="Position", anchor="w").grid(row=1, column=0, sticky="w", **pad_opts)
        self.position_entry = tk.Entry(self.root, width=40)
        self.position_entry.grid(row=1, column=1, sticky="w", **pad_opts)
        self.position_err = tk.Label(self.root, text="", fg="red", anchor="w", justify="left")
        self.position_err.grid(row=1, column=2, sticky="w", **pad_opts)
        self.position_entry.bind(
            "<KeyRelease>",
            lambda e: self.position_err.config(text="")
        )

        # Location
        tk.Label(self.root, text="Location", anchor="w").grid(row=2, column=0, sticky="w", **pad_opts)
        self.location_entry = tk.Entry(self.root, width=40)
        self.location_entry.grid(row=2, column=1, sticky="w", **pad_opts)
        self.location_optional = tk.Label(self.root, text="(optional)", fg="grey", anchor="w", justify="left")
        self.location_optional.grid(row=2, column=2, sticky="w", **pad_opts)
        self.location_entry.bind(
            "<KeyRelease>",
            lambda e: self.location_optional.config(text="")
        )

        # Job Description
        tk.Label(self.root, text="Job Description", anchor="w").grid(row=3, column=0, sticky="nw", **pad_opts)
        self.description_text = scrolledtext.ScrolledText(
            self.root,
            width=60,
            height=15,
            wrap=tk.WORD,
            font=self.text_font
        )
        self.description_text.grid(row=3, column=1, rowspan=2, columnspan=2, sticky="nsew", **pad_opts)
        self.description_err = tk.Label(self.root, text="", fg="red", anchor="w", justify="left")
        self.description_err.grid(row=4, column=0, sticky="nw", **pad_opts)
        self.description_text.bind(
            "<KeyRelease>",
            lambda e: self.description_err.config(text="")
        )

        # Cover Letter checkbox
        self.cover_var = tk.BooleanVar(value=True)  # default ON
        self.cover_cb = tk.Checkbutton(
            self.root,
            text="Cover Letter",
            variable=self.cover_var
        )
        self.cover_cb.grid(row=5, column=0, sticky="w", **pad_opts)

        # Generate button
        self.generate_btn = tk.Button(self.root, text="Generate", command=self._generate)
        self.generate_btn.grid(row=5, column=1, sticky="w", **pad_opts)

        # Status/output label
        self.status_label = tk.Label(self.root, text="Chat BDD IS READY TO COOK  👈(￣▽￣👈)", fg="Black", anchor="w", justify="left")
        self.status_label.grid(row=6, column=0, columnspan=3, sticky="w", **pad_opts)

        # Make job description expand if window resized
        self.root.grid_rowconfigure(4, weight=1)
        self.root.grid_columnconfigure(2, weight=1)

    def _generate(self):
        company = self.company_entry.get()
        position = self.position_entry.get()
        location = self.location_entry.get() or ""
        description = self.description_text.get("1.0", tk.END).strip()

        if not self._input_validation():
            self.status_label.config(text="Please fill in required fields  (╯ ▔皿▔)╯", fg="red")
            return

        job = JobData(
            company=company,
            job_title=position,
            location=location,
            job_description=description
        )

        # Run workflows in background thread
        thread = threading.Thread(
            target=self._run_workflows,
            args=(job,),
            daemon=True
        )
        thread.start()

    def _input_validation(self):
        company = self.company_entry.get()
        position = self.position_entry.get()
        description = self.description_text.get("1.0", tk.END).strip()
        valid = True

        if not company:
            self.company_err.config(text="Company Required")
            valid = False
        if not position:
            self.position_err.config(text="Position Required")
            valid = False
        if not description:
            self.description_err.config(text="Required")
            valid = False

        return valid

    def _run_workflows(self, job: JobData):
        self._set_ui_state(False)
        try:
            self._spinner_text = "Generating Resume  (～￣▽￣)～"
            self._start_spinner()
            self.resume_workflow.run(job)

            if self.cover_var.get():
                self._spinner_text = "Generating Cover Letter  (～￣▽￣)～"
                self.cover_workflow.run(job)

            self.root.after(0, self._stop_spinner())
            self.root.after(0, self._on_success(job))

        except Exception as e:
            self.root.after(0, self._stop_spinner())
            self.root.after(0, self._on_error(str(e)))

    def _on_success(self, job):
        self.status_label.config(
            text=f"Files generated successfully for {job.company} {job.job_title}  (-￣▽￣-)👍",
            fg="green"
        )

        self.company_entry.delete(0, tk.END)
        self.position_entry.delete(0, tk.END)
        self.location_optional.config(text="(optional)")
        self.location_entry.delete(0, tk.END)
        self.description_text.delete("1.0", tk.END)
        self._set_ui_state(True)

    def _on_error(self, message):
        self.status_label.config(text="Oopsie (￣ー￣* )... "+message, fg="red")
        self._set_ui_state(True)

    def _start_spinner(self):
        self._loading = True
        self._spinner_index = 0
        self._spin()

    def _spin(self):
        if not self._loading:
            return

        char = self._spinner_chars[self._spinner_index]
        self.status_label.config(text=f"{self._spinner_text}{char}", fg="blue")

        self._spinner_index = (self._spinner_index + 1) % len(self._spinner_chars)
        self.root.after(100, self._spin)  # 10 fps

    def _stop_spinner(self):
        self._loading = False

    def _set_ui_state(self, enabled: bool):
        state = "normal" if enabled else "disabled"
        inputs = [
            self.company_entry,
            self.position_entry,
            self.location_entry,
            self.description_text,
            self.generate_btn,
            self.cover_cb
        ]
        for inp in inputs:
            inp.config(state=state)

    def run(self):
        """Start the Tkinter main loop"""
        self.root.mainloop()
