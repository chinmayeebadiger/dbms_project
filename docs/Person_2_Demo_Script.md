# Person 2 Demo Script

## Setup

Terminal 1:

```bash
cd backend
PYTHONPATH=. uvicorn app.main:app --reload --port 8000
```

Terminal 2:

```bash
cd frontend
npm install
cp .env.example .env
npm run dev
```

Open `http://localhost:5173`.

## Demonstration sequence

1. Open **Analyze migration**.
2. Keep or paste:

   ```sql
   ALTER TABLE customers DROP COLUMN email;
   UPDATE customers SET active = false;
   ```

3. Click **Analyze migration**.
4. Explain the Critical score, `DROP_COLUMN` data-loss finding, `UPDATE_WITHOUT_WHERE` mass-update finding, and safer alternatives.
5. Open **Migration history** and show the saved analysis ID and score.
6. Open the saved item to demonstrate the report can be retrieved by ID.
7. Open **Dashboard** and point out saved count, average score, and critical count.
8. Open **Knowledge graph** and explain Operation -> Object/Risk -> Severity/Alternative.
9. Return to Analyze and upload a `.sql` file containing `DROP TABLE audit_log;`.
10. Mention that SQL is analyzed only, never executed.

## Known limitation to state clearly

The current history adapter is in-memory for the Person 2 integration milestone. Restarting the backend clears history. Person 1’s PostgreSQL storage work should replace the adapter through the same history/detail/stats/graph API contract.
