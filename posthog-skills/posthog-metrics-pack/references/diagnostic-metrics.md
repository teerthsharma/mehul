# Diagnostic Metrics

## Chapter Drop-off

```
chapter_dropoff(chapter_n) = 1 - (chapter_completed where chapter_number=n / chapter_opened where chapter_number=n)
```

## Campaign Traffic Quality

```
quality_score(campaign) = chapter_completed / $pageview
```
Where both events have same utm_campaign.

## UTM Persistence Failure Rate

```
persistence_failure = user_registered events with no utm_campaign / total user_registered
```
Currently: 100% failure (all user_registered events lack UTM)

## Bot Risk Score

```
bot_score(country) = (chapter_completed = 0 AND chapter_opened > 0) / chapter_opened
```
High score = suspicious - clicks but no completions.

## Reading Velocity

```
velocity(novel) = avg(time_spent_sec) on chapter_completed
velocity(chapter_n) = avg(time_spent_sec) where chapter_number=n
```
Low velocity (< 30s) = likely bot/skimmer.

## Author Health

```
publish_rate = novel_published / $pageview on author.novelpedia.net
comment_rate = comment_posted / novel_published
```
Currently: novel_published and comment_posted not firing.

## Registration Funnel (Broken)

```
registration_attribution_rate = user_registered with $initial_utm_campaign set / total user_registered
```
Currently: 0% (no $identify with UTM confirmed)
