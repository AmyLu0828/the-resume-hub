# Resume Builder Backend

A FastAPI-based backend service for the Resume Builder application that provides PDF generation and AI-powered content improvement.

## Features

- **PDF Generation**: Convert resume data to professional PDF documents using LaTeX
- **AI Content Improvement**: Enhance resume content using OpenAI's GPT models
- **RESTful API**: Clean, documented API endpoints for frontend integration
- **CORS Support**: Configured for frontend development servers
- **Template System**: Flexible LaTeX template system with multiple styles
- **Data Validation**: Comprehensive Pydantic models for data validation

## Prerequisites

### System Requirements

1. **Python 3.8+**
2. **LaTeX Distribution**: Install one of the following:
   - **TeX Live** (Linux/macOS): `sudo apt-get install texlive-full` (Ubuntu/Debian)
   - **MiKTeX** (Windows): Download from https://miktex.org/
   - **MacTeX** (macOS): Download from https://tug.org/mactex/

3. **OpenAI API Key**: Required for content improvement features

## Installation

1. **Clone the repository** (if not already done):
   ```bash
   cd backend
   ```

2. **Create a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**:
   ```bash
   cp env.example .env
   # Edit .env with your configuration
   ```

## Configuration

### Environment Variables

Create a `.env` file in the backend directory with the following variables:

```env
# Required: OpenAI API Configuration
OPENAI_API_KEY=your_openai_api_key_here
BASE_URL=https://api.openai.com/v1

# Server Configuration
HOST=0.0.0.0
PORT=8000
DEBUG=true

# CORS Configuration (frontend URLs)
CORS_ORIGINS=http://localhost:3000,http://localhost:5173,http://127.0.0.1:5173

# LaTeX Configuration
LATEX_COMPILER=pdflatex
LATEX_TIMEOUT=60

# Logging
LOG_LEVEL=INFO
```

### Getting an OpenAI API Key

1. Go to [OpenAI Platform](https://platform.openai.com/)
2. Create an account or sign in
3. Navigate to API Keys section
4. Create a new API key
5. Add it to your `.env` file

## Running the Backend

### Development Mode

```bash
# Activate virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Run the server
python main.py
```

Or using uvicorn directly:

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### Production Mode

```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

The server will be available at `http://localhost:8000`

## API Endpoints

### Health Check
- **GET** `/api/health` - Check if the API is running

### Content Improvement
- **POST** `/api/polish-content` - Improve individual content sections
- **POST** `/api/polish-batch` - Improve multiple content updates

### PDF Generation
- **POST** `/api/generate-pdf` - Generate PDF from resume data
- **POST** `/api/preview-latex` - Preview LaTeX source (debugging)

### Templates
- **GET** `/api/templates` - Get available LaTeX templates

## API Documentation

Once the server is running, you can access:

- **Interactive API Docs**: http://localhost:8000/docs
- **ReDoc Documentation**: http://localhost:8000/redoc

## Project Structure

```
backend/
├── main.py                 # FastAPI application entry point
├── models/
│   └── resume_models.py    # Pydantic data models
├── agents/
│   ├── improvement_agent.py # AI content improvement
│   └── latex_agent.py      # LaTeX template processing
├── services/
│   └── pdf_service.py      # PDF generation service
├── templates/
│   └── default_resume.tex  # LaTeX template
├── requirements.txt        # Python dependencies
├── env.example            # Environment variables template
└── README.md              # This file
```

## Development

### Adding New Templates

1. Create a new `.tex` file in the `templates/` directory
2. Use Jinja2 syntax for dynamic content
3. Add the template name to `available_templates` in `latex_agent.py`

### Testing

```bash
# Run tests
pytest

# Run with coverage
pytest --cov=.
```

### Code Style

The project follows PEP 8 style guidelines. Use a linter like `flake8` or `black` for code formatting.

## Troubleshooting

### Common Issues

1. **LaTeX not found**: Ensure LaTeX is installed and `pdflatex` is in your PATH
2. **OpenAI API errors**: Check your API key and ensure you have sufficient credits
3. **CORS errors**: Verify the frontend URL is in the `CORS_ORIGINS` list
4. **PDF generation fails**: Check LaTeX installation and template syntax

### Debug Mode

Enable debug mode in your `.env` file:
```env
DEBUG=true
```

This will provide more detailed error messages and logging.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is part of the Resume Builder application.
