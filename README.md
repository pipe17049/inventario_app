# Inventory Management System

A modern Django-based inventory management system with real-time WebSocket notifications, MongoDB integration, and a responsive frontend.

## Features

- **RESTful API** with Django REST Framework
- **Real-time notifications** via independent WebSocket server
- **MongoDB** database with MongoEngine ODM
- **In-memory caching** for improved performance
- **Responsive frontend** with Bootstrap 5
- **Docker containerization** with Docker Compose
- **Comprehensive testing** with pytest
- **CI/CD pipeline** with GitHub Actions
- **Security scanning** with safety and bandit

## API Endpoints

### Items Management
- `GET /api/items/` - List all items (cached)
- `POST /api/items/` - Create new item
- `GET /api/items/{id}/` - Get item details (cached)
- `PUT /api/items/{id}/` - Update item
- `DELETE /api/items/{id}/` - Delete item (triggers WebSocket notification)

### Health Check
- `GET /api/health/` - API health status

## WebSocket Events

The system sends real-time notifications for:
- Item creation
- Item updates
- Item deletion

Connect to: `ws://localhost:8001/`

## Tech Stack

### Backend
- Django 5.1.5
- Django REST Framework 3.15.2
- Independent WebSocket Server (websockets library)
- MongoEngine 0.29.1 (MongoDB ODM)

### Frontend
- HTML5 + CSS3 + JavaScript (ES6+)
- Bootstrap 5.1.3
- Font Awesome 6.0.0
- Native WebSocket API
- Python HTTP Server (for static files)

### Infrastructure
- MongoDB 7.0
- Docker & Docker Compose

## Quick Start

### Prerequisites
- Docker and Docker Compose
- Git

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd WebAvanzadoII
   ```

2. **Start all services**
   ```bash
   docker-compose up --build
   ```

3. **Access the application**
   - Frontend: http://localhost:3000
   - API: http://localhost:8000/api/
   - WebSocket: ws://localhost:8001
   - Admin: http://localhost:8000/admin/

The application will automatically:
- Set up MongoDB with authentication
- Run Django migrations
- Start the Django API server
- Start the WebSocket server
- Start the frontend HTTP server

### Development Setup

1. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configurations
   ```

4. **Start services manually**
   ```bash
   # Start MongoDB (or use Docker)
   docker-compose up mongodb -d
   
   # Run Django development server
   python manage.py runserver &
   
   # Run WebSocket server
   python websocket_server.py &
   
   # Run frontend server
   cd frontend && python -m http.server 3000
   ```

   Or use the convenience scripts:
   ```bash
   # Linux/Mac
   ./start-dev.sh
   
   # Windows
   start-dev.bat
   ```

## Testing

### Run all tests
```bash
# Using Docker
docker-compose exec web python manage.py test

# Local development
python manage.py test
```

### Run with coverage
```bash
# Using pytest with coverage
coverage run --source='.' manage.py test
coverage report --show-missing
coverage html  # Generate HTML report
```

### Test specific modules
```bash
python manage.py test inventory.tests.ItemModelTest
python manage.py test inventory.tests.ItemAPITest
```

## API Usage Examples

### Create an item
```bash
curl -X POST http://localhost:8000/api/items/ \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Laptop",
    "description": "Dell XPS 13",
    "quantity": 5,
    "price": 999.99,
    "category": "Electronics"
  }'
```

### Get all items
```bash
curl http://localhost:8000/api/items/
```

### Update an item
```bash
curl -X PUT http://localhost:8000/api/items/{item_id}/ \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Updated Laptop",
    "quantity": 3,
    "price": 899.99
  }'
```

### Delete an item
```bash
curl -X DELETE http://localhost:8000/api/items/{item_id}/
```

## WebSocket Integration

### JavaScript Example
```javascript
const socket = new WebSocket('ws://localhost:8001/');

socket.onmessage = function(event) {
    const data = JSON.parse(event.data);
    console.log('Received:', data);
    
    switch(data.type) {
        case 'item_created':
            console.log('New item:', data.data);
            break;
        case 'item_deleted':
            console.log('Item deleted:', data.data.message);
            break;
    }
};
```

## Deployment

### Production Environment Variables
```bash
DEBUG=False
SECRET_KEY=your-super-secret-key
MONGODB_HOST=your-mongodb-host
MONGODB_USERNAME=your-mongodb-user
MONGODB_PASSWORD=your-mongodb-password
ALLOWED_HOSTS=your-domain.com,www.your-domain.com
```

### Docker Production
```bash
# Build and deploy
docker-compose -f docker-compose.prod.yml up --build -d

# Scale services
docker-compose -f docker-compose.prod.yml up --scale web=3 -d
```

## Monitoring and Logging

### View logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f web
docker-compose logs -f mongodb
```

### Health checks
```bash
# API health
curl http://localhost:8000/api/health/

# MongoDB status
docker-compose exec mongodb mongosh --eval "db.adminCommand('ping')"
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add tests for new functionality
5. Run the test suite (`python manage.py test`)
6. Commit your changes (`git commit -m 'Add amazing feature'`)
7. Push to the branch (`git push origin feature/amazing-feature`)
8. Open a Pull Request

### Code Quality

The project uses:
- **flake8** for linting
- **black** for code formatting
- **coverage** for test coverage
- **safety** for security scanning
- **bandit** for security analysis

```bash
# Run quality checks
flake8 .
coverage run --source='.' manage.py test
safety check
bandit -r .
```

## Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│     Frontend    │    │      Django     │    │     MongoDB     │
│   (Bootstrap)   │◄──►│   REST API      │◄──►│   (MongoEngine) │
│                 │    │    (Port 8000)  │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       
         │                       │                       
         │                       │               
         │                       │               
         │                       │               
         │                       │                       
         │                       │                       
         └──────────────►┌─────────────────┐               
           WebSocket     │   WebSocket     │               
           (Port 8001)   │    Server       │               
                        │ (asyncio.Queue) │               
                        └─────────────────┘               
```               
```

## Performance

- **Caching**: All GET requests are cached in memory (15-minute TTL)
- **Database**: MongoDB with proper indexing on frequently queried fields
- **WebSockets**: Efficient real-time communication without polling
- **Static Files**: Served by Nginx in production

## Security Features

- Input validation and sanitization
- CORS protection
- Environment-based configuration
- Security headers
- Automated vulnerability scanning
- No sensitive data in version control

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

For support, please open an issue in the GitHub repository or contact the development team.

---

**Happy Coding!** 🚀
