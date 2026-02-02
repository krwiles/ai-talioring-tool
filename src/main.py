from src.config import AppSettings
from src.io import FileManager, AppGUI
from src.llm import OpenAIClient
from src.prompt import ResumePromptBuilder, CoverLetterPromptBuilder
from src.workflow import ResumeWorkflow, CoverLetterWorkflow


def main():
    settings = AppSettings()
    file_manager = FileManager(settings)
    llm = OpenAIClient(settings)

    resume_prompt = ResumePromptBuilder(file_manager)
    resume_workflow = ResumeWorkflow(
        prompt_builder=resume_prompt,
        llm_client=llm,
        file_manager=file_manager,
        settings=settings
    )

    cover_letter_prompt = CoverLetterPromptBuilder(file_manager)
    cover_letter_workflow = CoverLetterWorkflow(
        prompt_builder=cover_letter_prompt,
        llm_client=llm,
        file_manager=file_manager,
        settings=settings
    )

    gui = AppGUI(
        resume_workflow=resume_workflow,
        cover_letter_workflow=cover_letter_workflow,
        file_manager=file_manager
    )
    gui.run()


if __name__ == "__main__":
    main()
