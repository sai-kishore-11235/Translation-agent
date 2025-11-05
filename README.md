# Translation Agent

A multi-language translation agent built with **LangGraph** and **Google Gemini API** that translates text from Excel files to multiple target languages using a state-based workflow.

## Overview

This project demonstrates how to use LangGraph to orchestrate a translation workflow where text is translated sequentially to multiple languages. The agent reads text from an Excel file, translates it to 5 different languages (English US, English Australia, Vietnamese, Thai, and Hindi), and outputs the results to a new Excel file.

## Features

- 📝 **Excel-based I/O**: Reads input from Excel files and writes translations to Excel
- 🌍 **Multi-language Support**: Translates to 5 target languages
- 🔄 **LangGraph Workflow**: Uses state-based graph orchestration for sequential translations
- 🤖 **Google Gemini Integration**: Leverages Gemini 2.5 Flash model for high-quality translations
- 🐳 **Docker Support**: Containerized application for easy deployment
- 📊 **Batch Processing**: Processes multiple rows of text efficiently

## Architecture

The translation agent uses **LangGraph** to create a state machine workflow:

```
Original Text → en-US → en-AU → vi → th → hi → END
```

Each node in the graph translates the text to its target language and updates the shared state. The state accumulates all translations as it progresses through the workflow.

### State Structure

```python
TranslationState:
    original_text: str          # The original text to translate
    translations: dict          # Accumulated translations {lang_code: translation}
    current_language: str       # Current target language being processed
```

## Supported Languages

1. **English (US)** - `en-US`
2. **English (Australia)** - `en-AU`
3. **Vietnamese** - `vi`
4. **Thai** - `th`
5. **Hindi** - `hi`

## Prerequisites

- Python 3.11 or higher
- Google Gemini API key ([Get one here](https://makersuite.google.com/app/apikey))
- Docker (optional, for containerized deployment)

## Installation

### 1. Clone the repository

```bash
git clone <repository-url>
cd Translation-agent
```

### 2. Create a virtual environment

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Set up environment variables

Set your Google Gemini API key:

```bash
export GOOGLE_API_KEY="your-api-key-here"
```

On Windows:
```cmd
set GOOGLE_API_KEY=your-api-key-here
```

## Usage

### Command Line Interface

The main script accepts several command-line arguments:

```bash
python app.py [OPTIONS]
```

**Options:**
- `--input PATH`: Path to input Excel file (default: `./input.xlsx`)
- `--text-col COLUMN`: Name of the column containing text to translate (default: `Original Text`)
- `--output PATH`: Path for output Excel file (default: auto-generated timestamp filename)
- `--batch-size N`: Batch size for processing (reserved for future use)

**Example:**

```bash
python app.py --input ./input.xlsx --text-col "Original Text" --output ./translations.xlsx
```

### Input Format

The input Excel file should contain a column with the text you want to translate. By default, the script looks for a column named "Original Text".

**Example input.xlsx:**
| Original Text |
|---------------|
| Hello, world! |
| How are you? |
| Thank you |

### Output Format

The output Excel file contains:
- Original Text column
- One column for each target language translation

**Example output:**
| Original Text | English (US) | English (Australia) | Vietnamese | Thai | Hindi |
|---------------|--------------|---------------------|------------|------|-------|
| Hello, world! | Hello, world! | G'day, world! | ... | ... | ... |

## Docker Usage

### Build the Docker image

```bash
docker build -t translation-agent .
```

### Run with Docker

```bash
docker run --rm \
  -e GOOGLE_API_KEY="your-api-key-here" \
  -v $(pwd):/app/data \
  translation-agent \
  --input /app/data/input.xlsx \
  --output /app/data/translations.xlsx
```

## Project Structure

```
Translation-agent/
├── app.py                    # Main application script
├── translation_agent.ipynb   # Jupyter notebook for experimentation
├── requirements.txt          # Python dependencies
├── Dockerfile               # Docker configuration
├── .gitignore               # Git ignore rules
├── input.xlsx              # Sample input file
└── README.md               # This file
```

## How It Works

1. **Initialization**: The app builds a LangGraph workflow with nodes for each target language
2. **State Creation**: For each text, an initial state is created with the original text
3. **Sequential Translation**: The workflow processes translations sequentially:
   - Starts at `en-US` node
   - Moves through each language node
   - Each node translates and updates the state
4. **Result Aggregation**: All translations are collected in the state's `translations` dictionary
5. **Output**: Results are written to an Excel file with all translations

### Key Components

- **`build_app()`**: Constructs the LangGraph workflow with translation nodes
- **`translate_text()`**: Core translation function that calls Gemini API
- **`translate_texts()`**: Batch processing function that processes multiple texts
- **`create_translation_node()`**: Factory function that creates language-specific nodes

## Dependencies

- `langchain-google-genai`: Google Gemini API integration
- `langgraph`: State-based workflow orchestration
- `langchain-core`: Core LangChain functionality
- `pandas`: Data manipulation and Excel I/O
- `openpyxl`: Excel file reading/writing

## Error Handling

The application includes error handling:
- If a translation fails, an error message is written to the first language column
- Empty or missing text is handled gracefully
- Invalid column names are caught and reported

## Notes

- The translation workflow is sequential (not parallel) to ensure quality
- Temperature is set to 0.3 for consistent translations
- The model used is `gemini-2.5-flash` for fast and cost-effective translations

## Future Enhancements

- Parallel translation processing
- Progress tracking for large batches
- Support for additional languages
- Translation quality scoring
- Retry logic for API failures

## License

This project is part of a LangGraph study/experiment.

## Contributing

This is an experimental project. Feel free to fork and modify for your needs!

## Troubleshooting

### API Key Issues
- Ensure `GOOGLE_API_KEY` is set correctly
- Verify the API key has access to Gemini models

### Excel File Issues
- Ensure the input file has the correct column name
- Check that the file is not corrupted or password-protected

### Import Errors
- Make sure all dependencies are installed: `pip install -r requirements.txt`
- Verify Python version is 3.11 or higher

## Contact

For questions or issues, please open an issue in the repository.

