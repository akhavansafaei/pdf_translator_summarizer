import os
from pathlib import Path
from typing import List, Tuple
import pdfplumber


class PDFProcessor:
    """Handles PDF file discovery and content extraction."""

    def __init__(self, input_dir: str, file_types: List[str]):
        """
        Initialize PDF processor.

        Args:
            input_dir: Root directory to search for files
            file_types: List of file extensions to process (e.g., ['pdf', 'txt'])
        """
        self.input_dir = Path(input_dir)
        self.file_types = [ft.lower().strip('.') for ft in file_types]

    def find_files(self) -> List[Path]:
        """
        Recursively find all files with specified extensions in input directory.

        Returns:
            List of Path objects for found files
        """
        found_files = []

        if not self.input_dir.exists():
            print(f"Warning: Input directory '{self.input_dir}' does not exist.")
            return found_files

        for file_type in self.file_types:
            # Use rglob for recursive search
            pattern = f"**/*.{file_type}"
            files = list(self.input_dir.rglob(pattern))
            found_files.extend(files)

        # Remove duplicates and sort
        found_files = sorted(set(found_files))

        return found_files

    def extract_text_from_pdf(self, pdf_path: Path) -> Tuple[str, bool]:
        """
        Extract text content from a PDF file.

        Args:
            pdf_path: Path to the PDF file

        Returns:
            Tuple of (extracted_text, success_flag)
        """
        try:
            text_content = []

            with pdfplumber.open(pdf_path) as pdf:
                for page_num, page in enumerate(pdf.pages, 1):
                    # Extract text from page
                    page_text = page.extract_text()

                    if page_text:
                        text_content.append(f"--- Page {page_num} ---\n{page_text}")
                    else:
                        text_content.append(f"--- Page {page_num} ---\n[No extractable text]")

            full_text = "\n\n".join(text_content)

            if not full_text.strip():
                return "", False

            return full_text, True

        except Exception as e:
            print(f"Error extracting text from {pdf_path.name}: {str(e)}")
            return "", False

    def read_text_file(self, file_path: Path) -> Tuple[str, bool]:
        """
        Read content from a text file.

        Args:
            file_path: Path to the text file

        Returns:
            Tuple of (file_content, success_flag)
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            return content, True
        except Exception as e:
            print(f"Error reading file {file_path.name}: {str(e)}")
            return "", False

    def get_file_content(self, file_path: Path) -> Tuple[str, bool]:
        """
        Get content from a file based on its type.

        Args:
            file_path: Path to the file

        Returns:
            Tuple of (content, success_flag)
        """
        extension = file_path.suffix.lower().strip('.')

        if extension == 'pdf':
            return self.extract_text_from_pdf(file_path)
        elif extension in ['txt', 'md', 'tex']:
            return self.read_text_file(file_path)
        else:
            print(f"Unsupported file type: {extension}")
            return "", False

    def get_relative_path(self, file_path: Path) -> str:
        """
        Get relative path of file from input directory.

        Args:
            file_path: Absolute path to file

        Returns:
            Relative path as string
        """
        try:
            return str(file_path.relative_to(self.input_dir))
        except ValueError:
            return file_path.name
