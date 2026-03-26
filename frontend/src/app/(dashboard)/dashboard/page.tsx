"use client";
import { useEffect, useState } from "react";
import { listAlerts, listRecommendations } from "@/lib/api";
import type { Alert, AIRecommendation } from "@/types";
import { TrendingDown, TrendingUp, Sparkles, Bell } from "lucide-react";

export default function DashboardPage() {
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [recommendations, setRecommendations] = useState<AIRecommendation[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([listAlerts(true), listRecommendations()]).then(([a, r]) => {
      setAlerts(a.data.slice(0, 5));
      setRecommendations(r.data.slice(0, 5));
      setLoading(false);
    });
  }, []);

  if (loading) return <p className="text-gray-400">A carregar...</p>;

  return (
    <div className="space-y-8">
      <h1 className="text-2xl font-bold">Dashboard</h1>

      {/* KPI cards */}
      <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
        {[
          { label: "Alertas não lidos", value: alerts.length, icon: Bell, color: "text-orange-500" },
          { label: "Recomendações pendentes", value: recommendations.filter((r) => r.status === "pending").length, icon: Sparkles, color: "text-blue-500" },
        ].map(({ label, value, icon: Icon, color }) => (
          <div key={label} className="bg-white rounded-xl border p-5 flex items-center gap-4">
            <Icon className={color} size={28} />
            <div>
              <p className="text-2xl font-bold">{value}</p>
              <p className="text-sm text-gray-500">{label}</p>
            </div>
          </div>
        ))}
      </div>

      {/* Recent alerts */}
      <section>
        <h2 className="text-lg font-semibold mb-3">Alertas recentes</h2>
        <div className="space-y-2">
          {alerts.length === 0 && <p className="text-gray-400 text-sm">Sem alertas.</p>}
          {alerts.map((alert) => (
            <div key={alert.id} className="bg-white border rounded-xl p-4 flex items-start gap-3">
              {alert.alert_type === "price_drop" ? (
                <TrendingDown className="text-green-500 mt-0.5 shrink-0" size={18} />
              ) : (
                <TrendingUp className="text-red-500 mt-0.5 shrink-0" size={18} />
              )}
              <p className="text-sm text-gray-700">{alert.message}</p>
            </div>
          ))}
        </div>
      </section>

      {/* AI Recommendations */}
      <section>
        <h2 className="text-lg font-semibold mb-3">Recomendações AI</h2>
        <div className="space-y-2">
          {recommendations.length === 0 && <p className="text-gray-400 text-sm">Sem recomendações.</p>}
          {recommendations.map((rec) => (
            <div key={rec.id} className="bg-white border rounded-xl p-4">
              <div className="flex items-center justify-between mb-1">
                <span className="text-sm font-medium">Produto #{rec.product_id}</span>
                {rec.suggested_price && (
                  <span className="text-blue-600 font-bold">€{rec.suggested_price.toFixed(2)}</span>
                )}
              </div>
              <p className="text-sm text-gray-600">{rec.reasoning}</p>
            </div>
          ))}
        </div>
      </section>
    </div>
  );
}
