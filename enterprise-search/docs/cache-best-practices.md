# 缓存最佳实践

## 为什么需要缓存？

缓存是提升性能的关键手段。通过将频繁访问的数据存储在快速的存储介质中，可以：

- 减少数据库查询次数
- 降低响应延迟
- 提高系统吞吐量

## Redis 缓存使用

### 基本操作

```python
import redis

# 连接 Redis
r = redis.Redis(host='localhost', port=6379, db=0)

# 设置缓存
r.set('key', 'value', ex=3600)  # 1小时过期

# 获取缓存
value = r.get('key')
```

### 常用数据结构

1. **String**: 简单键值对
2. **Hash**: 存储对象
3. **List**: 消息队列
4. **Set**: 标签、去重
5. **Sorted Set**: 排行榜

## 缓存模式

### Cache Aside Pattern

最常用的缓存模式：

```python
def get_user(user_id):
    # 1. 先查缓存
    user = cache.get(f"user:{user_id}")
    if user:
        return user

    # 2. 缓存不存在，查数据库
    user = db.query_user(user_id)

    # 3. 写入缓存
    cache.set(f"user:{user_id}", user, ex=3600)

    return user
```

### Read/Write Through

由缓存层处理数据库读写，应用只与缓存交互。

### Write Behind

写入缓存后异步更新数据库，提高写入性能。

## 缓存问题及解决方案

### 缓存穿透

问题：查询不存在的数据，请求直接打到数据库

解决方案：

- 缓存空值
- 布隆过滤器

### 缓存雪崩

问题：大量缓存同时过期

解决方案：

- 设置随机过期时间
- 多级缓存
- 熔断降级

### 缓存击穿

问题：热点数据过期，大量请求打到数据库

解决方案：

- 互斥锁
- 永不过期 + 异步更新

## 缓存一致性

### 延迟双删

```python
def update_user(user_id, data):
    # 1. 删除缓存
    cache.delete(f"user:{user_id}")

    # 2. 更新数据库
    db.update_user(user_id, data)

    # 3. 延迟删除缓存
    time.sleep(0.5)
    cache.delete(f"user:{user_id}")
```

### 基于消息队列

使用 Canal 监听 binlog，异步更新缓存。

## 本地缓存

对于热点数据，可以使用本地缓存进一步提升性能：

```python
from functools import lru_cache

@lru_cache(maxsize=1000)
def get_config(key):
    return db.get_config(key)
```

## 总结

合理使用缓存可以显著提升系统性能，但需要注意：

1. 选择合适的缓存策略
2. 处理好缓存一致性问题
3. 监控缓存命中率
4. 设置合理的过期时间
