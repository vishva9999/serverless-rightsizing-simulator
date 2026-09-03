/**
 * Mock data for Phase 1 dashboard.
 * All values are synthetic — they do NOT represent real AWS data.
 * These will be replaced by real API data in future phases.
 */

// ── Summary Card Data ─────────────────────────────────────────────────────────
export const summaryMetrics = {
  currentMonthlyCost:  { value: "$2,847.50", change: "+4.2%",  trend: "up",   label: "Current Monthly Cost" },
  optimizedMonthlyCost:{ value: "$1,923.10", change: "-32.4%", trend: "down", label: "Optimized Monthly Cost" },
  estimatedSavings:    { value: "$924.40",   change: "+28.1%", trend: "up",   label: "Estimated Savings" },
  averageLatency:      { value: "142 ms",    change: "-8.3%",  trend: "down", label: "Avg. Latency (p95)" },
  availability:        { value: "99.94%",    change: "+0.01%", trend: "up",   label: "Availability" },
  monthlyRequests:     { value: "4.2M",      change: "+12.7%", trend: "up",   label: "Monthly Requests" },
}

// ── Cost Comparison Chart ─────────────────────────────────────────────────────
export const costComparisonData = [
  { month: "Mar", current: 2610, optimized: 1820 },
  { month: "Apr", current: 2750, optimized: 1870 },
  { month: "May", current: 2680, optimized: 1800 },
  { month: "Jun", current: 2920, optimized: 1950 },
  { month: "Jul", current: 2780, optimized: 1900 },
  { month: "Aug", current: 2847, optimized: 1923 },
]

// ── Latency Trend Chart ───────────────────────────────────────────────────────
export const latencyTrendData = [
  { day: "Week 1", p50: 95,  p95: 148, p99: 210 },
  { day: "Week 2", p50: 92,  p95: 142, p99: 195 },
  { day: "Week 3", p50: 101, p95: 160, p99: 228 },
  { day: "Week 4", p50: 88,  p95: 135, p99: 188 },
  { day: "Week 5", p50: 94,  p95: 142, p99: 202 },
  { day: "Week 6", p50: 90,  p95: 138, p99: 195 },
]

// ── Request Volume Chart ──────────────────────────────────────────────────────
export const requestVolumeData = [
  { time: "00:00", requests: 1200 },
  { time: "03:00", requests: 580  },
  { time: "06:00", requests: 890  },
  { time: "09:00", requests: 3400 },
  { time: "12:00", requests: 4200 },
  { time: "15:00", requests: 3900 },
  { time: "18:00", requests: 3100 },
  { time: "21:00", requests: 1800 },
  { time: "24:00", requests: 1100 },
]

// ── Recent Activity ───────────────────────────────────────────────────────────
export const recentActivity = [
  { id: 1, event: "Simulation scenario created",     time: "2 min ago",  status: "success" },
  { id: 2, event: "Traffic spike detected (9am)",    time: "14 min ago", status: "warning" },
  { id: 3, event: "CSV dataset loaded (2880 rows)",  time: "1 hr ago",   status: "success" },
  { id: 4, event: "API server started on port 8000", time: "1 hr ago",   status: "success" },
  { id: 5, event: "Phase 1 foundation completed",    time: "2 hrs ago",  status: "success" },
]
