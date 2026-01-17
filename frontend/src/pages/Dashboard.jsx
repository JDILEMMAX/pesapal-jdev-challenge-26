import { useState, useEffect } from "react";
import { executeQuery } from "../api/dbClient";

import SqlEditor from "../components/SqlEditor";
import ResultGrid from "../components/ResultGrid";
import TableList from "../components/TableList";

export default function Dashboard() {
  const [queryResult, setQueryResult] = useState(null);
  const [queryError, setQueryError] = useState(null);
  const [isExecuting, setIsExecuting] = useState(false);
  const [tables, setTables] = useState([]);
  const [sql, setSql] = useState(""); // bind to SqlEditor

  // Load tables on mount
  useEffect(() => {
    async function loadTables() {
      try {
        const result = await executeQuery("SHOW TABLES;");
        if (result.ok && Array.isArray(result.data.data)) {
          setTables(result.data.data.map((row) => row.table_name));
        }
      } catch (err) {
        console.error("Failed to load tables", err);
      }
    }

    loadTables();
  }, []);

  async function handleExecute(customSql) {
    setIsExecuting(true);
    setQueryError(null);
    setQueryResult(null);

    const execSql = customSql ?? sql;

    const result = await executeQuery(execSql);

    if (!result.ok) {
      setQueryError(result.error.message);
    } else {
      setQueryResult(result.data);

      // If SHOW TABLES executed, update TableList
      const normalizedSql = execSql.trim().toUpperCase();
      if (normalizedSql.startsWith("SHOW TABLES")) {
        const newTables = Array.isArray(result.data.data)
          ? result.data.data.map((row) => row.table_name)
          : [];
        setTables(newTables);
      }
    }

    setIsExecuting(false);
  }

  function handleTableSelect(tableName) {
    const newSql = `SELECT * FROM ${tableName};`;
    setSql(newSql);
  }

  return (
    <div className="app-container">
      {/* Sidebar */}
      <aside className="sidebar">
        <TableList tables={tables} onSelect={handleTableSelect} />
      </aside>

      {/* Main workspace */}
      <main className="main-content">
        <SqlEditor
          sql={sql}
          setSql={setSql}
          onExecute={handleExecute}
          isExecuting={isExecuting}
        />
        <ResultGrid result={queryResult} error={queryError} />
      </main>
    </div>
  );
}
