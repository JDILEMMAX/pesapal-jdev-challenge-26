// src/components/TableList.jsx
export default function TableList({
  tables = [],
  onSelect = () => {},
}) {
  return (
    <section className="panel table-list">
      <header className="table-list-header">
        <h3>Tables</h3>
        <span className="table-list-meta">
          {tables.length} detected
        </span>
      </header>

      <div className="table-list-body">
        {tables.length === 0 ? (
          <div className="table-list-empty">
            No tables loaded
          </div>
        ) : (
          <ul className="table-list-items">
            {tables.map((table) => (
              <li
                key={table}
                className="table-list-item"
                onClick={() => onSelect(table)}
                tabIndex={0}
                role="button"
                onKeyDown={(e) => {
                  if (e.key === "Enter") onSelect(table);
                }}
              >
                {table}
              </li>
            ))}
          </ul>
        )}
      </div>
    </section>
  );
}
