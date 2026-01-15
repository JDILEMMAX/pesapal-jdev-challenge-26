import { useState } from "react";
import { executeQuery } from "../api/dbClient";

import SqlEditor from "../components/SqlEditor";
import ResultGrid from "../components/ResultGrid";
import TableList from "../components/TableList";

export default function Dashboard() {
  const [queryResult, setQueryResult] = useState(null);
  const [queryError, setQueryError] = useState(null);
  const [isExecuting, setIsExecuting] = useState(false);

  async function handleExecute(sql) {
    setIsExecuting(true);
    setQueryError(null);
    setQueryResult(null);

    const result = await executeQuery(sql);

    if (!result.ok) {
      setQueryError(result.error.message);
    } else {
      setQueryResult(result.data);
    }

    setIsExecuting(false);
  }

  return (
    <div className="app-container">
      {/* Sidebar */}
      <aside className="sidebar">
        <TableList />
      </aside>

      {/* Main workspace */}
      <main className="main-content">
        <SqlEditor
          onExecute={handleExecute}
          isExecuting={isExecuting}
        />
        <ResultGrid
          result={queryResult}
          error={queryError}
        />
      </main>
    </div>
  );
}
