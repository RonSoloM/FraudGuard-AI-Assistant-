FRAUD_PerMonth_SQL = """
SELECT
    COALESCE(FORMAT(Trans_Date_Trans_Time, 'yyyy-MM'), 'Grand Total') AS Month,
    SUM(CASE WHEN Is_fraud = 1 THEN 1 ELSE 0 END) AS Fraudulent_Transactions,
    SUM(CASE WHEN Is_fraud = 0 THEN 1 ELSE 0 END) AS Total_Transactions,
    CASE
        WHEN SUM(CASE WHEN Is_fraud = 0 THEN 1 ELSE 0 END) = 0 THEN '0.00%'
        ELSE FORMAT(
            CAST(SUM(CASE WHEN Is_fraud = 1 THEN 1 ELSE 0 END) AS FLOAT) /
            SUM(CASE WHEN Is_fraud = 0 THEN 1 ELSE 0 END) * 100, 'N2'
        ) + '%'
    END AS Fraudulent_Ratio
FROM [dbo].[CustomerTransactions]
GROUP BY GROUPING SETS (
    (FORMAT(Trans_Date_Trans_Time, 'yyyy-MM')),
    ()
)
ORDER BY
    CASE WHEN FORMAT(Trans_Date_Trans_Time, 'yyyy-MM') IS NULL THEN 1 ELSE 0 END,
    COALESCE(FORMAT(Trans_Date_Trans_Time, 'yyyy-MM'), 'Grand Total')
"""

GENERIC_ALL_DATA_SQL = "SELECT * FROM [dbo].[CustomerTransactions]"

CATEGORY_VOLUME_SQL = """
SELECT
	Category,
	FORMAT(SUM(Amount),'N0') AS Total_Amount,
                    	FORMAT(SUM(CASE WHEN Is_Fraud = 1 THEN Amount ELSE 0 END),'N0') AS Fraudulent_Amount,
	FORMAT(ROUND((SUM(CASE WHEN Is_Fraud = 1 THEN Amount ELSE 0 END) / NULLIF(SUM(Amount), 0)) * 100, 2), 'N0') + '%' AS Fraud_Ratio
FROM
	[dbo].[CustomerTransactions]
GROUP BY
	Category
ORDER BY
	(SUM(CASE WHEN Is_Fraud = 1 THEN Amount ELSE 0 END) / NULLIF(SUM(Amount), 0)) DESC
"""

INTENTS = {
    "fraud_analysis": {
        "examples": [
            "Show monthly fraud analysis summary.",
            "Display the number of fraudulent and total transactions per month.",
            "Summarize fraud statistics by month and overall."
        ],
        "query": FRAUD_PerMonth_SQL
    },
    "all_data": {
        "examples": [
            "Show all customer transactions.",
            "Display the entire CustomerTransactions table.",
            "List every transaction record.",
            "Get all transaction data."
        ],
        "query": GENERIC_ALL_DATA_SQL
    },
    "category_volume": {
        "examples": [
            "Show total and fraudulent transaction amounts by category.",
            "Display the total and fraudulent transaction amounts by category.",
            "Show fraudulent transaction amounts by category.",
            "Show total transaction amounts by category."
        ],
        "query": CATEGORY_VOLUME_SQL
    },
}
