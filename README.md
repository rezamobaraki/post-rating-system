# Post Rating System

A highly scalable Django-based application allowing users to view and rate posts. It includes advanced features such as user authentication, fraud detection, rate limiting, and asynchronous task processing using Celery. The project is Dockerized for easy deployment and comes with auto-generated API documentation using Swagger and ReDoc.

## Table of Contents

- [Project Overview](#project-overview)
- [Features](#features)
- [System Architecture](#system-architecture)
- [Key Components](#key-components)
- [Use-Cases](#use-cases)
- [Mechanism of Fraud Detection](#mechanism-of-fraud-detection)
- [Setup and Installation](#setup-and-installation)
- [Docker Usage](#docker-usage)
- [Environment Variables](#environment-variables)
- [Makefile Commands](#makefile-commands)
- [Testing](#testing)
- [API Documentation](#api-documentation)
- [Performance and Scalability](#performance-and-scalability)
- [Future Improvements](#future-improvements)
- [Contact](#contact)

---

## Project Overview

The **Post Rating System** allows users to interact with posts by rating them. It implements fraud detection mechanisms to prevent rating manipulation and is designed to handle high traffic with ease. The project is fully containerized using Docker and supports background tasks with Celery.

---

## Features

- User authentication (JWT)
- Post rating with average score and total count
- Fraud detection for rating manipulation
- Asynchronous processing with Celery
- Redis for caching and rate limiting
- API documentation with Swagger UI and ReDoc
- Dockerized for deployment

---

## System Architecture

```
[User] <-> [Nginx] <-> [Django App] <-> [PostgreSQL]
                          ^
                          |
                          v
                      [Redis Cache]
                          ^
                          |
                          v
                    [Celery Worker]
```

- **Django Application**: Core API handling user interactions.
- **PostgreSQL**: Database for storing posts, ratings, and statistics.
- **Redis**: Caching and fraud detection.
- **Celery Worker**: Asynchronous background task processing.

---

## Key Components

- **Post**: Represents user-generated content that can be rated.
- **Rate**: Stores user ratings for a post, including a score and whether the rating is suspected of fraud.
- **PostStat**: Tracks aggregated statistics like average rating and total number of ratings.
- **Fraud Detection**: Uses Redis to monitor and prevent rating manipulation through suspicious activity detection.

---

## Use-Cases

1. **Viewing Posts with Statistics**:
   - A user can request a list of posts. Each post displays its title, content, and aggregated rating statistics (average rating and total ratings).

2. **Submitting a Rating**:
   - Authenticated users can rate posts. A score between 0 and 5 is allowed, and the system updates the post statistics (average score and total ratings) accordingly.

3. **Fraud Detection and Rating Prevention**:
   - If a user attempts to submit an abnormal number of ratings within a short period (e.g., coordinated attacks), the system detects this behavior, flags it as suspicious, and prevents the action from being processed.

4. **Periodic Post Statistics Update**:
   - The system automatically updates post statistics at scheduled intervals, processing pending ratings and adjusting the average score.

---

## Mechanism of Fraud Detection

The system employs a multi-tiered approach to detect and prevent fraudulent rating activities. Fraud detection is implemented using Redis and custom logic, ensuring real-time identification of suspicious behavior.

### Fraud Detection Strategies:

1. **Not Suspected**: 
   - If no fraudulent activity is detected, the user's rating is saved, and the post statistics are updated immediately.
   
2. **Flag and Prevent**: 
   - Blocks fraudulent activity before it occurs. For example, if a user is attempting to flood the system with ratings in a short time, the system prevents the action.

3. **Flag and Repost**: 
   - Identifies suspicious ratings and flags them for review. These flagged actions can be resubmitted later after a more in-depth analysis.

4. **Flag and Remove**: 
   - Detects fraudulent ratings and removes them from the system automatically.

5. **Flag and Update**: 
   - Marks suspicious activity for later analysis and updates the post statistics accordingly.

### Fraud Detection Workflow:
- In the initial stage, within 10 minutes, if 1000 fraudulent ratings (is_fraud = True) are detected, the system takes action.
- After detecting potential fraud, the post statistics are updated, and the fraudulent activity is either blocked or flagged.

### Fraud Detection Class:

The fraud detection system works with several approaches to detect and mitigate suspicious activities:

```python
"""
This module contains the FraudDetectionSystem class that is responsible for detecting fraudulent activities.

Several approaches to detect fraudulent activities:
1. Rate limiting: Limit the number of actions a user can perform within a certain period.
2. Suspicious activity detection: Detect suspicious activities based on certain thresholds.
3. User behavior analysis: Analyze user behavior to detect fraudulent activities.

Fraud Detection Mechanisms:
- Analyse and remove: Use a flag to mark fraudulent activities.
- Prevent: Use a throttled exception to stop the action.
"""
```

---

## Setup and Installation

### Requirements

- Docker
- Docker Compose
- Python 3.8+
- Poetry (for dependency management)

### Local Development

1. Clone the repository:

   ```bash
   git clone https://github.com/MrRezoo/post-rating-system.git
   cd post-rating-system
   ```

2. Install dependencies using Poetry:

   ```bash
   poetry install
   ```

3. Set up the environment variables:

   ```bash
   cp config.example.env config.env
   ```

4. Start the development server:

   ```bash
   make runserver
   ```

---

### Using Docker

1. Prepare the Docker environment:

   ```bash
   make prepare-compose
   ```

2. Start the Docker containers:

   ```bash
   make up
   ```

3. To rebuild and start:

   ```bash
   make up-force-build
   ```

4. To stop the containers:

   ```bash
   make down
   ```

---

## Environment Variables

Ensure the following environment variables are set in the `config.env` file:

```ini
SECRET_KEY=django-insecure
DEBUG=True
LOGLEVEL=info
ALLOWED_HOSTS=0.0.0.0,127.0.0.1,localhost
POSTGRES_DB=post_rating
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_HOST=post_rating_postgres
POSTGRES_PORT=5432
REDIS_HOST=post_rating_redis
REDIS_PORT=6379
JWT_SECRET_KEY=your_jwt_secret_key
```

---

## Makefile Commands

This project includes a `Makefile` for automating common tasks:

| Command                 | Description                                     |
|-------------------------|-------------------------------------------------|
| `make help`              | Show available commands                         |
| `make install`           | Install all dependencies using Poetry           |
| `make runserver`         | Run Django development server                   |
| `make migrate`           | Apply database migrations                       |
| `make dump-data`         | Dump current database data                      |
| `make create-superuser`  | Create a Django superuser                       |
| `make shell`             | Open the Django shell                           |
| `make show-urls`         | Display all registered URLs                     |
| `make test`              | Run unit tests                                  |
| `make build`             | Build the Docker image                          |
| `make up`                | Start the Docker containers                     |
| `make down`              | Stop the Docker containers                      |
| `make seeder`            | Seed the database with initial data             |

---

## Testing

To run the tests, use the following command:

```bash
make test
```

The project includes tests for critical features such as fraud detection and rating logic, as well as integration tests to ensure smooth interactions between components.

---

## API Documentation

This project comes with automatically generated API documentation using Swagger and ReDoc.

- **Swagger UI**: Available at `/api/v1/swagger/`
- **ReDoc UI**: Available at `/api/v1/redoc/`

API routes include:

- `GET /api/v1/posts/` - List all posts and their statistics.
- `POST /api/v1/posts/{post_id}/rates/` - Rate a specific post.

---

## Performance and Scalability

- **Caching**: Redis is used to cache post statistics and pending ratings.
- **Asynchronous Processing**: Celery is used for background tasks, ensuring that the main API remains responsive.
- **Rate Limiting**: Implemented via custom throttles to prevent abuse.
- **Dockerized**: The system is fully containerized using Docker, allowing for easy scaling and deployment.

---

## Future Improvements

1. **Enhanced Fraud Detection**: Add machine learning-based fraud detection to improve accuracy.
2. **Real-Time Updates**: Implement WebSockets for real-time rating updates.
3. **Database Sharding**: Shard the database to handle larger datasets more efficiently.
4. **CDN Integration**: Use a CDN for serving static and media files to reduce server load.

---

## Contact

For any inquiries or issues, please contact:

- Name: Reza Mobaraki
- Email: rezam578@gmail.com



