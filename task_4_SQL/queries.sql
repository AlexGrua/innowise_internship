-- Task 1
-- Output the number of movies in each category, sorted descending.

SELECT category.name as category_name, COUNT(film_category.film_id) AS movie_count
FROM category
JOIN film_category ON film_category.category_id = category.category_id
JOIN film ON film.film_id = film_category.film_id
GROUP BY category.name
ORDER BY  movie_count DESC;


-- Task 2
-- Output the 10 actors whose movies rented the most, sorted in descending order.

SELECT actor.first_name, actor.last_name,  COUNT(rental.rental_id) AS rental_count
FROM actor
JOIN film_actor ON actor.actor_id = film_actor.actor_id 
JOIN inventory ON film_actor.film_id = inventory.film_id
JOIN rental ON inventory.inventory_id = rental.inventory_id 
GROUP BY actor.last_name, actor.first_name, actor.actor_id
ORDER BY rental_count DESC
LIMIT 10;

-- Task 3
-- Output the category of movies on which the most money was spent.

SELECT category.name AS category_name, SUM(payment.amount) AS total_revenue
FROM category
JOIN film_category ON category.category_id = film_category.category_id
JOIN film ON film_category.film_id = film.film_id
JOIN inventory ON film.film_id = inventory.film_id
JOIN rental ON inventory.inventory_id = rental.inventory_id
JOIN payment ON rental.rental_id = payment.rental_id
GROUP BY category_name
ORDER BY total_revenue DESC
LIMIT 1;

-- Task 4
-- Print the names of movies that are not in the inventory. 
-- Write a query without using the IN operator.

SELECT title
FROM film
LEFT JOIN inventory ON film.film_id = inventory.film_id
WHERE inventory.film_id IS NULL;


-- Task 5
-- Output the top 3 actors who have appeared the most in movies in the “Children” category. 
-- If several actors have the same number of movies, output all of them.


SELECT first_name, last_name, movie_count
FROM (
	SELECT first_name, last_name, COUNT(*) AS movie_count,
		DENSE_RANK() OVER(ORDER BY COUNT(*) DESC) AS appearance_rank
	FROM actor
	JOIN film_actor ON actor.actor_id = film_actor.actor_id
	JOIN film_category ON film_actor.film_id = film_category.film_id
	JOIN category ON film_category.category_id = category.category_id
	WHERE category.name = 'Children' 
	
	GROUP BY first_name, last_name, actor.actor_id
	) as t
WHERE appearance_rank <=3
ORDER BY movie_count DESC, last_name ASC;


-- Task 6
-- Output cities with the number of active 
-- and inactive customers (active - customer.active = 1).
-- Sort by the number of inactive customers in descending order.

SELECT city, 
	SUM(CASE WHEN customer.active = 1 THEN 1 ELSE 0 END) AS active_customers,
	SUM(CASE WHEN customer.active = 0 THEN 1 ELSE 0 END) AS inactive_customers
FROM city
JOIN address ON city.city_id = address.city_id
JOIN customer ON address.address_id = customer.address_id
GROUP BY city
ORDER BY inactive_customers DESC, city ASC;


-- Task 7
-- Output the category of movies that have the highest number of total rental hours in the city 
-- (customer.address_id in this city)
--  and that start with the letter “a”. Do the same for cities that have a “-” in them. 
-- Write everything in one query.


WITH rental_hours AS (
    SELECT city.city, category.name AS category,
        EXTRACT(EPOCH FROM (rental.return_date - rental.rental_date)) / 3600 AS hours
    FROM rental
    JOIN customer ON rental.customer_id = customer.customer_id
    JOIN address ON customer.address_id = address.address_id
    JOIN city ON address.city_id = city.city_id
    JOIN inventory ON rental.inventory_id = inventory.inventory_id
    JOIN film ON inventory.film_id = film.film_id
    JOIN film_category ON film.film_id = film_category.film_id
    JOIN category ON film_category.category_id = category.category_id
    WHERE
        rental.return_date IS NOT NULL
        AND (city.city ILIKE 'a%' OR city.city LIKE '%-%')
),

summing AS (
    SELECT city, category, SUM(hours) AS total_hours
    FROM rental_hours
    GROUP BY city, category
),

ranked AS (
    SELECT city, category, total_hours,
        DENSE_RANK() OVER (PARTITION BY city ORDER BY total_hours DESC) AS rank_in_city
    FROM summing
)

SELECT category, ROUND(total_hours, 2), city
FROM ranked
WHERE rank_in_city = 1
ORDER BY total_hours DESC;





