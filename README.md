# Smart Airport Ride Pooling Backend

A complete FastAPI backend that pools airport passengers into shared cabs using seat/luggage constraints, detour checks, concurrency-safe assignment, and dynamic pricing.

## Architecture Overview

- **FastAPI** REST service (`backend/app/main.py`) with Swagger docs at `/docs`.
- **Service layer + Repository layer** for separation of concerns.
- **SQLAlchemy ORM + PostgreSQL** for persistence.
- **Alembic** for schema migrations.
- **Redis lock + DB row lock** for concurrency-safe pool assignment.
- **Pooling algorithm** with Haversine distance + detour tolerance.

## Project Structure

```text
backend/
  app/
    algorithms/
    api/
    core/
    db/
    models/
    repositories/
    schemas/
    services/
    main.py
  migrations/
    versions/
  tests/
  requirements.txt
  Dockerfile
  alembic.ini
docker-compose.yml
README.md
requirements.txt
```

## Database Schema

Tables:
- `passengers(id, pickup_lat, pickup_lng, drop_lat, drop_lng, luggage_count, detour_tolerance, status)`
- `cabs(id, seat_capacity, luggage_capacity, status)`
- `rides(id, cab_id, status, total_price)`
- `ride_passengers(ride_id, passenger_id, pickup_order, drop_order)`

Indexes:
- `passengers.status`, `passengers.pickup_lat`, `passengers.pickup_lng`
- `cabs.status`, `rides.status`

## Setup & Run

### Option A: Docker Compose (recommended)

```bash
docker-compose up --build
```

This runs migrations, seeds sample data (5 passengers + 3 cabs), and starts API at:
- `http://localhost:8000`
- Swagger: `http://localhost:8000/docs`

### Option B: Local without Docker

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
alembic upgrade head
python -m app.db.seed
uvicorn app.main:app --reload
```

## API Documentation

### `POST /passengers/request_ride`
Create a passenger ride request.

### `POST /pool/run`
Run pooling to create one feasible shared ride.

### `GET /ride/{id}`
Get ride details and passenger order.

### `DELETE /ride/{id}`
Cancel a ride and release cab/passengers.

## Pooling Algorithm (Working)

1. Fetch waiting passengers.
2. Choose anchor passenger and find nearby passengers by Haversine distance threshold.
3. For each available cab (locked with `SELECT ... FOR UPDATE SKIP LOCKED`):
   - Enforce seat and luggage capacities.
   - Validate detour tolerance.
4. Create ride and ride-passenger mapping.
5. Apply dynamic pricing.

### Dynamic Pricing

```text
base_price = distance * rate_per_km
shared_discount = passengers / cab_capacity
final_price = base_price * (1 - shared_discount * 0.3)
```

## Concurrency Handling

To avoid two pool workers assigning the same seat:
- **Redis lock** `pooling_assignment_lock` ensures only one active pooling run cluster-wide.
- **Database row locks** on available cabs with `FOR UPDATE SKIP LOCKED` prevent duplicate cab assignment in concurrent transactions.

## Performance Considerations

- **100 RPS (design-level)**:
  - SQLAlchemy engine pooling (`pool_size`, `max_overflow`) for efficient DB connections.
  - Redis lock operation is O(1); pooling runs are bounded by candidate window.
- **Latency under 300ms (design-level)**:
  - API endpoints are lightweight, indexed filters on status and pickup coords.
  - Keep nearby search bounded (`nearby_distance_km`) and use prefiltered waiting list.
- **10,000 concurrent users (design-level)**:
  - Horizontal scale FastAPI pods/containers behind load balancer.
  - Shared Redis for distributed lock + PostgreSQL for durable state.
  - Add read replicas and queue-based async matching if traffic grows.

## Complexity Analysis

Let:
- `P` = waiting passengers
- `C` = available cabs

Current single-run complexity:
- Nearby scan: `O(P)`
- Cab evaluation with constraints: up to `O(C * P)`
- Route distance computation per candidate set: linear in matched passengers

Total worst-case per run: **`O(C * P)`**.

## Assumptions

- A pooling run creates at most one ride per invocation (`POST /pool/run`).
- Passenger detour tolerance is interpreted as percentage over direct anchor route.
- Ride cancellation marks linked passengers as cancelled.

## Tests

Run:

```bash
cd backend
pytest -q
```

Includes:
- ride request creation
- pooling behavior
- pricing formula
