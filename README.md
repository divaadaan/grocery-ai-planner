# Grocery AI Planner

AI-powered meal planning application that optimizes grocery shopping based on real-time store deals and user preferences.

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose
- Ollama running locally (for LLM integration)
- Python 3.11+ (for local development)

### 1. Setup Environment
```bash
# Clone the repository
git clone <your-repo-url>
cd grocery-ai-planner

# Copy environment template
cp .env.example .env

# Edit .env with your configuration
# Minimum required: DATABASE_URL, REDIS_URL, LLM_API_URL
```

### 2. Start Development Stack
```bash
# Start all services (database, redis, api, workers, monitoring)
docker-compose up -d

# View logs
docker-compose logs -f grocery-api

# Check health
curl http://localhost:8000/api/v1/health
```

### 3. Access Services
- **API Documentation**: http://localhost:8000/docs
- **Application**: http://localhost:8000
- **Prometheus**: http://localhost:9090
- **Grafana**: http://localhost:3000 (admin/admin)
- **Metrics**: http://localhost:8001/metrics

## 🏗️ Architecture

### Multi-Agent AI System (LangGraph)
- **Chef Agent**: Orchestrates meal planning process
- **Sous Chef Agents**: Create specialized recipes (breakfast, lunch, dinner)
- **Nutritionist Agent**: Validates nutritional requirements
- **Shopping Optimizer**: Optimizes store visits and costs

### Backend Stack
- **FastAPI**: Async web framework with automatic API docs
- **PostgreSQL**: Primary database for structured data
- **Redis**: Job queuing and caching
- **Celery**: Background task processing
- **OpenTelemetry**: Comprehensive observability

### Data Pipeline
1. **Store Discovery**: Find local grocery stores via postal code
2. **Deal Scraping**: Extract current offers and prices
3. **AI Meal Planning**: Generate optimized meal plans
4. **Shopping Optimization**: Minimize cost and store visits

## 📦 Project Structure

```
grocery-ai-planner/
├── backend/
│   ├── app.py                    # Main FastAPI application
│   ├── core/
│   │   ├── models/              # SQLAlchemy database models
│   │   ├── agents/              # LangGraph AI agents
│   │   ├── tools/               # Agent tools and utilities
│   │   ├── scraping/            # Store-specific scrapers
│   │   └── llm_client.py        # LLM integration
│   ├── api/routes/              # REST API endpoints
│   ├── tasks/                   # Celery background tasks
│   ├── telemetry/              # OpenTelemetry monitoring
│   └── worker.py               # Celery worker configuration
├── monitoring/                  # Prometheus & Grafana config
├── docker-compose.yml          # Complete development stack
└── .env.example                # Environment configuration template
```

## 🛠️ Development

### Local Development Setup
```bash
# Install Python dependencies
cd backend
pip install -r requirements.txt

# Run database migrations
alembic upgrade head

# Start FastAPI with hot reload
uvicorn app:app --reload --host 0.0.0.0 --port 8000

# Start Celery worker (separate terminal)
celery -A worker worker --loglevel=info

# Start Celery beat scheduler (separate terminal)
celery -A worker beat --loglevel=info
```

### Database Management
```bash
# Create new migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Reset database (development only)
docker-compose exec postgres psql -U postgres -d grocery_planner -c "DROP SCHEMA public CASCADE; CREATE SCHEMA public;"
```

### Testing Background Jobs
```bash
# Test store discovery
curl -X POST "http://localhost:8000/api/v1/stores/discover/M5V3A8"

# Test meal plan generation
curl -X POST "http://localhost:8000/api/v1/meal-plans/generate" \
  -H "Content-Type: application/json" \
  -d '{"user_id": 1, "week_start": "2024-01-15"}'
```

## 🔧 Configuration

### Environment Variables

#### Required
```bash
DATABASE_URL=postgresql://postgres:password@localhost:5432/grocery_planner
REDIS_URL=redis://localhost:6379/0
LLM_API_URL=http://host.docker.internal:11434/api/generate
DEFAULT_MODEL=qwen2.5-coder:14b
```

#### Optional External APIs
```bash
GOOGLE_MAPS_API_KEY=your_api_key_here    # For store discovery
MAIL_USERNAME=your_email@gmail.com       # For notifications
MAIL_PASSWORD=your_app_password          # Gmail app password
```

#### Development Settings
```bash
DEBUG=true                               # Enable debug mode
TELEMETRY_CONSOLE_EXPORT=true           # Log spans to console
LOG_LEVEL=DEBUG                          # Detailed logging
```

## 📊 Monitoring

### Telemetry Metrics
- **LLM Performance**: Request count, response time, token usage
- **Agent Execution**: Success rate, processing time, retry count
- **Scraping Jobs**: Success rate, offers found, error tracking
- **Meal Planning**: Generation time, cost optimization, user satisfaction

### Health Checks
```bash
# Application health
curl http://localhost:8000/api/v1/health

# Simple health (for load balancers)
curl http://localhost:8000/api/v1/health/simple

# Component status
curl http://localhost:8000/metrics-info
```

### Grafana Dashboards
Access Grafana at http://localhost:3000 (admin/admin) for:
- API performance metrics
- Database connection health
- Background job success rates
- LLM usage patterns
- Cost optimization trends

## 🤖 AI Agents

### Chef Agent (Orchestrator)
- Receives user requirements (budget, dietary needs, household size)
- Analyzes current deals and develops meal strategy
- Delegates recipe creation to specialized agents
- Makes final decisions on meal plan composition

### Sous Chef Agents (Specialists)
- **Breakfast Chef**: Morning meal optimization
- **Lunch Chef**: Midday meal planning
- **Dinner Chef**: Evening meal strategy
- Each receives ingredients and dietary requirements from Chef

### Nutritionist Agent (Validator)
- Reviews recipes for nutritional balance
- Flags dietary restriction violations
- Suggests ingredient swaps for better nutrition
- Validates daily/weekly nutritional targets

### Shopping Optimizer Agent
- Consolidates ingredients across meals
- Optimizes store routing for efficiency
- Calculates total costs and flags budget overruns
- Minimizes number of store visits

## 🗄️ Database Schema

### Core Models
- **Users**: Preferences, budget, dietary restrictions
- **Stores**: Location, scraping configuration, success rates
- **CurrentOffers**: Product deals, pricing, dates
- **MealPlans**: Generated plans, recipes, shopping lists
- **ScrapeJobs**: Background job tracking and results

### Key Relationships
- Users have multiple MealPlans
- Stores have many CurrentOffers
- MealPlans contain Recipes and ShoppingLists
- ScrapeJobs track store discovery and offer updates

## 🕷️ Web Scraping

### Store Discovery Pipeline
1. User enters postal code
2. Check database for existing store data
3. If no data: trigger background store discovery
4. Use Google Maps API to find local stores
5. Attempt to locate flyer/deals webpages
6. Configure scraping rules per store format
7. Email user when data ready (~30-60 minutes)

### Adaptive Scraping Strategy
- **Primary**: Beautiful Soup with rate limiting
- **Fallback 1**: Selenium for JavaScript-heavy sites
- **Fallback 2**: OCR on PDF flyers
- **Fallback 3**: Vision agents for complex layouts

### Compliance & Ethics
- Respects robots.txt files
- Implements rate limiting and delays
- Graceful failure handling with retry logic
- User notifications for failed scrapes

## 🎯 User Flow

### First-Time User
1. **Registration**: Enter postal code, preferences, budget
2. **Data Check**: System checks if grocery data exists for area
3. **Data Collection**: Background scraping with progress updates (if needed)
4. **Meal Planning**: User requests meal plan → AI agents collaborate
5. **Plan Delivery**: Optimized meal plan with shopping list by store

### Returning User
1. **Quick Planning**: Instant meal plan generation using cached store data
2. **Plan Customization**: Modify preferences, budget, or dietary restrictions
3. **Shopping Optimization**: Get updated prices and store recommendations
4. **Feedback Loop**: Rate meal plans to improve future recommendations

## 🚀 Deployment

### Development
```bash
# Start complete stack
docker-compose up -d

# Scale workers for load testing
docker-compose up -d --scale celery-worker=3
```

### Production Considerations
- Use managed PostgreSQL (AWS RDS, Google Cloud SQL)
- Redis Cluster for high availability
- Container orchestration (Kubernetes, Docker Swarm)
- Load balancer for API instances
- Separate monitoring stack

## 🛡️ Security

### Authentication (To Be Implemented)
- JWT tokens for API authentication
- Email verification for new accounts
- Rate limiting for API endpoints
- Input validation and sanitization

### Data Protection
- Encrypted database connections
- Secure handling of personal preferences
- No storage of payment information
- Privacy-compliant data retention

## 🧪 Testing

### Manual Testing
```bash
# Test user creation
curl -X POST "http://localhost:8000/api/v1/users/" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "postal_code": "M5V3A8",
    "budget": 150.0,
    "household_size": 2
  }'

# Test store discovery
curl -X POST "http://localhost:8000/api/v1/stores/discover/M5V3A8"

# Monitor job progress
curl "http://localhost:8000/api/v1/scraping/jobs/1"
```

## 📈 Performance Optimization

### Database
- Indexed queries for postal code lookups
- Efficient offer filtering by date and store
- Connection pooling for concurrent requests

### Caching Strategy
- Redis caching for frequent store lookups
- Meal plan template caching
- Rate-limited API response caching

### Background Processing
- Celery queues for different task priorities
- Retry logic with exponential backoff
- Job result storage for status tracking

## 🔮 Future Enhancements

### Phase 2 Features
- Mobile application (React Native)
- Recipe difficulty scoring
- Seasonal ingredient preferences
- Integration with grocery delivery services

### Advanced AI Features
- Computer vision for flyer analysis
- Natural language meal requests
- Nutritional trend analysis
- Predictive pricing models

### Platform Expansion
- Multi-city deployment
- Partnership with grocery chains
- B2B meal planning for offices
- Integration with fitness tracking apps

## 🆘 Troubleshooting

### Common Issues

**Database Connection Failed**
```bash
# Check if PostgreSQL is running
docker-compose ps postgres

# View database logs
docker-compose logs postgres

# Reset database
docker-compose down -v && docker-compose up -d
```

**Celery Worker Not Processing Jobs**
```bash
# Check worker status
docker-compose logs celery-worker

# Restart workers
docker-compose restart celery-worker celery-beat
```

**LLM Connection Issues**
```bash
# Verify Ollama is running
curl http://localhost:11434/api/tags

# Test LLM endpoint
curl -X POST http://localhost:11434/api/generate \
  -d '{"model": "qwen2.5-coder:14b", "prompt": "Hello"}'
```

**Telemetry Not Working**
```bash
# Check OpenTelemetry installation
pip list | grep opentelemetry

# Verify metrics endpoint
curl http://localhost:8001/metrics
```

## 🎉 Day 1 Morning Tasks - COMPLETED ✅

This boilerplate includes everything needed for Day 1 Morning:

1. ✅ **Project Repository Structure** - Complete directory layout
2. ✅ **Docker Compose Setup** - PostgreSQL + Redis + Full stack
3. ✅ **Database Schema** - All SQLAlchemy models implemented
4. ✅ **FastAPI Application** - Main app with health checks
5. ✅ **Environment Configuration** - Complete settings management
6. ✅ **Telemetry Integration** - Full OpenTelemetry setup
7. ✅ **Background Jobs** - Celery workers and task structure
8. ✅ **API Routes** - Basic endpoint structure ready

### Next Steps (Day 1 Afternoon)
1. Test database connectivity and basic CRUD operations
2. Implement postal code input validation
3. Set up first background job triggers
4. Move to Day 2: Store discovery and scraping implementation

### Quick Test Commands
```bash
# 1. Start the stack
cd grocery-ai-planner
cp .env.example .env
# Edit LLM_API_URL in .env for your Ollama instance
docker-compose up -d

# 2. Test health
curl http://localhost:8000/api/v1/health

# 3. Test user creation
curl -X POST "http://localhost:8000/api/v1/users/" \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "postal_code": "M5V3A8", "budget": 150.0, "household_size": 2}'

# 4. View API docs
open http://localhost:8000/docs
```

The foundation is solid and ready for building your grocery AI meal planner! 🚀

---

## 🆕 RECENT UPDATE: New Scraping Architecture

**Major Change**: The scraping system has been completely redesigned!

### What Changed?
- **Removed Beautiful Soup** - Ineffective for modern JavaScript sites
- **Added Flipp API integration** - Primary data source for Canadian grocery stores
- **Selenium-first fallbacks** - Better handling of dynamic content
- **Intelligent orchestration** - Automatic method selection and retry logic

### New Scraping Endpoints
```bash
# Test all scraping methods
curl -X POST http://localhost:8000/api/v1/scraping/test

# Smart postal code scraping with Flipp integration
curl -X POST http://localhost:8000/api/v1/scraping/postal-code \
  -H "Content-Type: application/json" \
  -d '{"postal_code": "M5V 3A8"}'

# View results
curl http://localhost:8000/api/v1/scraping/postal-codes/M5V%203A8/stores
```

### Benefits
- **90% less scraping complexity** - One API covers hundreds of stores
- **Better data quality** - Official retailer partnerships via Flipp
- **Faster development** - Focus on AI agents instead of web scraping
- **Nationwide coverage** - All major Canadian grocery chains included

**For complete details, see `SCRAPING_UPDATE.md`**

This update significantly improves the reliability and coverage of the grocery data collection system! 🎆