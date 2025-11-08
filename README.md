# Warehouse Neuron

A warehouse management system with stock tracking and movement capabilities.

## Development Setup

This project uses Nix flakes for reproducible development environments with automatic Python virtual environment setup.

### Prerequisites

- [Nix](https://nixos.org/download.html) with flakes enabled
- [direnv](https://direnv.net/) (recommended for automatic environment loading)

### Getting Started

1. **With direnv (recommended):**
   ```bash
   # Allow direnv for this directory
   direnv allow
   
   # The environment will load automatically when you cd into the directory
   # A Python venv will be created at .venv and activated automatically
   ```

2. **Without direnv:**
   ```bash
   # Enter the Nix development shell manually
   nix develop
   
   # The venv will be created and activated automatically
   ```

### Code Formatting

The project uses Black and isort for Python code formatting:

```bash
# Format all Python files
isort . && black .
```

### Project Structure

```
warehouse-neuron/
├── services/
│   ├── backend/          # FastAPI backend
│   │   ├── app/
│   │   │   ├── config.py
│   │   │   ├── database.py
│   │   │   ├── models.py
│   │   │   ├── schema.py
│   │   │   ├── crud.py
│   │   │   └── routes/
│   │   │       └── stock.py
│   │   ├── Dockerfile
│   │   └── requirements.txt
│   └── migrations/       # Database migrations
├── docker-compose.yml
└── flake.nix            # Nix development environment
```

### Running the Application

```bash
# Start services with Docker Compose
docker-compose up

# Backend API will be available at http://localhost:8000
```

### Environment Variables

Create a `.env` file in the backend directory:

```env
DATABASE_URL=postgresql+asyncpg://wn_user:wn_pass@localhost:5432/warehouse_neuron
REDIS_URL=redis://localhost:6379
APP_ENV=development
```
