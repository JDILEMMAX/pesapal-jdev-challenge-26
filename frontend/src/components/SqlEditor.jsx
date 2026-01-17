import { useEffect, useRef } from "react";

export default function SqlEditor({ sql, setSql, onExecute, isExecuting }) {
  const textareaRef = useRef(null);

  // Keyboard shortcut: Ctrl / Cmd + Enter
  useEffect(() => {
    function handleKeyDown(e) {
      const isCmdEnter = (e.ctrlKey || e.metaKey) && e.key === "Enter";

      if (isCmdEnter && !isExecuting) {
        e.preventDefault();
        if (sql.trim()) {
          onExecute(sql);
        }
      }
    }

    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [sql, onExecute, isExecuting]);

  return (
    <section className="panel sql-editor">
      {/* Header */}
      <header className="sql-editor-header">
        <span>SQL Editor</span>
        <span className="sql-editor-shortcut">Ctrl / Cmd + Enter to execute</span>
      </header>

      {/* Editor */}
      <textarea
        ref={textareaRef}
        value={sql}
        onChange={(e) => setSql(e.target.value)}
        placeholder="Enter SQL query…"
        spellCheck={false}
      />

      {/* Footer */}
      <footer className="sql-editor-footer">
        <button
          onClick={() => onExecute(sql)}
          disabled={!sql.trim() || isExecuting}
        >
          {isExecuting ? "Executing…" : "Run Query"}
        </button>
      </footer>
    </section>
  );
}
