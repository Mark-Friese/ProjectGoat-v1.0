# Contributing to ProjectGoat

Thank you for your interest in contributing to ProjectGoat! This document provides guidelines for contributing to the project.

## Code of Conduct

Please be respectful and constructive in all interactions. We aim to maintain a welcoming and inclusive community.

## How to Contribute

### Reporting Bugs

1. Check if the bug has already been reported in [Issues](../../issues)
2. If not, create a new issue with:
   - Clear title and description
   - Steps to reproduce
   - Expected vs actual behavior
   - Environment details (OS, Python version, browser)
   - Screenshots if applicable

### Suggesting Features

1. Check [Issues](../../issues) for existing feature requests
2. Create a new issue with:
   - Clear description of the feature
   - Use cases and benefits
   - Potential implementation approach (optional)

### Pull Requests

1. **Fork the repository**
2. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Make your changes**
   - Follow existing code style
   - Add tests if applicable
   - Update documentation as needed

4. **Test your changes**
   ```bash
   # Backend tests
   python -m pytest

   # Frontend tests (if applicable)
   npm test
   ```

5. **Commit with clear messages**
   ```bash
   git commit -m "feat: Add user profile customization"
   ```

6. **Push to your fork**
   ```bash
   git push origin feature/your-feature-name
   ```

7. **Create a Pull Request**
   - Describe what changes you made and why
   - Reference any related issues
   - Ensure all tests pass

## Development Setup

### Prerequisites
- Python 3.9 or higher
- Node.js 16 or higher
- Git

### Local Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/YourUsername/ProjectGoat.git
   cd ProjectGoat
   ```

2. **Backend setup**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Frontend setup**
   ```bash
   npm install
   ```

4. **Run the application**
   ```bash
   # Terminal 1: Backend
   python run.py

   # Terminal 2: Frontend (development)
   npm run dev
   ```

5. **Access the application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000/api
   - API Docs: http://localhost:8000/docs

## Code Style

### Python
- Follow PEP 8 guidelines
- Use type hints where applicable
- Document functions with docstrings
- Maximum line length: 100 characters

### TypeScript/React
- Use TypeScript for type safety
- Follow existing component patterns
- Use functional components with hooks
- Organize imports: React → libraries → local

### Commit Messages
Use conventional commits format:
- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation changes
- `style:` Code style changes (formatting)
- `refactor:` Code refactoring
- `test:` Test additions or modifications
- `chore:` Build process or auxiliary tool changes

## Project Structure

```
ProjectGoat/
├── backend/              # Python/FastAPI backend
│   ├── main.py          # API endpoints
│   ├── models.py        # Database models
│   ├── schemas.py       # Pydantic schemas
│   ├── crud.py          # Database operations
│   ├── auth.py          # Authentication
│   └── config.py        # Configuration
├── src/                 # React/TypeScript frontend
│   ├── components/      # React components
│   ├── services/        # API client
│   ├── types/           # TypeScript types
│   └── App.tsx          # Main application
├── tests/               # Test files
├── run.py              # Startup script
└── README.md           # Project documentation
```

## Testing

### Backend Tests
```bash
# Run all tests
python -m pytest

# Run with coverage
python -m pytest --cov=backend

# Run specific test file
python -m pytest tests/test_auth.py
```

### Frontend Tests
```bash
# Run unit tests
npm test

# Run E2E tests
npm run test:e2e
```

## Documentation

- Update README.md for user-facing changes
- Update DEPLOYMENT.md for deployment-related changes
- Add docstrings to new Python functions
- Add comments for complex logic

## Questions?

If you have questions about contributing:
1. Check existing documentation
2. Search [Issues](../../issues) for similar questions
3. Create a new issue with the "question" label

## License

By contributing to ProjectGoat, you agree that your contributions will be licensed under the MIT License.

Thank you for contributing! 🐐
