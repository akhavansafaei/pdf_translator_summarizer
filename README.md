# Academic Paper Translator & Summarizer

A Python application that automatically translates and/or summarizes academic papers (PDF files) using Large Language Models (LLMs). The application recursively scans directories, processes PDF files, and generates translated/summarized outputs in various formats.

## Features

- **Recursive Directory Scanning**: Automatically finds all PDF files in subdirectories
- **Dual Processing Modes**: Translate, summarize, or both
- **Multiple Output Formats**: DOCX, LaTeX (TEX), TXT, or Markdown (MD)
- **Customizable Prompts**: Full control over translation and summarization prompts
- **Progress Tracking**: Visual progress bars and detailed statistics
- **Error Handling**: Continue processing even if individual files fail
- **Flexible Configuration**: All settings managed through YAML config file

## Project Structure

```
paper-translator/
├── config.yaml              # Configuration file
├── main.py                  # Main application
├── pdf_processor.py         # PDF processing logic
├── llm_client.py           # LLM API client
├── output_writer.py        # Output file generation
├── requirements.txt        # Python dependencies
├── README.md              # This file
├── papers/                # Input directory (with subdirectories)
├── translates/           # Translation outputs
└── summarizations/       # Summarization outputs
```

## Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### Setup Steps

1. **Clone or download this project**

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure the application**:
   - Open [config.yaml](config.yaml)
   - Update the API key and model if needed
   - Adjust other settings as desired (see Configuration section)

4. **Create input directory**:
   ```bash
   mkdir papers
   ```

   Place your PDF files in the `papers` directory or its subdirectories.

## Usage

### Basic Usage

Simply run the main script:

```bash
python main.py
```

The application will:
1. Load configuration from [config.yaml](config.yaml)
2. Scan the `papers` directory recursively for PDF files
3. Process each file according to the configured mode (translate/summarize/both)
4. Save outputs to `translates/` and/or `summarizations/` directories

### Custom Configuration File

You can specify a custom configuration file:

```bash
python main.py custom_config.yaml
```

## Configuration

All settings are managed in [config.yaml](config.yaml). Here are the key configuration options:

### API Settings

```yaml
api:
  base_url: "https://api.tokenfactory.nebius.com/v1/"
  api_key: "your-api-key-here"
  model: "openai/gpt-oss-120b"
```

**Available models** (see config file for full list):
- `openai/gpt-oss-120b` (default)
- `deepseek-ai/DeepSeek-V3-0324`
- `Qwen/Qwen3-235B-A22B-Instruct-2507`
- `NousResearch/Hermes-4-405B`
- And many more...

### Processing Options

```yaml
processing:
  mode: "both"                    # "translate", "summarize", or "both"
  file_types:                     # File extensions to process
    - "pdf"
  pdf_method: "extract"           # "extract" or "direct"
  output_language: "Persian"      # Target language
  output_format: "docx"          # "docx", "tex", "txt", or "md"
```

### Directory Paths

```yaml
paths:
  input_dir: "papers"
  translate_dir: "translates"
  summarize_dir: "summarizations"
```

### Customizable Prompts

You can fully customize the translation and summarization prompts in the config file:

```yaml
prompts:
  translation: |
    You are a professional translator. Translate the following...

  summarization: |
    You are an academic research assistant. Please provide a comprehensive summary...
```

**Prompt placeholders**:
- `{content}`: The extracted text from the PDF
- `{output_language}`: The configured output language

### Advanced Settings

```yaml
advanced:
  max_tokens: 16000              # Maximum response length
  temperature: 0.3               # LLM creativity (0.0-1.0)
  show_progress: true            # Show progress bar
  continue_on_error: true        # Continue if a file fails
```

## Output

### Directory Structure

The application preserves the directory structure from the input:

```
papers/
  ├── subfolder1/
  │   └── paper1.pdf
  └── subfolder2/
      └── paper2.pdf

translates/
  ├── subfolder1/
  │   └── paper1.docx
  └── subfolder2/
      └── paper2.docx

summarizations/
  ├── subfolder1/
  │   └── paper1.docx
  └── subfolder2/
      └── paper2.docx
```

### Output Formats

- **DOCX**: Microsoft Word format with proper formatting
- **TEX**: LaTeX document ready for compilation
- **TXT**: Plain text format
- **MD**: Markdown format

## Examples

### Example 1: Translate Only

Edit [config.yaml](config.yaml):
```yaml
processing:
  mode: "translate"
  output_language: "Persian"
  output_format: "docx"
```

Run:
```bash
python main.py
```

### Example 2: Summarize in English

Edit [config.yaml](config.yaml):
```yaml
processing:
  mode: "summarize"
  output_language: "English"
  output_format: "md"
```

Run:
```bash
python main.py
```

### Example 3: Both Translation and Summary

Edit [config.yaml](config.yaml):
```yaml
processing:
  mode: "both"
  output_language: "Persian"
  output_format: "docx"
```

Run:
```bash
python main.py
```

## Troubleshooting

### No files found

- Ensure PDF files are in the `papers` directory or subdirectories
- Check that `file_types` in config includes "pdf"
- Verify the `input_dir` path is correct

### API errors

- Verify your API key is correct in [config.yaml](config.yaml)
- Check that the model name is valid
- Ensure you have internet connection

### PDF extraction failed

- Some PDFs may be scanned images without text
- Try using a different PDF or use OCR preprocessing
- Check if the PDF is corrupted

### Out of memory

- Reduce `max_tokens` in advanced settings
- Process fewer files at once
- Use a smaller model

## Advanced Usage

### Processing Specific File Types

You can process other text-based files beyond PDFs:

```yaml
processing:
  file_types:
    - "pdf"
    - "txt"
    - "md"
```

### Using Different Models for Different Tasks

While the current version uses the same model for all tasks, you can create multiple config files:

```bash
python main.py config_translate.yaml  # For translation
python main.py config_summarize.yaml  # For summarization
```

## License

This project is provided as-is for academic and research purposes.

## Support

For issues or questions:
1. Check the troubleshooting section
2. Review the [config.yaml](config.yaml) settings
3. Ensure all dependencies are installed correctly

## Credits

Built with:
- OpenAI Python SDK
- pdfplumber for PDF processing
- python-docx for document generation
- PyYAML for configuration management
