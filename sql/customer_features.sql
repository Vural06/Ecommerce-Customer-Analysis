-- Gözlem aralığı: [observation_start, cutoff). cutoff anı geleceğe aittir.
-- event_date faturanın son kalem zamanıdır: toplam tutar o anda kullanılabilir.
SELECT
    customer_id,
    CAST(julianday(:cutoff) - julianday(MAX(event_date)) AS INTEGER) AS recency_days,
    COUNT(DISTINCT invoice_id) AS frequency_180d,
    SUM(amount_gbp) AS monetary_180d_gbp,
    AVG(amount_gbp) AS average_invoice_amount_gbp,
    SUM(total_quantity) AS quantity_180d,
    MIN(event_date) AS first_observed_purchase,
    MAX(event_date) AS last_observed_purchase
FROM invoices
WHERE event_date >= :observation_start AND event_date < :cutoff
GROUP BY customer_id
ORDER BY customer_id;
