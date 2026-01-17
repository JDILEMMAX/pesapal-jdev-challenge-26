export default function ResultGrid({ result, error }) {
  let content;

  if (error) {
    content = <div className="error-message">{error}</div>;
  } else if (!result) {
    content = <div className="info-message">No results yet</div>;
  } else {
    const data = Array.isArray(result)
      ? result
      : Array.isArray(result.data)
      ? result.data
      : [];

    const message = result?.message;
    const warning = result?.warning;

    content = (
      <>
        {/* Informational message */}
        {message && <div className="info-message">{message}</div>}

        {/* Row count */}
        {data.length > 0 && (
          <div className="info-message">
            {data.length} row{data.length > 1 ? "s" : ""}
          </div>
        )}

        {/* Result table */}
        {data.length > 0 ? (
          <div className="result-table-wrapper">
            <table>
              <thead>
                <tr>
                  {Object.keys(data[0]).map((col) => (
                    <th key={col}>{col}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {data.map((row, idx) => (
                  <tr key={idx}>
                    {Object.keys(row).map((col) => (
                      <td key={col}>{String(row[col])}</td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          !message && <div className="info-message">Query executed successfully (0 rows)</div>
        )}

        {/* Warning message */}
        {warning && <div className="warning">{warning}</div>}
      </>
    );
  }

  return (
    <section className="panel result-grid">
      <h3>Query Result</h3>
      {content}
    </section>
  );
}
