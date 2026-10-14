-- Özellik tablosundaki müşterilerin gelecek dönem alışverişlerini say.
-- LEFT JOIN, gelecek dönemde hiç faturası olmayan müşterileri de korur.
SELECT
    f.customer_id,
    COUNT(DISTINCT i.invoice_id) AS future_invoice_count,
    CASE WHEN COUNT(DISTINCT i.invoice_id) = 0 THEN 1 ELSE 0 END AS no_purchase_90d
FROM snapshot_features AS f
LEFT JOIN invoices AS i
    ON f.customer_id = i.customer_id
    AND i.event_date >= :cutoff
    AND i.event_date < :target_end
GROUP BY f.customer_id
ORDER BY f.customer_id;
