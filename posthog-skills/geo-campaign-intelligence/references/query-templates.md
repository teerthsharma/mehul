# Query Templates

## Query 1
```sql
GROUP BY properties.$geoip_country_name on $pageview
```

## Query 2
```sql
JOIN chapter_opened ON distinct_id + 5-min window to get geo for readers
```

