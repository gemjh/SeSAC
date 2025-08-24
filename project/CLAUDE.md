# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Structure

This is a machine learning and data science tutorial repository focused on three main technologies:

- **Streamlit**: Interactive web applications for data visualization and ML model deployment
- **Whisper**: OpenAI's speech recognition and translation models 
- **KoSpeech**: Korean speech recognition models

### Key Directories

- `Streamlit/`: Contains 4 progressive tutorial modules
  - `1. Basic/`: Basic Streamlit components and layouts
  - `2. Advanced/`: Session state management and advanced features
  - `3. Data Analysis/`: Interactive data analysis with bike sharing dataset
  - `4. Prediction Model/`: ML model deployment and prediction interface
  - `web/`: Production web applications (medical dashboard, database connections)

- `Whisper/`: Speech-to-text and translation examples
- `kospeech/`: Korean speech recognition experiments
- `spice/`: Additional speech processing experiments

## Common Commands

### Running Streamlit Applications
```bash
streamlit run "path/to/app.py"
```

Example:
```bash
streamlit run "Streamlit/1. Basic/magic_cmd.py"
```

### Whisper Installation and Usage
```bash
# Install Whisper
pip install -U openai-whisper

# Basic transcription
whisper audio_file.wav --model tiny

# With language specification
whisper audio_file.wav --model medium --language Korean --task translate
```

### Required Dependencies
For Whisper projects, install:
```bash
pip install numba numpy torch tqdm more-itertools tiktoken
```

## Architecture Overview

### Streamlit Applications
- **Progressive Learning Structure**: Each module builds on previous concepts
- **Data Processing Pattern**: Most apps use `@st.cache_data` for performance optimization
- **Common Libraries**: pandas, matplotlib, seaborn, streamlit for data apps
- **Model Integration**: Module 4 demonstrates ML model deployment with pickle files

### Notebook-First Development
- Primary development happens in Jupyter notebooks (`.ipynb` files)
- Python scripts (`.py` files) are typically cleaned-up versions for production
- Each major module has accompanying notebook documentation

### Data Pipeline
- CSV data files stored in `data/` subdirectories
- Preprocessing functions typically cached with `@st.cache_data`
- Feature engineering follows datetime parsing → derived features → mapping pattern

## File Patterns

### Streamlit Apps
- Use `st.set_page_config()` for page configuration
- Implement caching with `@st.cache_data` for data loading
- Follow pattern: data loading → preprocessing → visualization/interaction

### Whisper Integration
- Models loaded with `whisper.load_model(model_size)`
- Audio processed with `model.transcribe(audio_file)`
- Supports multiple languages and translation tasks

## Development Notes

- This repository appears to be educational/tutorial focused rather than production code
- Korean language content and comments throughout
- Mixed Korean and English file naming conventions
- No formal testing or CI/CD infrastructure detected