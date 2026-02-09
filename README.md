# Neighborhood Library Service

A library management system built with Python (gRPC + FastAPI), PostgreSQL, and Next.js.

## Features

- **Books Management**: Create, read, update, and delete books
- **Members Management**: Manage library members with activation status
- **Borrowing Operations**: Track book borrowing and returns with due dates
- **Modern UI**: Clean, responsive interface built with Next.js

## Tech Stack

### Backend
- **Python** - Server implementation
- **gRPC** - High-performance RPC framework with Protocol Buffers
- **FastAPI** - REST API layer for frontend communication
- **PostgreSQL** - Relational database
- **SQLAlchemy** - ORM for database operations

### Frontend
- **Next.js 14** - React framework with App Router
- **TypeScript** - Type-safe JavaScript

### Infrastructure
- **Docker & Docker Compose** - Containerization

## Quick Start

### Prerequisites

- Docker and Docker Compose installed
- Ports 3002, 8000, 5432, 50051 available

### Running with Docker Compose

```bash
# Start all services
docker-compose up --build

# Access the application
# Frontend:    http://localhost:3002
# REST API:    http://localhost:8000
# API Docs:    http://localhost:8000/docs
```

### Stopping Services

```bash
# Stop all services
docker-compose down

# Stop and remove all data (including database)
docker-compose down -v
```

## Project Structure

```
library-mangement-system/
├── backend/
│   ├── app/
│   │   ├── api/              # REST API routes and schemas
│   │   ├── domain/           # Domain entities (pure Python)
│   │   │   └── entities.py   # BookEntity, MemberEntity, BorrowRecordEntity
│   │   ├── repositories/     # Repository pattern implementation
│   │   │   ├── book_repository.py
│   │   │   ├── member_repository.py
│   │   │   ├── borrow_repository.py
│   │   │   └── unit_of_work.py  # Transaction management
│   │   ├── generated/        # Generated protobuf Python files
│   │   ├── services/         # gRPC service implementation
│   │   ├── config.py         # Application configuration
│   │   ├── database.py       # Database connection
│   │   ├── logging_config.py # Structured logging
│   │   ├── middleware.py     # Request logging middleware
│   │   └── models.py         # SQLAlchemy ORM models
│   ├── migrations/
│   │   └── init.sql          # Database schema and seed data
│   ├── protos/
│   │   └── library.proto     # Protocol Buffer definitions
│   ├── tests/                # Unit and integration tests
│   ├── logs/                 # Application log files
│   ├── requirements.txt      # Python dependencies
│   ├── server.py             # gRPC server entry point
│   ├── rest_server.py        # REST API server entry point
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── app/              # Next.js pages (App Router)
│   │   ├── components/       # Reusable UI components
│   │   └── lib/              # API client and types
│   ├── package.json
│   └── Dockerfile
├── docker-compose.yml
├── setup_steps.txt           # Quick setup commands
└── README.md
```

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Presentation Layer                        │
│         (REST API routes / gRPC Service)                     │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    Repository Layer                          │
│    (BookRepository, MemberRepository, BorrowRepository)     │
│                      Unit of Work                            │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                     Domain Layer                             │
│       (BookEntity, MemberEntity, BorrowRecordEntity)        │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                  Infrastructure Layer                        │
│              (SQLAlchemy ORM Models, Database)              │
└─────────────────────────────────────────────────────────────┘
```

## API Documentation

### REST API Endpoints

Access interactive documentation at: **http://localhost:8000/docs**

#### Books
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/books` | Create a new book |
| GET | `/api/books` | List books (with pagination & search) |
| GET | `/api/books/{id}` | Get book by ID |
| PUT | `/api/books/{id}` | Update book |
| DELETE | `/api/books/{id}` | Delete book |

#### Members
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/members` | Create a new member |
| GET | `/api/members` | List members (with pagination & search) |
| GET | `/api/members/{id}` | Get member by ID |
| PUT | `/api/members/{id}` | Update member |
| DELETE | `/api/members/{id}` | Delete member |
| GET | `/api/members/{id}/borrowed` | Get member's borrowed books |

#### Borrowing
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/borrows` | Borrow a book |
| GET | `/api/borrows` | List borrow records (with filters) |
| GET | `/api/borrows/{id}` | Get borrow record by ID |
| POST | `/api/borrows/{id}/return` | Return a book |

### gRPC Service

The gRPC service definitions are in `backend/protos/library.proto`.


## Database Schema

```sql
-- Books table
books (
  id SERIAL PRIMARY KEY,
  title VARCHAR(255) NOT NULL,
  author VARCHAR(255) NOT NULL,
  isbn VARCHAR(20) UNIQUE,
  published_year INTEGER,
  genre VARCHAR(100),
  total_copies INTEGER DEFAULT 1,
  available_copies INTEGER DEFAULT 1,
  created_at TIMESTAMP,
  updated_at TIMESTAMP
)

-- Members table
members (
  id SERIAL PRIMARY KEY,
  name VARCHAR(255) NOT NULL,
  email VARCHAR(255) UNIQUE NOT NULL,
  phone VARCHAR(20),
  address TEXT,
  membership_date DATE DEFAULT CURRENT_DATE,
  is_active BOOLEAN DEFAULT TRUE,
  created_at TIMESTAMP,
  updated_at TIMESTAMP
)

-- Borrow records table
borrow_records (
  id SERIAL PRIMARY KEY,
  book_id INTEGER REFERENCES books(id),
  member_id INTEGER REFERENCES members(id),
  borrow_date DATE NOT NULL,
  due_date DATE NOT NULL,
  return_date DATE,
  status VARCHAR(20) DEFAULT 'BORROWED',
  created_at TIMESTAMP,
  updated_at TIMESTAMP
)
```

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://library_user:library_pass@postgres:5432/library_db` |
| `REST_PORT` | REST API server port | `8000` |
| `GRPC_PORT` | gRPC server port | `50051` |
| `DEFAULT_BORROW_DAYS` | Default loan period | `14` |
| `MAX_BOOKS_PER_MEMBER` | Maximum books per member | `5` |
| `LOG_LEVEL` | Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL) | `INFO` |
| `LOG_FORMAT` | Log format ("json" for structured, "text" for human-readable) | `json` |
| `LOG_FILE` | Log file path | `logs/app.log` |
| `LOG_MAX_BYTES` | Max log file size before rotation | `10485760` (10 MB) |
| `LOG_BACKUP_COUNT` | Number of backup log files to keep | `5` |

## Logging

The application uses structured JSON logging for production-ready log management.

### Log Locations

- **Console (stdout)**: Always enabled, shows real-time logs
- **File**: `backend/logs/app.log` (with automatic rotation)

### Log Format

Logs are output in JSON format (by default) for easy parsing and analysis:

```json
{
  "timestamp": "2024-01-29T10:30:45.123456Z",
  "level": "INFO",
  "logger": "api.routes",
  "message": "Book borrowed",
  "module": "routes",
  "function": "borrow_book",
  "line": 320,
  "borrow_id": 15,
  "book_id": 3,
  "member_id": 2,
  "due_date": "2024-02-12"
}
```

### Request Logging

All HTTP requests are automatically logged with:
- Request ID (added to response headers as `X-Request-ID`)
- HTTP method and path
- Client IP address
- Response status code
- Duration in milliseconds

### Viewing Logs

```bash
# View real-time console logs
docker-compose logs -f backend

```

### Configuration

Set environment variables to customize logging:

```bash
# In .env file or docker-compose.yml
LOG_LEVEL=DEBUG          # More verbose logging
LOG_FILE=logs/app.log    # Log file location
```


## Troubleshooting

### Port Conflicts
```bash
# Check what's using a port
lsof -i :3002
lsof -i :8000

# Modify ports in docker-compose.yml if needed
```

### Database Connection Issues
```bash
# Check if postgres container is healthy
docker-compose ps

# View postgres logs
docker-compose logs postgres
```

### Rebuild Everything
```bash
# Full rebuild (removes all data)
docker-compose down -v
docker-compose up --build
```

## Development (Without Docker)

### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
./generate_proto.sh
python rest_server.py
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

## Testing

### Backend Tests (Python/pytest)

```bash
cd backend

# Install dependencies (if not already)
pip install -r requirements.txt

# Run all tests
pytest
```

### Frontend Tests (TypeScript/Jest)

```bash
cd frontend

# Install dependencies (if not already)
npm install

# Run all tests
npm test
```

### Test Structure

```
backend/tests/
├── conftest.py           # Pytest fixtures
├── test_api_books.py     # Books API unit tests
├── test_api_members.py   # Members API unit tests
├── test_api_borrows.py   # Borrows API unit tests
└── test_integration.py   # End-to-end integration tests

frontend/src/lib/__tests__/
├── validation.test.ts    # Validation utilities tests
└── api-endpoints.test.ts # API endpoints tests
```

### Integration Tests

The integration tests (`test_integration.py`) cover complete workflows:

| Test | Description |
|------|-------------|
| `test_full_borrow_return_cycle_restores_availability` | Complete borrow/return cycle verifies availability tracking |
| `test_member_can_borrow_up_to_limit_then_borrow_again_after_returning` | Member borrow limit enforcement and recovery |
| `test_multiple_members_borrow_limited_copies` | Multiple members competing for limited book copies |
| `test_member_lifecycle_with_borrow_history` | Member creation, borrowing, returning, deactivation |
| `test_member_without_history_can_be_deleted` | Clean member deletion |
| `test_book_lifecycle_with_borrow_history` | Book creation, copy management, borrowing, updates |
| `test_book_without_history_can_be_deleted` | Clean book deletion |

