# Pastebin Service

A monolithic implementation of a Pastebin service that allows users to create, share, and manage text snippets with optional expiration times.

## Features

- Create pastes with optional expiration times
- View pastes via unique URLs
- Track page views and monthly statistics
- Automatic cleanup of expired pastes
- Copy paste contents to clipboard
- Responsive web interface
- Pre-populated database with sample data

## Requirements

### Local Development
- Python 3.8+
- MySQL Server
- pip (Python package manager)

### Docker Deployment
- Docker
- Docker Compose

## Setup

### Local Development

1. Create a MySQL database and initialize it:
```sql
mysql -u root -p < init.sql
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure environment variables:
- Copy `.env.example` to `.env`
- Update the `DATABASE_URL` with your MySQL credentials
- Generate a new `SECRET_KEY`

4. Initialize the database:
```bash
python app.py
```

### Docker Deployment

1. Build and start the containers:
```bash
docker-compose up -d
```

This will:
- Build the Flask application container
- Start a MySQL container
- Initialize the database with schema and sample data
- Create a persistent volume for MySQL data
- Set up the network between containers

2. Access the application at `http://localhost:5000`

The database comes pre-populated with:
- Sample pastes with different expiration settings
- Sample analytics data for the current and previous month

To stop the containers:
```bash
docker-compose down
```

To view logs:
```bash
docker-compose logs -f
```

## Running the Application

### Local Development
1. Start the application:
```bash
python app.py
```

2. Access the application at `http://localhost:5000`

## Architecture

The application follows a monolithic architecture with the following components:

- Flask web framework for handling HTTP requests
- SQLAlchemy ORM for database operations
- APScheduler for automated cleanup tasks
- Bootstrap for responsive UI
- MySQL for data persistence

## Database Schema

### Paste Table
- id (String): Primary key, URL-safe unique identifier
- content (Text): The paste content
- created_at (DateTime): Creation timestamp
- expires_at (DateTime, nullable): Expiration timestamp
- views (Integer): View counter
- Indexes on expires_at and created_at for better performance

### Analytics Table
- id (Integer): Primary key
- month (Date): Month for which statistics are collected
- total_views (Integer): Total page views for the month
- total_pastes (Integer): Total pastes created in the month
- Unique index on month for faster queries

## Security Considerations

- All user input is sanitized before storage
- Expired pastes are automatically cleaned up
- No sensitive information is exposed in URLs
- Rate limiting should be implemented in production

## Performance Optimization

- Database indexes on frequently queried columns
- Efficient cleanup of expired pastes
- Minimal database queries per request
- Static asset caching 