export default function ResultGrid({ result, error }) {
  let content;

  if (error) {
    content = <pre className="error-message">{error}</pre>;
  } else if (!result || (Array.isArray(result) && result.length === 0)) {
    content = <div className="error-message">No results</div>;
  } else if (Array.isArray(result)) {
    const columns = Object.keys(result[0] || {});

    content = (
      <div className="result-table-wrapper">
        <table>
          <thead>
            <tr>
              {columns.map((col) => (
                <th key={col}>{col}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {result.map((row, idx) => (
              <tr key={idx}>
                {columns.map((col) => (
                  <td key={col}>{String(row[col])}</td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    );
  } else {
    content = <pre className="info-message">{String(result)}</pre>;
  }

  return (
    <section className="panel result-grid">
      <h3>Query Result</h3>
      {content}
    </section>
  );
}
