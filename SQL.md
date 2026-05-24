# SQL task

Given tables:

```sql
tasks    (id, name, status, project_id)
projects (id, name)
```

All queries are written for PostgreSQL.


## 1. Get all statuses, not repeating, alphabetically ordered

```sql
SELECT DISTINCT status
FROM   tasks
ORDER  BY status;
```


## 2. Get the count of all tasks in each project, ordered by tasks count descending

```sql
SELECT p.id,
       p.name,
       COUNT(t.id) AS tasks_count
FROM   projects p
LEFT   JOIN tasks t ON t.project_id = p.id
GROUP  BY p.id, p.name
ORDER  BY tasks_count DESC, p.name;
```

`LEFT JOIN` keeps projects that have no tasks (count = 0).
`COUNT(t.id)` ignores `NULL`s, so it is `0` for empty projects.


## 3. Get the count of all tasks in each project, ordered by project names

```sql
SELECT p.id,
       p.name,
       COUNT(t.id) AS tasks_count
FROM   projects p
LEFT   JOIN tasks t ON t.project_id = p.id
GROUP  BY p.id, p.name
ORDER  BY p.name;
```


## 4. Get the tasks for all projects having the name beginning with "N"

```sql
SELECT t.*
FROM   tasks t
JOIN   projects p ON p.id = t.project_id
WHERE  p.name LIKE 'N%';
```

Use `ILIKE 'N%'` instead of `LIKE` if the match should be case-insensitive.


## 5. Get the list of all projects containing the 'a' letter in the middle of the name, with task counts

"Middle" means the letter `a` is neither the first nor the last character, so
the name must have at least one character on each side of an `a`. The pattern
`_%a%_` enforces that: a single character, then zero or more characters,
then `a`, then zero or more characters, then a single character.

Projects without tasks still appear (count = 0). Orphan tasks (those with
`project_id IS NULL`) are simply ignored because we drive the query from
`projects` via `LEFT JOIN`.

```sql
SELECT p.id,
       p.name,
       COUNT(t.id) AS tasks_count
FROM   projects p
LEFT   JOIN tasks t ON t.project_id = p.id
WHERE  p.name LIKE '_%a%_'
GROUP  BY p.id, p.name
ORDER  BY p.name;
```


## 6. Get the list of tasks with duplicate names, alphabetically ordered

```sql
SELECT id,
       name,
       status,
       project_id
FROM   tasks
WHERE  name IN (
           SELECT name
           FROM   tasks
           GROUP  BY name
           HAVING COUNT(*) > 1
       )
ORDER  BY name, id;
```

The subquery picks names that occur more than once; the outer query returns
every individual task that has one of those names.


## 7. Tasks with several exact matches of both name and status, from project 'Delivery', ordered by matches count

```sql
SELECT t.name,
       t.status,
       COUNT(*) AS matches
FROM   tasks t
JOIN   projects p ON p.id = t.project_id
WHERE  p.name = 'Delivery'
GROUP  BY t.name, t.status
HAVING COUNT(*) > 1
ORDER  BY matches DESC, t.name, t.status;
```

If individual task rows are required instead of grouped pairs, use a window
function:

```sql
SELECT t.id,
       t.name,
       t.status,
       COUNT(*) OVER (PARTITION BY t.name, t.status) AS matches
FROM   tasks t
JOIN   projects p ON p.id = t.project_id
WHERE  p.name = 'Delivery'
       AND (t.name, t.status) IN (
           SELECT t2.name, t2.status
           FROM   tasks t2
           JOIN   projects p2 ON p2.id = t2.project_id
           WHERE  p2.name = 'Delivery'
           GROUP  BY t2.name, t2.status
           HAVING COUNT(*) > 1
       )
ORDER  BY matches DESC, t.name, t.status, t.id;
```


## 8. Project names having more than 10 tasks in status 'completed', ordered by project_id

```sql
SELECT p.id,
       p.name
FROM   projects p
JOIN   tasks t ON t.project_id = p.id
WHERE  t.status = 'completed'
GROUP  BY p.id, p.name
HAVING COUNT(*) > 10
ORDER  BY p.id;
```
