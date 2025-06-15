CREATE OR REPLACE PROCEDURE init_table()
LANGUAGE plpgsql
AS $$
BEGIN
  CREATE SCHEMA IF NOT EXISTS bronze;
  CREATE SCHEMA IF NOT EXISTS silver;
  CREATE SCHEMA IF NOT EXISTS gold;

  CREATE TABLE IF NOT EXISTS bronze.performances (
    time           timestamptz,
    cpu_usage      numeric(5,2),
    memory_usage   numeric(5,2),
    cpu_interrupts bigint,
    cpu_calls      bigint,
    memory_used    numeric(5,2),
    memory_free    numeric(5,2),
    bytes_sent     bigint,
    bytes_received bigint,
    disk_usage     numeric(5,2)
  );

  CREATE TABLE IF NOT EXISTS silver.performances (
    time           timestamptz,
    cpu_usage      numeric(5,2),
    memory_usage   numeric(5,2),
    cpu_interrupts bigint,
    cpu_calls      bigint,
    memory_used    numeric(5,2),
    memory_free    numeric(5,2),
    bytes_sent     bigint,
    bytes_received bigint,
    disk_usage     numeric(5,2)
  );

END;
$$;

CALL init_performance_pipeline();
