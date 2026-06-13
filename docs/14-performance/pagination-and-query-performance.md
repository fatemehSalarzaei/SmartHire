# Pagination and Query Performance

- All list endpoints use pagination.
- Default page size: 25.
- Maximum page size: 100.
- Sort fields must be indexed where high volume.
- Search should be controlled and indexed; avoid unrestricted JSON search initially.
