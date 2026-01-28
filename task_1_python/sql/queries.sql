-- name: rooms_with_students_count
SELECT r.id, r.name, COUNT(s.id) as students_count
FROM rooms2 r
LEFT JOIN students2 s ON s.room_id = r.id
GROUP BY r.id, r.name
ORDER BY r.id;

-- name: rooms_with_smallest_avg_age
SELECT r.id, r.name,
       AVG(EXTRACT(YEAR FROM AGE(CURRENT_DATE, s.birthday))) as avg_age
FROM rooms2 r
JOIN students2 s ON s.room_id = r.id
GROUP BY r.id, r.name
ORDER BY avg_age ASC
LIMIT %s;

-- name: rooms_with_largest_age_diff
WITH t AS (
    SELECT r.id, r.name,
           MIN(EXTRACT(YEAR FROM AGE(CURRENT_DATE, s.birthday))) as min_age,
           MAX(EXTRACT(YEAR FROM AGE(CURRENT_DATE, s.birthday))) as max_age
    FROM rooms2 r
    JOIN students2 s ON s.room_id = r.id
    GROUP BY r.id, r.name
)
SELECT id, name, (max_age - min_age) AS age_diff, min_age, max_age
FROM t
ORDER BY age_diff DESC
LIMIT %s;

-- name: rooms_with_mixed_sex
SELECT r.id, r.name, COUNT(DISTINCT s.sex) AS sex_count
FROM rooms2 r
JOIN students2 s ON r.id = s.room_id
GROUP BY r.id, r.name
HAVING COUNT(DISTINCT s.sex) = 2
ORDER BY r.id;
