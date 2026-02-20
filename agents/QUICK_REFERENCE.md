# Quick Reference: Search, Filter, Sort API

**Tasks:** T5.2.3, T5.2.4, T5.2.5
**For:** Developers integrating search, filter, and sort features

---

## API Endpoint

```
GET /tasks
```

---

## Query Parameters

| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| `search` | string | Search in title/description | `search=meeting` |
| `status` | string | pending \| completed | `status=pending` |
| `priority` | string | low \| medium \| high \| urgent | `priority=high` |
| `tags` | string | Comma-separated (AND logic) | `tags=work,urgent` |
| `due_from` | date | YYYY-MM-DD | `due_from=2026-02-15` |
| `due_to` | date | YYYY-MM-DD | `due_to=2026-02-20` |
| `sort` | string | field:direction | `sort=due_date:asc` |

---

## Sort Fields

- `due_date` - Due date
- `priority` - Priority level
- `created_at` - Creation date
- `title` - Task title

**Directions:** `asc` (ascending) or `desc` (descending)

---

## Examples

### Search
```bash
GET /tasks?search=meeting
```

### Filter by Status
```bash
GET /tasks?status=pending
```

### Filter by Priority
```bash
GET /tasks?priority=high
```

### Filter by Tags (AND logic)
```bash
GET /tasks?tags=work,urgent
```

### Filter by Due Date Range
```bash
GET /tasks?due_from=2026-02-15&due_to=2026-02-20
```

### Sort by Due Date
```bash
GET /tasks?sort=due_date:asc
```

### Sort by Priority
```bash
GET /tasks?sort=priority:desc
```

### Combined
```bash
GET /tasks?search=meeting&status=pending&priority=high&tags=work&sort=due_date:asc
```

---

## Response Format

```json
{
  "tasks": [
    {
      "id": "task-123",
      "title": "Team meeting",
      "description": "Quarterly review",
      "status": "pending",
      "priority": "high",
      "tags": ["work", "urgent"],
      "due_date": "2026-02-20",
      "created_at": "2026-02-15T10:00:00Z",
      "completed_at": null,
      "user_id": "user-456"
    }
  ],
  "total": 1,
  "filters_applied": {
    "search": "meeting",
    "status": "pending",
    "priority": "high",
    "tags": ["work"],
    "sort": "due_date:asc"
  }
}
```

---

## Frontend Components

### SearchBar
```tsx
<SearchBar onSearch={setQuery} placeholder="Search..." />
```

### FilterPanel
```tsx
<FilterPanel onFilterChange={setFilters} availableTags={tags} />
```

### SortSelect
```tsx
<SortSelect onSortChange={setSort} />
```

### TagChips
```tsx
<TagChips tags={task.tags} onTagsChange={updateTags} />
```

### PriorityDropdown
```tsx
<PriorityDropdown value={task.priority} onChange={updatePriority} />
```

---

## Error Codes

| Code | Description |
|------|-------------|
| 400 | Invalid query parameters |
| 401 | Unauthorized |
| 500 | Server error |

---

## Performance

All operations complete in **< 500ms**

---

## Full Documentation

See `agents/SEARCH_FILTER_SORT_DOCUMENTATION.md` for complete details.
