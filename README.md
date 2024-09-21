Here’s an integrated and improved version of the document with all the suggested additions:

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

The system adopts a **microservices architecture**, utilizing Docker for containerization and orchestration. Below are the key components:

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

### 3.1 Post Model

The `Post` model represents user-generated content that can be rated.

```python
class Post(BaseModel):
    title = models.CharField(_("title"), max_length=255)
    content = models.TextField(_("content"))
```

- **Attributes**:
  - `title`: The title of the post.
  - `content`: The body of the post.
  - Inherits from `BaseModel`, which tracks the creation and modification timestamps.

### 3.2 Rate Model

The `Rate` model handles user ratings for each post. Each rating is linked to a user and a post.

```python
class Rate(BaseModel):
    post = models.ForeignKey("Post", on_delete=models.CASCADE, related_name='rates')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='rates')
    score = models.IntegerField(
        null=True,
        validators=[
            MinValueValidator(RateScoreEnum.ZERO_STARS), 
            MaxValueValidator(RateScoreEnum.FIVE_STARS)
        ]
    )
    is_suspected = models.BooleanField(default=False)
```

### 3.3 PostStat Model

The `PostStat` model maintains aggregated statistics for each post, including the average rating and the total number of ratings.

```python
class PostStat(BaseModel):
    post = models.OneToOneField(Post, on_delete=models.CASCADE, related_name='stat')
    average_rates = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    total_rates = models.PositiveIntegerField(default=0)
```

### 3.4 Caching Strategy

- **Post Statistics Caching**: Post stats (e.g., average rating, total rates) are cached in Redis to reduce load on the database.
- **Pending Rates**: New ratings are stored in Redis before being processed in bulk to optimize database transactions.

### 3.5 Asynchronous Processing with Celery

Celery is used for handling background tasks, such as updating post statistics and applying pending rates.

```python
@shared_task
def apply_pending_rates():
    key = RedisKeyTemplates.pending_rates_key()
    if pending_rates := cache.get(key, []):
        from posts.services.commands.rate import bulk_update_or_create_rates
        bulk_update_or_create_rates(rate_data=pending_rates)
        cache.delete(key)
```

### 3.6 Rate Limiting and Fraud Detection

The system employs a multi-tiered approach to prevent fraudulent rating activities. This includes:

- **Rate Limiting**: Restricting the number of ratings a user can submit within a time period.
- **Fraud Detection**: Detecting abnormal activity, such as a sudden spike in ratings, and marking them as suspicious.

```python
class FraudDetection:
    @classmethod
    def detect_suspicious_activity(cls, post_id: int) -> bool:
        fraud_detect_key = RedisKeyTemplates.format_fraud_detect_key(post_id)
        recent_actions = redis_client.lrange(fraud_detect_key, 0, -1)
        if len(recent_actions) >= cls.suspicious_threshold:
            first_action_time = float(recent_actions[0])
            current_time = time.time()
            if current_time - first_action_time < cls.time_threshold:
                return True
        redis_client.lpush(fraud_detect_key, time.time())
        redis_client.ltrim(fraud_detect_key, 0, cls.last_actions_to_track - 1)
        redis_client.expire(fraud_detect_key, cls.time_threshold)
        return False
```

---

## Use-Cases

1. **Viewing Posts with Statistics**: Users can view a list of posts, along with statistics like average ratings and total ratings.
2. **Submitting a Rating**: Authenticated users can submit ratings for posts, with the system updating statistics accordingly.
3. **Fraud Prevention**: The system detects and prevents fraudulent activity when abnormal rating patterns are identified.
4. **Post Statistics Update**: Post statistics are updated periodically by background tasks.

---

## Mechanism of Fraud Detection

Fraud detection is implemented to identify and prevent rating manipulation. The system uses Redis to track real-time activity and flags suspicious patterns.

### Fraud Detection Workflow:
- **Rate Limiting**: Limits the number of actions a user can perform within a given period.
- **Suspicious Activity Detection**: Detects suspicious behavior based on the frequency of ratings in a short time.

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

### Docker Usage

1. Prepare the Docker environment:

   ```bash
   make prepare-compose
   ```

2. Start the Docker containers:

   ```bash
   make up
   ```

3. Rebuild and start the containers:

   ```bash
   make up-force-build
   ```

4. Stop the containers:

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

The project includes tests for key features, such as fraud detection, rating logic, and system integration.

---

## API Documentation

The project includes automatically generated API documentation using **Swagger UI** and **ReDoc**.

- **Swagger UI**: Available at `/api/v1/swagger/`
- **ReDoc UI**: Available at `/api/v1/red

oc/`

---

## Performance and Scalability

The system is designed to scale efficiently:

1. **Caching**: Redis caches post statistics to minimize database load.
2. **Asynchronous Processing**: Celery processes background tasks to maintain responsiveness.
3. **Rate Limiting**: Custom throttles prevent abusive behavior.
4. **Dockerized**: Fully containerized for scalability and ease of deployment.

---

## Future Improvements

1. **Enhanced Fraud Detection**: Add machine learning algorithms for better fraud detection.
2. **Real-Time Updates**: Introduce WebSockets or gRPC for real-time updates on post ratings.
3. **Database Sharding**: Shard the database to handle large datasets efficiently.
4. **CDN Integration**: Implement a CDN for serving static files to reduce load.

---

## Contact

For any inquiries or issues, please contact:

- **Name**: Reza Mobaraki
- **Email**: rezam578@gmail.com

---

