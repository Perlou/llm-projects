# Database Optimization Handbook

## Overview

Database optimization is essential for maintaining high-performance applications. This guide covers key strategies for optimizing relational databases.

## Index Optimization

### When to Create Indexes

Create indexes on columns that are:

- Frequently used in WHERE clauses
- Used in JOIN conditions
- Used in ORDER BY or GROUP BY

### Types of Indexes

1. **B-Tree Index**: Default, good for most queries
2. **Hash Index**: Exact match queries
3. **Full-Text Index**: Text search
4. **Composite Index**: Multiple columns

### Index Best Practices

```sql
-- Good: Composite index matching query order
CREATE INDEX idx_user_status_created
ON users(status, created_at);

-- Query that uses the index
SELECT * FROM users
WHERE status = 'active'
AND created_at > '2024-01-01';
```

## Query Optimization

### Use EXPLAIN

Always analyze your queries:

```sql
EXPLAIN ANALYZE
SELECT * FROM orders
WHERE user_id = 123
ORDER BY created_at DESC;
```

### Avoid Common Pitfalls

1. **Don't use SELECT \***

```sql
-- Bad
SELECT * FROM users;

-- Good
SELECT id, name, email FROM users;
```

2. **Avoid functions on indexed columns**

```sql
-- Bad: Index not used
WHERE YEAR(created_at) = 2024

-- Good: Index used
WHERE created_at >= '2024-01-01'
AND created_at < '2025-01-01'
```

3. **Use appropriate JOINs**

```sql
-- Use INNER JOIN when possible
SELECT u.name, o.total
FROM users u
INNER JOIN orders o ON u.id = o.user_id
WHERE o.status = 'completed';
```

## Connection Pooling

### Why Use Connection Pools?

- Reduce connection overhead
- Limit database connections
- Improve response time

### Configuration Example

```python
from sqlalchemy import create_engine

engine = create_engine(
    "postgresql://user:pass@localhost/db",
    pool_size=10,
    max_overflow=20,
    pool_timeout=30
)
```

## Partitioning

### When to Partition

- Tables with millions of rows
- Queries filter by partition key
- Need to archive old data

### Types of Partitioning

1. **Range Partitioning**: By date range
2. **Hash Partitioning**: By hash value
3. **List Partitioning**: By specific values

## Monitoring

### Key Metrics

- Query execution time
- Connection count
- Lock wait time
- Buffer hit ratio

### Slow Query Log

Enable slow query logging:

```sql
SET GLOBAL slow_query_log = 'ON';
SET GLOBAL long_query_time = 1;
```

## Summary

Database optimization requires a combination of:

- Proper indexing
- Query optimization
- Connection management
- Regular monitoring
