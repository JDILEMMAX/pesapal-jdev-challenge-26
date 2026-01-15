const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;

/**
 * Execute a raw SQL query against the backend.
 *
 * Always returns a normalized result:
 *   - { ok: true, data }
 *   - { ok: false, error: { kind, message } }
 */
export async function executeQuery(sql) {
  if (!sql || typeof sql !== "string") {
    return {
      ok: false,
      error: {
        kind: "CLIENT",
        message: "No SQL query provided",
      },
    };
  }

  const url = `${API_BASE_URL}/api/query/?q=${encodeURIComponent(sql)}`;

  try {
    const response = await fetch(url, {
      method: "GET",
    });

    const contentType = response.headers.get("content-type") || "";

    // Backend sometimes returns HTML (404, CORS, DEBUG pages)
    if (!contentType.includes("application/json")) {
      const text = await response.text();
      console.error("Non-JSON backend response:", text);

      return {
        ok: false,
        error: {
          kind: "BACKEND",
          message: "Backend returned an unexpected response",
        },
      };
    }

    const payload = await response.json();

    if (!response.ok || payload.status === "ERROR") {
      return {
        ok: false,
        error: {
          kind: payload?.error?.type || "BACKEND",
          message: payload?.error?.message || "Query failed",
        },
      };
    }

    return {
      ok: true,
      data: payload.data,
    };
  } catch (err) {
    console.error("Network error:", err);

    return {
      ok: false,
      error: {
        kind: "NETWORK",
        message: "Unable to reach backend",
      },
    };
  }
}
