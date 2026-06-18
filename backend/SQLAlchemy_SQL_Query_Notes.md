# SQLAlchemy SQL 查询笔记

本文用于理解本项目 FastAPI 后端中 SQLAlchemy ORM 查询语句和 SQL 语句之间的对应关系。

## 1. SQLAlchemy ORM 是什么

SQLAlchemy ORM 可以理解为：

```text
用 Python 对象和链式方法来构造 SQL 查询语句。
```

例如本项目中的 ORM 模型：

```python
TrafficLog
```

对应数据库表：

```sql
traffic_log
```

模型字段：

```python
TrafficLog.src_ip
TrafficLog.packet_size
TrafficLog.created_at
```

对应数据库字段：

```sql
src_ip
packet_size
created_at
```

## 2. 基本对应关系

常见 SQLAlchemy 写法和 SQL 的关系如下：

```text
db.query(...)        -> SELECT ...
.filter(...)         -> WHERE ...
.group_by(...)       -> GROUP BY ...
.order_by(...)       -> ORDER BY ...
.limit(...)          -> LIMIT ...
.all()               -> 执行 SQL，返回所有结果列表
.first()             -> 执行 SQL，返回第一条结果
.count()             -> 执行 SQL，返回数量
.scalar()            -> 执行 SQL，返回单个值
```

## 3. db.query(...)

`db.query(...)` 用来声明要查询的字段，对应 SQL 的 `SELECT`。

Python 写法：

```python
db.query(
    TrafficLog.src_ip,
    TrafficLog.packet_size,
)
```

对应 SQL：

```sql
SELECT
    src_ip,
    packet_size
FROM traffic_log;
```

如果查询整个 ORM 对象：

```python
db.query(TrafficLog)
```

对应：

```sql
SELECT
    id,
    src_ip,
    src_port,
    dst_ip,
    dst_port,
    protocol,
    packet_size,
    duration,
    created_at
FROM traffic_log;
```

## 4. label(...)

`label(...)` 用来给查询结果字段起别名，对应 SQL 的 `AS`。

Python 写法：

```python
TrafficLog.src_ip.label("src_ip")
```

对应 SQL：

```sql
src_ip AS src_ip
```

再例如：

```python
func.count(TrafficLog.id).label("count")
```

对应：

```sql
COUNT(id) AS count
```

作用是让查询结果可以通过清晰的名字访问：

```python
row.src_ip
row.count
```

## 5. func

`func` 用来调用 SQL 函数。

Python 写法：

```python
func.count(TrafficLog.id)
```

对应 SQL：

```sql
COUNT(id)
```

常见例子：

```python
func.count(TrafficLog.id)
func.sum(TrafficLog.packet_size)
func.max(TrafficLog.packet_size)
func.min(TrafficLog.packet_size)
func.avg(TrafficLog.packet_size)
```

分别对应：

```sql
COUNT(id)
SUM(packet_size)
MAX(packet_size)
MIN(packet_size)
AVG(packet_size)
```

## 6. COALESCE

`COALESCE` 是 SQL 的空值处理函数。

SQL 写法：

```sql
COALESCE(value1, value2, ...)
```

含义：

```text
从左到右返回第一个不是 NULL 的值。
```

本项目中的写法：

```python
func.coalesce(func.sum(TrafficLog.packet_size), 0)
```

对应 SQL：

```sql
COALESCE(SUM(packet_size), 0)
```

作用：

```text
如果 SUM(packet_size) 的结果是 NULL，就返回 0。
```

这样可以保证 API 返回的是数字：

```json
{
  "total_bytes": 0
}
```

而不是：

```json
{
  "total_bytes": null
}
```

## 7. group_by(...)

`group_by(...)` 对应 SQL 的 `GROUP BY`，用于分组统计。

Python 写法：

```python
.group_by(TrafficLog.src_ip)
```

对应 SQL：

```sql
GROUP BY src_ip
```

含义：

```text
把 src_ip 相同的多条记录合并成一组，再对每组做 COUNT、SUM 等统计。
```

例如：

```python
db.query(
    TrafficLog.src_ip.label("src_ip"),
    func.count(TrafficLog.id).label("count"),
)
.group_by(TrafficLog.src_ip)
```

对应 SQL：

```sql
SELECT
    src_ip AS src_ip,
    COUNT(id) AS count
FROM traffic_log
GROUP BY src_ip;
```

## 8. order_by(...)

`order_by(...)` 对应 SQL 的 `ORDER BY`，用于排序。

升序：

```python
.order_by(TrafficLog.created_at.asc())
```

对应：

```sql
ORDER BY created_at ASC
```

降序：

```python
.order_by(TrafficLog.created_at.desc())
```

对应：

```sql
ORDER BY created_at DESC
```

按总流量从大到小排序：

```python
.order_by(func.sum(TrafficLog.packet_size).desc())
```

对应：

```sql
ORDER BY SUM(packet_size) DESC
```

## 9. limit(...)

`limit(...)` 对应 SQL 的 `LIMIT`，用于限制返回数量。

Python 写法：

```python
.limit(10)
```

对应 SQL：

```sql
LIMIT 10
```

在接口中通常把它写成参数：

```python
def get_top_src_ip(db: Session, limit: int = 10):
    ...
    .limit(limit)
```

这样请求：

```text
GET /stats/top-src-ip?limit=20
```

就会返回前 20 条。

## 10. all()

`.all()` 的作用是：

```text
真正执行 SQL，并返回所有查询结果。
```

注意：

```python
query = db.query(TrafficLog).limit(10)
```

这一步只是构造查询对象，还没有真正向数据库发送 SQL。

只有调用：

```python
rows = db.query(TrafficLog).limit(10).all()
```

SQLAlchemy 才会执行 SQL，并返回结果列表。

## 11. first()

`.first()` 用来执行 SQL，并返回第一条结果。

Python 写法：

```python
record = db.query(TrafficLog).first()
```

对应含义：

```sql
SELECT ...
FROM traffic_log
LIMIT 1;
```

如果没有数据，返回：

```python
None
```

## 12. scalar()

`.scalar()` 用来获取单个值。

例如统计总记录数：

```python
total = db.query(func.count(TrafficLog.id)).scalar()
```

对应 SQL：

```sql
SELECT COUNT(id)
FROM traffic_log;
```

返回结果可能是：

```python
12345
```

而不是一整行对象。

## 13. 本项目 top-src-ip 查询示例

Python SQLAlchemy 写法：

```python
rows = (
    db.query(
        TrafficLog.src_ip.label("src_ip"),
        func.count(TrafficLog.id).label("count"),
        func.coalesce(func.sum(TrafficLog.packet_size), 0).label("total_bytes"),
    )
    .group_by(TrafficLog.src_ip)
    .order_by(func.coalesce(func.sum(TrafficLog.packet_size), 0).desc())
    .limit(limit)
    .all()
)
```

对应 SQL：

```sql
SELECT
    src_ip AS src_ip,
    COUNT(id) AS count,
    COALESCE(SUM(packet_size), 0) AS total_bytes
FROM traffic_log
GROUP BY src_ip
ORDER BY COALESCE(SUM(packet_size), 0) DESC
LIMIT 10;
```

含义：

```text
从 traffic_log 表中按 src_ip 分组，
统计每个源 IP 的记录数量和总流量，
按总流量从大到小排序，
最后返回前 limit 条。
```

## 14. 查询结果转换

SQLAlchemy 查询返回的 `row` 可以通过字段别名访问：

```python
row.src_ip
row.count
row.total_bytes
```

本项目把它转换成字典：

```python
return [
    {
        "src_ip": row.src_ip,
        "count": int(row.count),
        "total_bytes": int(row.total_bytes or 0),
    }
    for row in rows
]
```

这样 FastAPI 最终可以返回 JSON：

```json
{
  "status": "success",
  "count": 1,
  "elapsed_seconds": 0.003,
  "data": [
    {
      "src_ip": "192.168.1.10",
      "count": 32,
      "total_bytes": 204800
    }
  ]
}
```

## 15. 记忆模板

可以用下面这个模板记忆统计查询：

```python
rows = (
    db.query(
        Model.group_field.label("group_field"),
        func.count(Model.id).label("count"),
        func.coalesce(func.sum(Model.value_field), 0).label("total_value"),
    )
    .group_by(Model.group_field)
    .order_by(func.coalesce(func.sum(Model.value_field), 0).desc())
    .limit(limit)
    .all()
)
```

对应 SQL：

```sql
SELECT
    group_field AS group_field,
    COUNT(id) AS count,
    COALESCE(SUM(value_field), 0) AS total_value
FROM table_name
GROUP BY group_field
ORDER BY COALESCE(SUM(value_field), 0) DESC
LIMIT limit;
```
