#!/usr/bin/env python3
"""
Academic Paper Translator and Summarizer
Processes PDF files using LLM for translation and summarization.
"""

import os
import sys
import yaml
import time
from pathlib import Path
from typing import Dict, Any, List
from tqdm import tqdm

from pdf_processor import PDFProcessor
from llm_client import LLMClient
from output_writer import OutputWriter


class PaperProcessor:
    """Main application class for processing academic papers."""

    def __init__(self, config_path: str = "config.yaml"):
        """
        Initialize the paper processor.

        Args:
            config_path: Path to configuration file
        """
        self.config = self._load_config(config_path)
        self._validate_config()

        # Initialize components
        self.pdf_processor = PDFProcessor(
            input_dir=self.config['paths']['input_dir'],
            file_types=self.config['processing']['file_types']
        )

        self.llm_client = LLMClient(
            base_url=self.config['api']['base_url'],
            api_key=self.config['api']['api_key'],
            model=self.config['api']['model'],
            max_tokens=self.config['advanced']['max_tokens'],
            temperature=self.config['advanced']['temperature'],
            timeout=self.config['advanced'].get('timeout', 300)
        )

        self.output_writer = OutputWriter(
            output_format=self.config['processing']['output_format'],
            formatting_config=self.config.get('formatting', {}),
            output_language=self.config['processing']['output_language']
        )

        # Statistics
        self.stats = {
            'total_files': 0,
            'successful': 0,
            'failed': 0,
            'skipped': 0,
            'translated': 0,
            'summarized': 0
        }

    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """
        Load configuration from YAML file.

        Args:
            config_path: Path to config file

        Returns:
            Configuration dictionary
        """
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            return config
        except FileNotFoundError:
            print(f"Error: Configuration file '{config_path}' not found.")
            sys.exit(1)
        except yaml.YAMLError as e:
            print(f"Error parsing configuration file: {str(e)}")
            sys.exit(1)

    def _validate_config(self):
        """Validate required configuration parameters."""
        required_keys = [
            ('api', 'base_url'),
            ('api', 'api_key'),
            ('api', 'model'),
            ('processing', 'mode'),
            ('paths', 'input_dir')
        ]

        for keys in required_keys:
            current = self.config
            for key in keys:
                if key not in current:
                    print(f"Error: Missing required configuration: {'.'.join(keys)}")
                    sys.exit(1)
                current = current[key]

        # Validate processing mode
        valid_modes = ['translate', 'summarize', 'both']
        mode = self.config['processing']['mode']
        if mode not in valid_modes:
            print(f"Error: Invalid processing mode '{mode}'. Must be one of {valid_modes}")
            sys.exit(1)

    def _check_output_exists(self, file_path: Path) -> Dict[str, bool]:
        """
        Check if output files already exist for a given input file.

        Args:
            file_path: Path to the input file

        Returns:
            Dictionary with 'translate' and 'summarize' keys indicating if outputs exist
        """
        mode = self.config['processing']['mode']
        output_format = self.config['processing']['output_format']
        base_filename = file_path.stem

        # Get relative path
        relative_path = self.pdf_processor.get_relative_path(file_path)
        relative_dir = Path(relative_path).parent

        exists = {'translate': False, 'summarize': False}

        # Check translation output
        if mode in ['translate', 'both']:
            translate_path = Path(self.config['paths']['translate_dir']) / relative_dir / f"{base_filename}.{output_format}"
            exists['translate'] = translate_path.exists()

        # Check summarization output
        if mode in ['summarize', 'both']:
            summarize_path = Path(self.config['paths']['summarize_dir']) / relative_dir / f"{base_filename}.{output_format}"
            exists['summarize'] = summarize_path.exists()

        return exists

    def process_file(self, file_path: Path) -> bool:
        """
        Process a single file (translate and/or summarize).

        Args:
            file_path: Path to the file to process

        Returns:
            True if successful, False otherwise
        """
        show_timing = self.config['advanced'].get('show_timing', True)
        skip_existing = self.config['advanced'].get('skip_existing', True)
        mode = self.config['processing']['mode']

        # Check if outputs already exist
        if skip_existing:
            outputs_exist = self._check_output_exists(file_path)

            # Determine if we should skip this file entirely
            should_skip = False
            if mode == 'both':
                # Skip only if BOTH outputs exist
                should_skip = outputs_exist['translate'] and outputs_exist['summarize']
            elif mode == 'translate':
                should_skip = outputs_exist['translate']
            elif mode == 'summarize':
                should_skip = outputs_exist['summarize']

            if should_skip:
                relative_path = self.pdf_processor.get_relative_path(file_path)
                print(f"  ⊘ Skipped (already processed): {relative_path}")
                self.stats['skipped'] += 1
                return True  # Return True because it's not a failure

        if show_timing:
            print(f"\n{'='*70}")
            print(f"Processing: {file_path.name}")
            print(f"{'='*70}")

        # Extract content
        t_start = time.time()
        content, success = self.pdf_processor.get_file_content(file_path)
        t_extract = time.time() - t_start

        if not success or not content.strip():
            print(f"  ✗ Failed to extract content from {file_path.name}")
            return False

        # Truncate content if needed
        max_chars = self.config['advanced'].get('max_content_chars', 0)
        original_length = len(content)
        if max_chars > 0 and len(content) > max_chars:
            content = content[:max_chars]
            if show_timing:
                print(f"⚠️  Content truncated from {original_length:,} to {max_chars:,} chars")

        if show_timing:
            print(f"⏱️  PDF Extraction: {t_extract:.2f}s ({len(content):,} chars)")

        # Get processing mode
        output_language = self.config['processing']['output_language']

        # Get base filename without extension
        base_filename = file_path.stem

        # Get relative path for preserving directory structure
        relative_path = self.pdf_processor.get_relative_path(file_path)
        relative_dir = Path(relative_path).parent

        file_success = True

        # Check which outputs to skip (for mode='both')
        skip_translate = False
        skip_summarize = False
        if skip_existing:
            outputs_exist = self._check_output_exists(file_path)
            skip_translate = outputs_exist['translate']
            skip_summarize = outputs_exist['summarize']

        # Process translation
        if mode in ['translate', 'both'] and not skip_translate:
            if show_timing:
                print(f"\n📝 Starting translation...")
            t_start = time.time()
            translated = self.llm_client.translate(
                content=content,
                prompt_template=self.config['prompts']['translation'],
                output_language=output_language
            )
            t_translate = time.time() - t_start
            if show_timing:
                print(f"⏱️  LLM Translation: {t_translate:.2f}s")

            if translated:
                t_start = time.time()
                output_dir = Path(self.config['paths']['translate_dir']) / relative_dir
                success = self.output_writer.write(translated, output_dir, base_filename)
                t_write = time.time() - t_start
                if show_timing:
                    print(f"⏱️  File Writing: {t_write:.2f}s")

                if success:
                    print(f"  ✓ Translated: {relative_path}")
                    self.stats['translated'] += 1
                else:
                    print(f"  ✗ Failed to write translation: {relative_path}")
                    file_success = False
            else:
                print(f"  ✗ Failed to translate: {relative_path}")
                file_success = False

        # Show skip message for translation if skipped
        elif mode in ['translate', 'both'] and skip_translate:
            if show_timing:
                print(f"  ⊘ Translation already exists, skipping...")

        # Process summarization
        if mode in ['summarize', 'both'] and not skip_summarize:
            if show_timing:
                print(f"\n📊 Starting summarization...")
            t_start = time.time()
            summarized = self.llm_client.summarize(
                content=content,
                prompt_template=self.config['prompts']['summarization'],
                output_language=output_language
            )
            t_summarize = time.time() - t_start
            if show_timing:
                print(f"⏱️  LLM Summarization: {t_summarize:.2f}s")

            if summarized:
                t_start = time.time()
                output_dir = Path(self.config['paths']['summarize_dir']) / relative_dir
                success = self.output_writer.write(summarized, output_dir, base_filename)
                t_write = time.time() - t_start
                if show_timing:
                    print(f"⏱️  File Writing: {t_write:.2f}s")

                if success:
                    print(f"  ✓ Summarized: {relative_path}")
                    self.stats['summarized'] += 1
                else:
                    print(f"  ✗ Failed to write summary: {relative_path}")
                    file_success = False
            else:
                print(f"  ✗ Failed to summarize: {relative_path}")
                file_success = False

        # Show skip message for summarization if skipped
        elif mode in ['summarize', 'both'] and skip_summarize:
            if show_timing:
                print(f"  ⊘ Summarization already exists, skipping...")

        return file_success

    def run(self):
        """Main execution method."""
        print("=" * 70)
        print("Academic Paper Translator & Summarizer")
        print("=" * 70)
        print()

        # Display configuration
        print(f"Model: {self.config['api']['model']}")
        print(f"Processing Mode: {self.config['processing']['mode']}")
        print(f"Output Language: {self.config['processing']['output_language']}")
        print(f"Output Format: {self.config['processing']['output_format']}")
        print(f"Input Directory: {self.config['paths']['input_dir']}")
        print()

        # Find files
        print("Scanning for files...")
        files = self.pdf_processor.find_files()
        self.stats['total_files'] = len(files)

        if not files:
            print(f"No files found in '{self.config['paths']['input_dir']}'")
            print(f"Looking for file types: {', '.join(self.config['processing']['file_types'])}")
            return

        print(f"Found {len(files)} file(s) to process")
        print()

        # Process files
        print("Processing files...")
        print("-" * 70)

        # Create progress bar if enabled
        if self.config['advanced']['show_progress']:
            iterator = tqdm(files, desc="Processing", unit="file")
        else:
            iterator = files

        for file_path in iterator:
            if self.config['advanced']['show_progress']:
                iterator.set_description(f"Processing {file_path.name}")

            try:
                success = self.process_file(file_path)

                if success:
                    self.stats['successful'] += 1
                else:
                    self.stats['failed'] += 1

                    if not self.config['advanced']['continue_on_error']:
                        print("\nStopping due to error (continue_on_error is disabled)")
                        break

            except Exception as e:
                print(f"  ✗ Unexpected error processing {file_path.name}: {str(e)}")
                self.stats['failed'] += 1

                if not self.config['advanced']['continue_on_error']:
                    print("\nStopping due to error (continue_on_error is disabled)")
                    break

        # Print summary
        print()
        print("=" * 70)
        print("Processing Complete")
        print("=" * 70)
        print(f"Total files: {self.stats['total_files']}")
        print(f"Successful: {self.stats['successful']}")
        print(f"Skipped: {self.stats['skipped']}")
        print(f"Failed: {self.stats['failed']}")
        print(f"Translations: {self.stats['translated']}")
        print(f"Summaries: {self.stats['summarized']}")
        print()

        if self.stats['translated'] > 0:
            print(f"Translations saved to: {self.config['paths']['translate_dir']}/")

        if self.stats['summarized'] > 0:
            print(f"Summaries saved to: {self.config['paths']['summarize_dir']}/")

        print("=" * 70)


def main():
    """Entry point for the application."""
    # Check if custom config path is provided
    config_path = "config.yaml"
    if len(sys.argv) > 1:
        config_path = sys.argv[1]

    # Create and run processor
    processor = PaperProcessor(config_path)
    processor.run()


if __name__ == "__main__":
    main()
