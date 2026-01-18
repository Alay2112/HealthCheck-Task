import { useEffect, useState } from "react";

function App() {
  const [health, setHealth] = useState(null);
  const [logs, setLogs] = useState([]);
  const [error, setError] = useState("");
  const [checking, setChecking] = useState(false);

  const API_URL = import.meta.env.VITE_API_URL;

  // ✅ Call /health → measure response time → send to /status
  const checkHealth = async () => {
    setChecking(true);
    setError("");

    const startTime = performance.now();

    try {
      const res = await fetch(`${API_URL}/health`);
      const data = await res.json();

      const endTime = performance.now();
      const responseTime = endTime - startTime;

      setHealth(data);

      console.log(`✅ Health OK: ${Math.round(responseTime)}ms`);

      // ✅ Send response time to backend using /status API
      const statusRes = await fetch(`${API_URL}/status`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          status: "UP",
          response_time_ms: responseTime,
        }),
      });

      const statusData = await statusRes.json();
      setLogs(statusData.logs);
    } catch (err) {
      const endTime = performance.now();
      const responseTime = endTime - startTime;

      setError("Backend is not reachable");
      setHealth(null);

      console.log(`❌ Health Failed: ${Math.round(responseTime)}ms`);

      // ✅ Even log DOWN into backend
      try {
        const statusRes = await fetch(`${API_URL}/status`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            status: "DOWN",
            response_time_ms: responseTime,
          }),
        });

        const statusData = await statusRes.json();
        setLogs(statusData.logs);
      } catch (e) {
        console.log("Backend completely down, can't log status.");
      }
    } finally {
      setChecking(false);
    }
  };

  // ✅ Load initially
  useEffect(() => {
    checkHealth();
  }, []);

  return (
    <div
      style={{
        maxWidth: "1400px",
        margin: "0 auto",
        padding: "20px 15px",
        fontFamily: "Arial, sans-serif",
        color: "#000",
      }}
    >
      <h1
        style={{
          borderBottom: "2px solid #333",
          paddingBottom: "10px",
          fontSize: "clamp(24px, 5vw, 32px)",
        }}
      >
        Health Check Logger
      </h1>

      {/* ✅ Health Status */}
      <div
        style={{
          background: "#f5f5f5",
          padding: "20px",
          marginBottom: "20px",
          borderRadius: "5px",
        }}
      >
        <h2 style={{ fontSize: "clamp(18px, 4vw, 24px)" }}>
          Backend Health Status
        </h2>

        {error ? (
          <p style={{ color: "red", fontWeight: "bold" }}>{error}</p>
        ) : health ? (
          <div
            style={{
              background: "#fff",
              padding: "15px",
              border: "1px solid #ddd",
              borderRadius: "3px",
            }}
          >
            <p>
              <strong>Status:</strong> {health.status}
            </p>
            <p>
              <strong>Timestamp:</strong> {health.timestamp}
            </p>
            <p>
              <strong>Timezone:</strong> {health.timezone}
            </p>
          </div>
        ) : (
          <p>Checking...</p>
        )}

        <button
          onClick={checkHealth}
          disabled={checking}
          style={{
            padding: "12px 30px",
            cursor: checking ? "not-allowed" : "pointer",
            background: checking ? "#ccc" : "#007bff",
            color: "white",
            border: "none",
            borderRadius: "3px",
            marginTop: "15px",
          }}
        >
          {checking ? "Checking..." : "Check Health"}
        </button>
      </div>

      {/* ✅ Logs Table */}
      <div style={{ background: "#f5f5f5", padding: "20px", borderRadius: "5px" }}>
        <h2 style={{ marginBottom: "15px" }}>Connection Logs</h2>

        {logs.length === 0 ? (
          <p>No logs available</p>
        ) : (
          <div style={{ overflowX: "auto" }}>
            <table
              style={{
                width: "100%",
                borderCollapse: "collapse",
                background: "white",
                minWidth: "600px",
              }}
            >
              <thead>
                <tr style={{ background: "#333", color: "white" }}>
                  <th style={{ padding: "12px 10px", textAlign: "left" }}>ID</th>
                  <th style={{ padding: "12px 10px", textAlign: "left" }}>Status</th>
                  <th style={{ padding: "12px 10px", textAlign: "left" }}>
                    Response Time (ms)
                  </th>
                  <th style={{ padding: "12px 10px", textAlign: "left" }}>
                    Timestamp
                  </th>
                </tr>
              </thead>

              <tbody>
                {logs.map((log) => (
                  <tr key={log.id} style={{ borderBottom: "1px solid #ddd" }}>
                    <td style={{ padding: "10px" }}>{log.id}</td>

                    <td style={{ padding: "10px" }}>
                      <span
                        style={{
                          padding: "6px 12px",
                          borderRadius: "3px",
                          background: log.status === "UP" ? "#d4edda" : "#f8d7da",
                          color: log.status === "UP" ? "#155724" : "#721c24",
                          fontWeight: "bold",
                          display: "inline-block",
                        }}
                      >
                        {log.status}
                      </span>
                    </td>

                    <td style={{ padding: "10px" }}>
                      {Math.round(log.response_time_ms)}
                    </td>

                    <td style={{ padding: "10px" }}>
                      {new Date(log.checked_at).toLocaleString("en-IN", {
                        timeZone: "Asia/Kolkata",
                      })}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;
