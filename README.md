# Post Rating System

A highly scalable Django-based application allowing users to view and rate posts. It includes advanced features such as
user authentication, fraud detection, rate limiting, and asynchronous task processing using Celery. The project is
Dockerized for easy deployment and comes with auto-generated API documentation using Swagger and ReDoc.

## Table of Contents

- [Project Overview](#project-overview)
- [Features](#features)
- [System Architecture](#system-architecture)
- [System Design Solution](#system-design-solution)
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

The **Post Rating System** allows users to interact with posts by rating them. It implements fraud detection mechanisms
to prevent rating manipulation and is designed to handle high traffic with ease. The project is fully containerized
using Docker and supports background tasks with Celery.

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

The system adopts a **microservices architecture**, utilizing Docker for containerization and orchestration. Below are
the key components:

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

## System Design Solution

### System Architecture Overview

**Some components are marked with (*) which are not implemented in the current project but are proposed for future**

This system design provides a scalable and resilient architecture for the Post Rating System, balancing performance,
consistency, and fault tolerance. **Eventual consistency** is a consistency model used in distributed computing to
achieve high availability and partition tolerance. It ensures that, given enough time, all replicas of a data item will
converge to the same value. This model allows the system to remain available and partition-tolerant, even if some nodes
are temporarily out of sync.

```
[Load Balancer] 
     |
     v
[API Gateway]
     |
     v
[Application Servers (Django)]
     |
     v
[Caching Layer (Redis)]
     |
     v
[Database Cluster (PostgreSQL)]
     |
     v
[Message Queue (RabbitMQ)]
     |
     v
[Celery Workers]
```

- *Load Balancer
    - Distributes incoming traffic across multiple API Gateway instances
    - Implements health checks and SSL termination

- *API Gateway
    - Handles authentication and rate limiting (e.g., using JWT tokens)
    - Routes requests to appropriate microservices (e.g., posts, users)

#### Application Servers (Django)

- Processes API requests (e.g., post rating,list of posts, user authentication)
- Implements business logic and fraud detection mechanisms

#### Caching Layer (Redis)

- Stores frequently accessed data (e.g., post statistics in retrieval, rates in submission)
- Implements rate limiting and fraud detection

#### Database Cluster (PostgreSQL)

- Primary data store for posts, users, ratings, and statistics
- *Implements sharding for horizontal scaling (e.g., weighted sharding based on post popularity)

#### Message Queue (Redis)

- Facilitates asynchronous communication between components (e.g., Apply pending rates)
- Ensures reliable message delivery for background tasks (e.g., updating post stats, periodic tasks)

#### Celery Workers

- Process background tasks (e.g., updating post statistics)
- Handle computationally intensive operations asynchronously (e.g., fraud detection, rate processing)

### Data Flow and Consistency Model

The system implements an eventual consistency model to ensure high availability and partition tolerance. Here's how data
flows through the system:

1. User submits a rating:
    - API Gateway validates the request and applies rate limiting (e.g., each user can only send 100 ratings per hour)
    - Application server receives the rating and performs initial validation
    - Rating is temporarily stored in Redis cache (pending rates)
    - Acknowledgment is sent back to the user

2. Background processing:
    - Celery worker periodically processes pending ratings from Redis
    - Updates are applied to the PostgreSQL database in batches
    - Post statistics are recalculated and cached in Redis

3. Read operations:
    - Frequently accessed data (e.g., post statistics) is served from Redis cache
    - Less frequent queries are served directly from the PostgreSQL database

### Scalability and Performance Optimizations

- *Horizontal Scaling
    - Application servers can be scaled horizontally behind the load balancer
    - Database read replicas can be added to handle increased read traffic
- Caching Strategy
    - *Use Read-Through and Write-Through caching for improved performance
    - Use cache-aside pattern for other frequently accessed data
        1. **Read Operation**:
            - Check if the data is in the cache.
            - If the data is found (cache hit), return it.
            - If the data is not found (cache miss), load it from the database, store it in the cache, and then return
              it.
        2. **Write Operation**:
            - Write the data to the database.
            - Invalidate or update the cache to ensure consistency.
    - *Use Redis pipeline for batch operations to reduce round-trip latency
- *Database Sharding
    - Implement horizontal sharding based on post ID or author popularity or user ID
    - Use consistent hashing for efficient data distribution
- Asynchronous Processing
    - Offload computationally intensive tasks to Celery workers (e.g., fraud detection, post statistics)
    - Use message queues to decouple components and ensure reliable processing

### Consistency and CAP Theorem Considerations

The system prioritizes Availability and Partition Tolerance (AP) from the CAP theorem, sacrificing strong consistency
for better performance and scalability. This choice is suitable for a rating system where occasional inconsistencies are
tolerable.

#### Eventual Consistency

- Ratings may not be immediately reflected in post statistics (e.g., pending rates)
- Background processes ensure data converges to a consistent state over time (e.g., updating post stats, periodic tasks)

#### *Conflict Resolution

- Implement versioning for ratings to detect and resolve conflicts
- Use last-write-wins (LWW) strategy for simplicity, or implement custom merge logic if needed( if two rating conflict
  with each other the one with the latest timestamp will be considered)¬

### *Fault Tolerance and Reliability

- Data Replication
    - Use multi-region database replication for disaster recovery
    - Implement read replicas for improved read performance and fault tolerance
- Monitoring and Alerting
    - Implement comprehensive monitoring using tools.(e.g., Prometheus, Grafana)
    - Set up alerts for critical system metrics and error rates

### Security Considerations

- Authentication and Authorization
    - Implement JWT-based authentication
    - *Use role-based access control (RBAC) for fine-grained permissions
- Rate Limiting and Throttling
    - Implement IP-based and user-based rate limiting at the API Gateway level (e.g., 1000 requests per hour)
    - Implement endpoint-specific rate limits to prevent abuse (e.g., `/rate` endpoint)
    - Use Redis to store and manage rate limiting counters

### Future Improvements

1. Implement a recommendation system based on user ratings and behavior
2. Introduce real-time updates using WebSockets, GRPC for live rating updates
3. Implement A/B testing framework for experimenting with different rating algorithms
4. Introduce machine learning-based fraud detection for more sophisticated anomaly detection
5. Implement a content delivery network (CDN) for serving static assets and improving global performance
 
## System Design used in this project

### Performance Optimizations

To handle millions of ratings per post without performance issues:

#### Denormalized Post Statistics

- Store `average_rating` and `total_ratings` in the `PostStat` model
- Update these values asynchronously using Celery tasks

#### Caching Strategy

- Cache post statistics in Redis
- Implement a write-through cache for immediate updates
- Periodically sync cache with the database

#### Batch Processing

- Accumulate new ratings in Redis (pending rates)
- Process and apply ratings in batches using Celery tasks

#### Database Indexing

- Create appropriate indexes on the `Rate` model (user, post)

### Fraud Detection and Rating Stabilization

To prevent sudden, artificial changes in post ratings:

- Time-based Weighted Average
    - Implement a weighted average system that gives more weight to established ratings
    - Gradually incorporate new ratings over time

- Rate Limiting
    - Implement user-based and IP-based rate limiting to prevent rapid-fire ratings

- Anomaly Detection
    - Monitor for unusual patterns in rating behavior (e.g., sudden spikes in low ratings)
    - Flag suspicious activities for review

- Delayed Impact
    - Introduce a delay before new ratings significantly affect the overall score
    - Use a sliding window approach to smooth out short-term fluctuations.
      this approach can help to stabilize the average rating by considering a window
      of recent ratings rather than just the most recent rating.
      This helps to prevent sudden changes in the average rating due to a few anomalous ratings.

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

The `PostStat` model maintains aggregated statistics for each post, including the average rating and the total number of
ratings.

```python
class PostStat(BaseModel):
    post = models.OneToOneField(Post, on_delete=models.CASCADE, related_name='stat')
    average_rates = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    total_rates = models.PositiveIntegerField(default=0)
```

### 3.4 Caching Strategy

- **Post Statistics Caching**: Post stats (e.g., average rating, total rates) are cached in Redis to reduce load on the
  database.
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

1. **Viewing Posts with Statistics**: Users can view a list of posts, along with statistics like average ratings and
   total ratings.
2. **Submitting a Rating**: Authenticated users can submit ratings for posts, with the system updating statistics
   accordingly.
3. **Fraud Prevention**: The system detects and prevents fraudulent activity when abnormal rating patterns are
   identified.
4. **Post Statistics Update**: Post statistics are updated periodically by background tasks.

---

## Mechanism of Fraud Detection

Fraud detection is implemented to identify and prevent rating manipulation. The system uses Redis to track real-time
activity and flags suspicious patterns.

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
SECRET_KEY = django-insecure
DEBUG = True
LOGLEVEL = info
ALLOWED_HOSTS = 0.0.0.0,127.0.0.1,localhost
POSTGRES_DB = post_rating
POSTGRES_USER = postgres
POSTGRES_PASSWORD = postgres
POSTGRES_HOST = post_rating_postgres
POSTGRES_PORT = 5432
REDIS_HOST = post_rating_redis
REDIS_PORT = 6379
JWT_SECRET_KEY = your_jwt_secret_key
```

---

## Makefile Commands

This project includes a `Makefile` for automating common tasks:

| Command                 | Description                           |
|-------------------------|---------------------------------------|
| `make help`             | Show available commands               |
| `make install`          | Install all dependencies using Poetry |
| `make runserver`        | Run Django development server         |
| `make migrate`          | Apply database migrations             |
| `make dump-data`        | Dump current database data            |
| `make create-superuser` | Create a Django superuser             |
| `make shell`            | Open the Django shell                 |
| `make show-urls`        | Display all registered URLs           |
| `make test`             | Run unit tests                        |
| `make build`            | Build the Docker image                |
| `make up`               | Start the Docker containers           |
| `make down`             | Stop the Docker containers            |
| `make seeder`           | Seed the database with initial data   |

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
- **ReDoc UI**: Available at `/api/v1/redoc/`

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

