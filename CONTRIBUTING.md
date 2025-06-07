# Contributing to Game Arcade API

Thank you for your interest in contributing to the Game Arcade API! We welcome contributions from everyone, whether it's fixing bugs, adding new features, improving documentation, or suggesting enhancements.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Workflow](#development-workflow)
- [Code Style](#code-style)
- [Testing](#testing)
- [Pull Request Process](#pull-request-process)
- [Reporting Bugs](#reporting-bugs)
- [Feature Requests](#feature-requests)
- [License](#license)

## Code of Conduct

This project and everyone participating in it is governed by our [Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code.

## Getting Started

1. **Fork** the repository on GitHub
2. **Clone** the project to your own machine
3. **Commit** changes to your own branch
4. **Push** your work back up to your fork
5. Submit a **Pull Request** so we can review your changes

### Prerequisites

- Python 3.8+
- pip
- Git

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/game-arcade-api.git
   cd game-arcade-api
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install development dependencies:
   ```bash
   make install
   ```

## Development Workflow

1. Create a new branch for your feature or bugfix:
   ```bash
   git checkout -b feature/your-feature-name
   # or
   git checkout -b bugfix/issue-number-description
   ```

2. Make your changes and commit them with a descriptive message:
   ```bash
   git commit -m "Add new feature for X"
   ```

3. Push your changes to your fork:
   ```bash
   git push origin your-branch-name
   ```

4. Open a Pull Request against the `main` branch

## Code Style

We use several tools to maintain code quality and style:

- **Black** for code formatting
- **isort** for import sorting
- **flake8** for linting
- **mypy** for static type checking

Run the following commands to ensure your code adheres to our standards:

```bash
make format  # Auto-format your code
make lint    # Check for style issues
make typecheck  # Run type checking
```

## Testing

We use `pytest` for testing. Follow these guidelines:

1. Write tests for new features or bug fixes
2. Ensure all tests pass before submitting a PR
3. Add appropriate docstrings to test functions

Run tests with:

```bash
make test  # Run all tests with coverage
make test-fast  # Run tests quickly without coverage
```

## Pull Request Process

1. Ensure any install or build dependencies are removed before the end of the layer when doing a build
2. Update the README.md with details of changes to the interface, including new environment variables, exposed ports, useful file locations, and container parameters
3. Increase the version numbers in any examples files and the README.md to the new version that this Pull Request would represent. The versioning scheme we use is [SemVer](http://semver.org/)
4. Your pull request will be reviewed by the maintainers
5. Once approved, your changes will be merged into the main branch

## Reporting Bugs

Use GitHub Issues to report bugs. Please include:

- A clear, descriptive title
- Steps to reproduce the issue
- Expected vs. actual behavior
- Any relevant error messages or logs
- Your environment (OS, Python version, etc.)

## Feature Requests

We welcome feature requests! Please open an issue with:

- A clear, descriptive title
- A detailed description of the feature
- Any relevant use cases or examples
- Any alternative solutions or workarounds you've considered

## License

By contributing, you agree that your contributions will be licensed under the [MIT License](LICENSE).
