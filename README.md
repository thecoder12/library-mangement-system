# Neighborhood Library Service

A library management system built with Python (gRPC + FastAPI), PostgreSQL, and Next.js.

## Features

- **Books Management**: Create, read, update, and delete books
- **Members Management**: Manage library members with activation status
- **Borrowing Operations**: Track book borrowing and returns with due dates

## Tech Stack

### Backend
- **Python** - Server implementation
- **gRPC** - RPC framework with Protocol Buffers
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
│   │   ├── api/           # REST API routes and schemas
│   │   ├── generated/     # Generated protobuf Python files
│   │   ├── services/      # gRPC service implementation
│   │   ├── config.py      # Application configuration
│   │   ├── database.py    # Database connection
│   │   └── models.py      # SQLAlchemy ORM models
│   ├── migrations/
│   │   └── init.sql       # Database schema and seed data
│   ├── protos/
│   │   └── library.proto  # Protocol Buffer definitions
│   ├── requirements.txt   # Python dependencies
│   ├── server.py          # gRPC server entry point
│   ├── rest_server.py     # REST API server entry point
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── app/           # Next.js pages (App Router)
│   │   ├── components/    # Reusable UI components
│   │   └── lib/           # API client and types
│   ├── package.json
│   └── Dockerfile
├── docker-compose.yml
├── setup_steps.txt        # Quick setup commands
└── README.md
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