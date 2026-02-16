from pyspark.sql import SparkSession, functions as F, Window

def read_csv(spark: SparkSession, name: str):
    return spark.read.option("header", True).option("inferSchema", True).csv(f"data/{name}.csv")

def main():
    spark = (
        SparkSession.builder
        .appName("pagila_spark_hw")
        .getOrCreate()
    )
    spark.sparkContext.setLogLevel("WARN")


    actor = read_csv(spark, "actor")
    film = read_csv(spark, "film")
    film_actor = read_csv(spark, "film_actor")
    category = read_csv(spark, "category")
    film_category = read_csv(spark, "film_category")
    inventory = read_csv(spark, "inventory")
    rental = read_csv(spark, "rental")
    payment = read_csv(spark, "payment")
    customer = read_csv(spark, "customer")
    address = read_csv(spark, "address")
    city = read_csv(spark, "city")

    # Parse timestamps (For Task 7) 

    rental = (
        rental
        .withColumn("rental_date_ts", F.to_timestamp("rental_date"))
        .withColumn("return_date_ts", F.to_timestamp("return_date"))
    )
    payment = payment.withColumn("payment_date_ts", F.to_timestamp("payment_date"))

# Task 1
# Output the number of movies in each category, sorted descending.

    t1 = (
        category.alias("c")
        .join(film_category.alias("fc"), F.col("fc.category_id") == F.col("c.category_id"), "inner")
        .join(film.alias("f"), F.col("f.film_id") == F.col("fc.film_id"), "inner")
        .groupBy(F.col("c.name").alias("category_name"))
        .agg(F.count(F.col("fc.film_id")).alias("movie_count"))
        .orderBy(F.col("movie_count").desc())
    )
    print("\n--- TASK 1 ---")
    t1.show(truncate=False)
    
# Task 2
# Output the 10 actors whose movies rented the most, sorted in descending order.

    t2 = (
        actor.alias("a")
        .join(film_actor.alias("fa"), F.col("fa.actor_id") == F.col("a.actor_id"), "inner")
        .join(inventory.alias("i"), F.col("i.film_id") == F.col("fa.film_id"), "inner")
        .join(rental.alias("r"), F.col("r.inventory_id") == F.col("i.inventory_id"), "inner")
        .groupBy(F.col("a.first_name").alias("first_name"), F.col("a.last_name").alias("last_name"))
        .agg(F.count(F.col("r.rental_id")).alias("rental_count"))
        .orderBy(F.col("rental_count").desc())
        .limit(10)
    )


    print("\n--- TASK 2 ---")
    t2.show(truncate=False)


# -- Task 3
# -- Output the category of movies on which the most money was spent.


    t3 = (
        category.alias("c")
        .join(film_category.alias("fc"), F.col("fc.category_id") == F.col("c.category_id"), "inner")
        .join(film.alias("f"), F.col("f.film_id") == F.col("fc.film_id"), "inner")
        .join(inventory.alias("i"), F.col("i.film_id") == F.col("f.film_id"), "inner")
        .join(rental.alias("r"), F.col("r.inventory_id") == F.col("i.inventory_id"), "inner")
        .join(payment.alias("p"), F.col("p.rental_id") == F.col("r.rental_id"), "inner")
        .groupBy(F.col("c.name").alias("category_name"))
        .agg(F.sum(F.col("p.amount")).alias("total_revenue"))
        .orderBy(F.col("total_revenue").desc())
        .limit(1)

        )

    
    print("\n--- TASK 3 ---")
    t3.show(truncate=False)


# -- Task 4
# -- Print the names of movies that are not in the inventory. 
# -- Write a query without using the IN operator.


    t4 = (
        film.alias("f")
        .join(inventory.alias("i"), F.col("i.film_id") == F.col("f.film_id"), "left")
        .filter(F.col("i.inventory_id").isNull())
        .select(F.col("f.title").alias("movie_title"))
    )

    print("\n--- TASK 4 ---")
    t4.show(truncate=False)


# -- Task 5
# -- Output the top 3 actors who have appeared the most in movies in the “Children” category. 
# -- If several actors have the same number of movies, output all of them.

    t5 = (
        actor.alias("a")
        .join(film_actor.alias("fa"), F.col("fa.actor_id") == F.col("a.actor_id"), "inner")
        .join(film_category.alias("fc"), F.col("fc.film_id") == F.col("fa.film_id"), "inner")
        .join(category.alias("c"), F.col("c.category_id") == F.col("fc.category_id"), "inner")
        .filter(F.col("c.name") == "Children")
        .groupBy(F.col("a.first_name").alias("first_name"), F.col("a.last_name").alias("last_name"))
        .agg(F.count(F.col("fa.film_id")).alias("movie_count"))
        .withColumn("rank", F.dense_rank().over(Window.orderBy(F.col("movie_count").desc())))
        .filter(F.col("rank") <= 3)
        .orderBy(F.col("movie_count").desc(), F.col("last_name").asc())
    )

    print("\n--- TASK 5 ---")
    t5.show(truncate=False)


# -- Task 6
# -- Output cities with the number of active 
# -- and inactive customers (active - customer.active = 1).
# -- Sort by the number of inactive customers in descending order.


    t6 = (
        customer.alias("c")
        .join(address.alias("a"), F.col("a.address_id") == F.col("c.address_id"), "inner")
        .join(city.alias("ci"), F.col("ci.city_id") == F.col("a.city_id"), "inner")
        .groupBy(F.col("ci.city").alias("city_name"))
        .agg(F.sum(F.when(F.col("c.active") == 1, 1).otherwise(0)).alias("active_customer"), F.sum(F.when(F.col("c.active") == 0, 1).otherwise(0)).alias("inactive_customer"))
        .orderBy(F.col("inactive_customer").desc(), F.col("city_name").asc())


    )

    print("\n--- TASK 6 ---")
    t6.show(truncate=False)




# -- Task 7
# -- Output the category of movies that have the highest number of total rental hours in the city 
# -- (customer.address_id in this city)
# --  and that start with the letter “a”. Do the same for cities that have a “-” in them. 
# -- Write everything in one query.

    t7_base = (
        rental.alias("r")
        .join(customer.alias("cu"), F.col("r.customer_id") == F.col("cu.customer_id"), "inner")
        .join(address.alias("ad"), F.col("cu.address_id") == F.col("ad.address_id"), "inner")
        .join(city.alias("ci"), F.col("ad.city_id") == F.col("ci.city_id"), "inner")
        .join(inventory.alias("i"), F.col("r.inventory_id") == F.col("i.inventory_id"), "inner")
        .join(film.alias("f"), F.col("i.film_id") == F.col("f.film_id"), "inner")
        .join(film_category.alias("fc"), F.col("f.film_id") == F.col("fc.film_id"), "inner")
        .join(category.alias("cat"), F.col("fc.category_id") == F.col("cat.category_id"), "inner")
    )


    t7_hours = (
        t7_base
        .withColumn("rental_ts", F.to_timestamp(F.col("r.rental_date")))
        .withColumn("return_ts", F.to_timestamp(F.col("r.return_date")))
        .filter(F.col("return_ts").isNotNull())
        .withColumn(
            "hours",
            (F.unix_timestamp("return_ts") - F.unix_timestamp("rental_ts")) / F.lit(3600.0)
        )
    )


    t7_filtered = (
        t7_hours
        .withColumn("city_name", F.col("ci.city"))
        .withColumn("category_name", F.col("cat.name"))
        .filter(
            (F.lower(F.col("city_name")).like("a%")) |
            (F.col("city_name").contains("-"))
        )
    )


    t7_summed = (
        t7_filtered
        .groupBy("city_name", "category_name")
        .agg(F.sum("hours").alias("total_hours"))
    )


    w_city = Window.partitionBy("city_name").orderBy(F.col("total_hours").desc())

    t7_result = (
        t7_summed
        .withColumn("rank_in_city", F.dense_rank().over(w_city))
        .filter(F.col("rank_in_city") == 1)
        .select(
            F.col("category_name").alias("category"),
            F.round(F.col("total_hours"), 2).alias("total_hours"),
            F.col("city_name").alias("city"),
        )
        .orderBy(F.col("total_hours").desc())
    )

    print("\n--- TASK 7 ---")
    t7_result.show(truncate=False)


    spark.stop()

if __name__ == "__main__":
    main()