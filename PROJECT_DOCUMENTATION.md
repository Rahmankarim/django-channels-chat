# Django Channels Real-Time Chat Application - Complete Documentation

## 📋 Table of Contents
- [Project Overview](#project-overview)
- [Architecture & Technology Stack](#architecture--technology-stack)
- [Features](#features)
- [Docker Implementation](#docker-implementation)
- [CI/CD Pipeline](#cicd-pipeline)
- [Project Structure](#project-structure)
- [Setup & Installation](#setup--installation)
- [Usage Guide](#usage-guide)
- [Testing](#testing)
- [Deployment](#deployment)
- [Best Practices](#best-practices)

---

## 🎯 Project Overview

### What is This Project?
This is a **real-time chat application** built with Django Channels that enables multiple users to communicate instantly through WebSocket connections. It demonstrates modern web development practices including:
- Real-time bidirectional communication using WebSockets
- Asynchronous message handling
- Scalable architecture with Redis as a channel layer
- Containerized deployment with Docker
- Automated CI/CD pipeline with GitHub Actions

### Key Capabilities
- **Multi-room chat**: Users can join different chat rooms by room name
- **Real-time messaging**: Messages appear instantly without page refresh
- **Scalable**: Can handle multiple concurrent connections
- **Production-ready**: Includes proper containerization, security, and deployment automation

---

## 🏗️ Architecture & Technology Stack

### Backend Framework
- **Django 4.2.25**: Web framework for Python
- **Django Channels 4.3.1**: Extends Django to handle WebSockets and async protocols
- **Daphne 4.2.1**: ASGI server that runs the Django Channels application

### Real-Time Communication
- **WebSockets**: Protocol for full-duplex communication channels
- **ASGI (Asynchronous Server Gateway Interface)**: Successor to WSGI for async Python web servers

### Data Layer
- **PostgreSQL 14**: Primary relational database for storing application data
- **Redis 6**: In-memory data store used as a channel layer for message routing between WebSocket connections

### Containerization & Orchestration
- **Docker**: Containerization platform
- **Docker Compose**: Multi-container orchestration
- **Multi-stage builds**: Optimized Docker images with separate build and runtime stages

### CI/CD & DevOps
- **GitHub Actions**: Automated testing and deployment pipeline
- **Docker Hub**: Container registry for storing built images
- **Automated testing**: Flake8, Bandit, and unit tests

---

## ✨ Features

### 1. Real-Time Chat Functionality
```python
# WebSocket Consumer (chat/consumers.py)
class ChatConsumer(AsyncWebsocketConsumer):
    - Handles WebSocket connections asynchronously
    - Manages chat room groups
    - Broadcasts messages to all room participants
```

**How it works:**
1. User connects to a WebSocket endpoint (e.g., `/ws/chat/room-name/`)
2. Connection is added to a room group in Redis
3. When a message is sent, it's broadcast to all connections in that group
4. All users in the room receive the message instantly

### 2. Multiple Chat Rooms
- Users can create/join rooms by accessing: `http://localhost:8000/chat/room-name/`
- Each room is isolated - messages only go to users in the same room
- Room names are URL parameters, making it easy to share room links

### 3. Asynchronous Message Processing
- Uses Python's `async/await` for efficient handling of concurrent connections
- Non-blocking I/O allows handling thousands of simultaneous connections
- Redis channel layer ensures messages are delivered even across multiple server instances

---

## 🐳 Docker Implementation

### What Docker Does in This Project

#### 1. **Multi-Stage Dockerfile** (`Dockerfile`)

**Stage 1: Builder Stage**
```dockerfile
FROM python:3.9-slim as builder
```
- **Purpose**: Compile and build Python packages
- **What it does**:
  - Installs build tools (gcc, build-essential, libpq-dev)
  - Compiles Python dependencies
  - Creates wheel files for faster installation
- **Why separate**: Build tools are large and not needed at runtime

**Stage 2: Runtime Stage**
```dockerfile
FROM python:3.9-slim
```
- **Purpose**: Create minimal production image
- **What it does**:
  - Uses only runtime dependencies (libpq5, curl)
  - Copies pre-built wheels from builder stage
  - Creates non-root user for security
  - Sets up health checks
- **Benefits**: 
  - Smaller image size (~200MB vs ~800MB)
  - Faster deployment
  - Better security (fewer attack surfaces)

#### 2. **Docker Compose Setup** (`docker-compose.yml`)

**Service: Web Application**
```yaml
web:
  build: .
  ports: "8000:8000"
  depends_on: [db, redis]
```
- **What it does**:
  - Builds and runs the Django Channels application
  - Exposes port 8000 for external access
  - Waits for database and Redis to be healthy before starting
  - Runs migrations and collects static files on startup
  - Starts Daphne ASGI server

**Service: PostgreSQL Database**
```yaml
db:
  image: postgres:14
  volumes: channels_db_data:/var/lib/postgresql/data
```
- **What it does**:
  - Runs PostgreSQL 14 database server
  - Persists data in a Docker volume (survives container restarts)
  - Health check ensures database is ready before app starts
  - Environment variables configure database credentials

**Service: Redis**
```yaml
redis:
  image: redis:latest
  ports: "6379:6379"
```
- **What it does**:
  - Runs Redis server for channel layer
  - Acts as message broker for WebSocket connections
  - Enables horizontal scaling (multiple app instances can share Redis)
  - Health check verifies Redis is responding

#### 3. **Container Networking**
- All services run on the same Docker network
- Services communicate using service names as hostnames:
  - App connects to database: `POSTGRES_HOST=db`
  - App connects to Redis: `REDIS_HOST=redis`
- Only port 8000 is exposed to the host machine

#### 4. **Entry Point Script** (`docker-entrypoint.sh`)
```bash
#!/bin/bash
python canal/manage.py collectstatic --noinput  # Gather CSS/JS files
python canal/manage.py migrate --noinput        # Update database schema
exec daphne -b 0.0.0.0 -p 8000 canal.asgi:application  # Start server
```
- **Purpose**: Automate startup tasks
- **What it does**:
  - Collects static files (CSS, JavaScript) for serving
  - Applies database migrations automatically
  - Starts the Daphne ASGI server to handle WebSocket connections

#### 5. **Docker Benefits in This Project**

**Development Benefits:**
- **Consistency**: Same environment on all developer machines
- **Quick setup**: `docker-compose up` starts everything
- **Isolation**: Dependencies don't conflict with system packages
- **Easy testing**: Spin up clean environments instantly

**Production Benefits:**
- **Reproducibility**: Exact same image from dev to production
- **Scalability**: Easy to run multiple instances behind a load balancer
- **Portability**: Runs anywhere Docker runs (AWS, Azure, GCP, on-premise)
- **Security**: Non-root user, minimal dependencies, isolated environment

---

## 🔄 CI/CD Pipeline

### GitHub Actions Workflow (`.github/workflows/ci-cd.yml`)

The CI/CD pipeline automates the entire process from code commit to production deployment.

#### **Pipeline Stages**

### **Stage 1: Build & Install** (`build-install` job)
```yaml
- Set up Python 3.9
- Cache pip dependencies
- Install development requirements
```
**Purpose**: Prepare Python environment and dependencies  
**What it does**:
- Installs Python 3.9
- Caches pip packages to speed up future builds
- Installs all project dependencies from `requirements/development.txt`
- Creates a cache key based on requirements file hash

**Benefits**:
- Faster subsequent builds (cache hit)
- Validates that all dependencies install correctly
- Provides base for subsequent jobs

---

### **Stage 2: Lint & Security** (`lint-and-security` job)
```yaml
- Run flake8 (code quality)
- Run bandit (security scan)
- Run safety check (dependency vulnerabilities)
```
**Purpose**: Ensure code quality and security  
**What it does**:

1. **Flake8 Linting**:
   - Checks Python code style (PEP 8 compliance)
   - Finds syntax errors and undefined names
   - Configured to ignore specific warnings: `F401,F403,F405,E402`
   - Max line length: 100 characters

2. **Bandit Security Scanning**:
   - Scans code for common security issues
   - Detects hardcoded passwords, SQL injection risks, etc.
   - Severity level: medium-high (`-ll` flag)

3. **Safety Dependency Check**:
   - Checks dependencies for known vulnerabilities
   - Uses database of CVEs (Common Vulnerabilities and Exposures)
   - Fails build if critical vulnerabilities found

**Benefits**:
- Prevents insecure code from reaching production
- Maintains consistent code style across team
- Early detection of security issues

---

### **Stage 3: Automated Testing** (`test` job)
```yaml
services:
  postgres: { image: postgres:12, ports: [5432] }
  redis: { image: redis:6, ports: [6379] }
steps:
  - Run database migrations
  - Execute test suite
```
**Purpose**: Validate application functionality  
**What it does**:

1. **Spins up test infrastructure**:
   - PostgreSQL 12 database container
   - Redis 6 container
   - Health checks ensure services are ready

2. **Runs database migrations**:
   - Creates all required database tables
   - Applies schema changes
   - Validates migration files

3. **Executes test suite**:
   - Runs all Django unit tests
   - Tests views, models, consumers
   - Validates WebSocket functionality

**Environment Variables**:
```yaml
POSTGRES_HOST: 127.0.0.1
POSTGRES_PORT: 5432
REDIS_HOST: 127.0.0.1
REDIS_PORT: 6379
```

**Benefits**:
- Catches bugs before deployment
- Ensures database compatibility
- Validates WebSocket functionality
- Prevents breaking changes

---

### **Stage 4: Docker Build & Push** (`docker-build-push` job)
```yaml
- Set up Docker Buildx
- Login to Docker Hub
- Build and push Docker image
```
**Purpose**: Create production-ready container image  
**What it does**:

1. **Docker Buildx Setup**:
   - Enables advanced Docker features
   - Multi-platform builds (if needed)
   - BuildKit caching for faster builds

2. **Docker Hub Authentication**:
   ```yaml
   username: prograhmankarim
   password: ${{ secrets.DOCKERHUB_TOKEN }}
   ```
   - Securely logs into Docker Hub
   - Uses GitHub Secrets for credentials
   - Token has Read/Write/Delete permissions

3. **Image Building**:
   - Builds multi-stage Dockerfile
   - Creates optimized production image
   - Tags image with:
     - Commit SHA: `prograhmankarim/django-channels-chat:a67da2a`
     - Latest tag: `prograhmankarim/django-channels-chat:latest`

4. **Layer Caching**:
   ```yaml
   cache-from: type=registry,ref=...:latest
   cache-to: type=inline
   ```
   - Pulls previous image for layer cache
   - Speeds up builds by reusing unchanged layers
   - Inline cache embedded in image

**Benefits**:
- Fast builds with layer caching
- Versioned images (can rollback to any commit)
- Automated image publishing
- No manual build/push required

---

### **Stage 5: Deployment** (`deploy` job)
```yaml
- Deploy application
- Health checks
- Rollback on failure
```
**Purpose**: Deploy to production environment  
**Current Setup**: Placeholder for deployment scripts  
**What it can do** (when configured):

**Deployment Options**:
1. **Platform-as-a-Service (PaaS)**:
   ```bash
   # Example for Heroku
   heroku container:push web -a your-app
   heroku container:release web -a your-app
   ```

2. **Kubernetes**:
   ```bash
   kubectl set image deployment/chat-app chat-app=prograhmankarim/django-channels-chat:${{ github.sha }}
   kubectl rollout status deployment/chat-app
   ```

3. **Docker Swarm**:
   ```bash
   docker service update --image prograhmankarim/django-channels-chat:latest chat-app
   ```

4. **Cloud Platforms**:
   - **AWS ECS**: Update task definition with new image
   - **Google Cloud Run**: Deploy container revision
   - **Azure Container Instances**: Update container group

**Deployment Steps** (typical):
1. Pull latest Docker image
2. Stop old containers gracefully
3. Start new containers
4. Run health checks
5. Route traffic to new version
6. Keep old version for rollback

---

### **Pipeline Triggers**

**Push Events**:
```yaml
on:
  push:
    branches: [main, develop, feature/**, release/**]
```
- Runs on every push to specified branches
- Validates all code changes
- Builds Docker images for all branches

**Pull Request Events**:
```yaml
on:
  pull_request:
    branches: [main, develop]
```
- Runs when PR is opened/updated
- Provides feedback before merging
- Prevents broken code from reaching main branches

---

### **Environment Variables & Secrets**

**Environment Variables** (defined in workflow):
```yaml
env:
  DOCKER_IMAGE: prograhmankarim/django-channels-chat
  DOCKER_TAG: ${{ github.sha }}
  POSTGRES_DB: postgres
  POSTGRES_USER: postgres
  POSTGRES_PASSWORD: postgres
```

**GitHub Secrets** (configured in repository):
- `DOCKERHUB_TOKEN`: Personal access token for Docker Hub
  - Created at: https://hub.docker.com/settings/security
  - Permissions: Read, Write, Delete
  - Stored in: Repository Settings → Secrets → Actions

**Benefits**:
- Credentials never exposed in code
- Easy to rotate tokens
- Different secrets per environment

---

### **CI/CD Pipeline Benefits**

**For Developers**:
- ✅ Instant feedback on code quality
- ✅ Automated testing (no manual QA needed)
- ✅ Consistent build process
- ✅ Easy rollbacks to previous versions

**For Operations**:
- ✅ Zero-downtime deployments
- ✅ Automated security scanning
- ✅ Reproducible builds
- ✅ Audit trail of all deployments

**For Business**:
- ✅ Faster time to market
- ✅ Reduced deployment errors
- ✅ Improved code quality
- ✅ Better security posture

---

### **Pipeline Execution Flow**

```
┌─────────────────┐
│  Code Push      │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Build & Install │ (Install dependencies, cache pip)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Lint & Security │ (Flake8, Bandit, Safety checks)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Run Tests       │ (Unit tests with PostgreSQL & Redis)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Docker Build    │ (Build image, push to Docker Hub)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Deploy          │ (Deploy to production environment)
└─────────────────┘
```

**Total Pipeline Time**: ~5-10 minutes
- Build & Install: 1-2 minutes
- Lint & Security: 30 seconds
- Tests: 2-3 minutes
- Docker Build: 2-5 minutes
- Deploy: 1-2 minutes

---

## 📁 Project Structure

```
django-channels-chat/
├── .github/
│   └── workflows/
│       └── ci-cd.yml              # GitHub Actions CI/CD pipeline
├── canal/                          # Main Django project
│   ├── canal/                      # Project settings
│   │   ├── __init__.py
│   │   ├── asgi.py                # ASGI configuration for Channels
│   │   ├── channel_layers.py     # Redis channel layer config
│   │   ├── databases.py          # Database configuration
│   │   ├── routing.py            # WebSocket URL routing
│   │   ├── settings.py           # Django settings
│   │   ├── urls.py               # HTTP URL routing
│   │   └── wsgi.py               # WSGI config (not used with Channels)
│   ├── chat/                      # Chat application
│   │   ├── consumers.py          # WebSocket consumer (handles chat logic)
│   │   ├── routing.py            # WebSocket routes for chat
│   │   ├── urls.py               # HTTP routes for chat views
│   │   ├── views.py              # HTTP views (chat room pages)
│   │   ├── models.py             # Database models (if any)
│   │   ├── admin.py              # Django admin configuration
│   │   ├── templates/
│   │   │   └── chat/
│   │   │       ├── index.html    # Chat room list/home page
│   │   │       └── room.html     # Individual chat room
│   │   └── tests/
│   │       └── test_views.py     # Unit tests
│   ├── static/                    # Static files (CSS, JS, images)
│   └── manage.py                  # Django management script
├── requirements/
│   ├── live.txt                   # Production dependencies
│   └── development.txt            # Development + testing dependencies
├── docker-compose.yml             # Multi-container orchestration
├── Dockerfile                     # Container build instructions
├── docker-entrypoint.sh          # Container startup script
├── Makefile                       # Development shortcuts
└── README.md                      # Basic project documentation
```

### Key Files Explained

**ASGI Configuration** (`canal/asgi.py`):
- Entry point for ASGI servers (Daphne)
- Routes HTTP and WebSocket requests
- Configures middleware and authentication

**Channel Layers** (`canal/channel_layers.py`):
- Configures Redis as message broker
- Enables communication between WebSocket connections
- Required for multi-instance deployment

**WebSocket Consumer** (`chat/consumers.py`):
- Handles WebSocket lifecycle (connect, receive, disconnect)
- Manages chat room groups
- Broadcasts messages to room participants

**WebSocket Routing** (`chat/routing.py`):
- Maps WebSocket URLs to consumers
- Similar to Django's URL routing but for WebSockets

---

## 🚀 Setup & Installation

### Prerequisites
- Python 3.9+
- Docker & Docker Compose
- Git

### Option 1: Docker Compose (Recommended)

1. **Clone the repository**:
   ```bash
   git clone https://github.com/Rahmankarim/django-channels-chat.git
   cd django-channels-chat
   ```

2. **Start all services**:
   ```bash
   docker-compose up --build
   ```
   This will:
   - Build the Django application image
   - Start PostgreSQL database
   - Start Redis server
   - Run migrations
   - Start the application on port 8000

3. **Access the application**:
   - Open browser: http://localhost:8000/chat/
   - Create a room: http://localhost:8000/chat/room-name/

### Option 2: Local Development

1. **Install PostgreSQL and Redis**:
   ```bash
   # Ubuntu/Debian
   sudo apt-get install postgresql redis-server
   
   # macOS
   brew install postgresql redis
   ```

2. **Create virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements/development.txt
   ```

4. **Configure database**:
   ```bash
   # Edit canal/canal/databases.py if needed
   # Default: PostgreSQL on localhost:5432
   ```

5. **Run migrations**:
   ```bash
   python canal/manage.py migrate
   ```

6. **Start development server**:
   ```bash
   python canal/manage.py runserver
   ```

---

## 📖 Usage Guide

### Creating and Joining Chat Rooms

1. **Access the chat home page**:
   ```
   http://localhost:8000/chat/
   ```

2. **Join/create a room by entering a room name**:
   ```
   http://localhost:8000/chat/your-room-name/
   ```

3. **Open the same URL in multiple browser tabs/windows**:
   - Messages sent in one window appear instantly in all others
   - Each room is isolated - messages only visible to users in that room

### How It Works

1. **WebSocket Connection**:
   ```javascript
   // Frontend establishes WebSocket connection
   const chatSocket = new WebSocket('ws://localhost:8000/ws/chat/room-name/');
   ```

2. **Sending Messages**:
   ```javascript
   chatSocket.send(JSON.stringify({
       'message': 'Hello, everyone!'
   }));
   ```

3. **Receiving Messages**:
   ```javascript
   chatSocket.onmessage = function(e) {
       const data = JSON.parse(e.data);
       // Display message in chat interface
   };
   ```

4. **Backend Processing**:
   ```python
   # Consumer receives message
   async def receive(self, text_data):
       # Broadcast to all users in room
       await self.channel_layer.group_send(
           self.room_group_name,
           {'type': 'chat_message', 'message': message}
       )
   ```

---

## 🧪 Testing

### Run All Tests
```bash
# Using Docker Compose
docker-compose exec web python canal/manage.py test

# Local development
python canal/manage.py test

# Using Makefile
make test
```

### Test Coverage
- Unit tests for views
- WebSocket consumer tests
- Integration tests with database
- Security tests (Bandit)
- Code quality tests (Flake8)

### Continuous Testing
Tests run automatically on every:
- Git push
- Pull request
- CI/CD pipeline execution

---

## 🌐 Deployment

### Docker Hub Image
Pre-built images available at:
```
docker pull prograhmankarim/django-channels-chat:latest
```

### Environment Variables (Production)
```bash
# Database
POSTGRES_DB=your_db_name
POSTGRES_USER=your_db_user
POSTGRES_PASSWORD=secure_password
POSTGRES_HOST=db_hostname
POSTGRES_PORT=5432

# Redis
REDIS_HOST=redis_hostname
REDIS_PORT=6379

# Django
DJANGO_SECRET_KEY=your_secret_key
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
```

### Production Checklist
- [ ] Set `DEBUG=False` in settings
- [ ] Configure proper `ALLOWED_HOSTS`
- [ ] Use strong `SECRET_KEY`
- [ ] Set up HTTPS/TLS
- [ ] Configure production database
- [ ] Set up Redis with persistence
- [ ] Configure static files serving (CDN)
- [ ] Set up monitoring and logging
- [ ] Configure backup strategy
- [ ] Implement rate limiting
- [ ] Set up load balancer (if scaling horizontally)

---

## 🔒 Best Practices

### Security
- Non-root user in Docker containers
- No hardcoded credentials
- Security scanning in CI/CD (Bandit, Safety)
- Regular dependency updates
- HTTPS in production
- CORS configuration
- WebSocket authentication (implement as needed)

### Performance
- Multi-stage Docker builds (smaller images)
- Redis for channel layer (fast message routing)
- Static file optimization
- Database connection pooling
- Async/await for WebSocket handling

### Scalability
- Stateless application design
- Redis as shared state store
- Horizontal scaling ready
- Load balancer compatible
- Health checks configured

### Development
- Version control (Git)
- Code linting (Flake8)
- Automated testing
- CI/CD pipeline
- Documentation
- Environment-specific configurations

---

## 📊 Monitoring & Logging

### Health Checks
```bash
# Application health
curl http://localhost:8000/chat/

# Database health
docker-compose exec db pg_isready

# Redis health
docker-compose exec redis redis-cli ping
```

### Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f web
docker-compose logs -f db
docker-compose logs -f redis
```

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Commit changes: `git commit -m 'Add some feature'`
4. Push to branch: `git push origin feature/your-feature`
5. Open a Pull Request

---

## 📝 License

This project is licensed under the MIT License.

---

## 🆘 Troubleshooting

### Common Issues

**WebSocket connection fails**:
- Check Redis is running: `docker-compose ps redis`
- Verify Redis connection in settings
- Check browser console for errors

**Database connection errors**:
- Ensure PostgreSQL is running: `docker-compose ps db`
- Verify database credentials
- Check migrations are applied

**Docker build fails**:
- Clear Docker cache: `docker-compose build --no-cache`
- Check disk space: `docker system df`
- Verify Dockerfile syntax

**CI/CD pipeline fails**:
- Check GitHub Actions logs
- Verify secrets are configured
- Test locally before pushing

---

## 📚 Additional Resources

- [Django Channels Documentation](https://channels.readthedocs.io/)
- [Docker Documentation](https://docs.docker.com/)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [WebSocket Protocol](https://developer.mozilla.org/en-US/docs/Web/API/WebSockets_API)
- [Redis Documentation](https://redis.io/documentation)

---

**Project Maintained By**: Rahman Karim  
**GitHub**: https://github.com/Rahmankarim/django-channels-chat  
**Docker Hub**: https://hub.docker.com/r/prograhmankarim/django-channels-chat
