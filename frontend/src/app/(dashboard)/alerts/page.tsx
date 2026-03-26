"use client";
import { useEffect, useState } from "react";
import { listAlerts, markAlertRead } from "@/lib/api";
import type { Alert } from "@/types";
import { TrendingDown, TrendingUp, Package, AlertCircle } from "lucide-react";
import clsx from "clsx";

const ICONS: Record<string, React.ReactNode> = {
  price_drop: <TrendingDown className="text-green-500" size={18} />,
  price_increase: <TrendingUp className="text-red-500" size={18} />,
  new_product: <Package className="text-blue-500" size={18} />,
  out_of_stock: <AlertCircle className="text-orange-400" size={18} />,
  back_in_stock: <Package className="text-teal-500" size={18} />,
};

export default function AlertsPage() {
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    listAlerts().then((r) => {
      setAlerts(r.data);
      setLoading(false);
    });
  }, []);

  const handleRead = async (id: number) => {
    await markAlertRead(id);
    setAlerts((prev) => prev.map((a) => (a.id === id ? { ...a, is_read: true } : a)));
  };

  if (loading) return <p className="text-gray-400">A carregar...</p>;

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">Alertas</h1>
      <div className="space-y-2">
        {alerts.length === 0 && <p className="text-gray-400 text-sm">Sem alertas.</p>}
        {alerts.map((alert) => (
          <div
            key={alert.id}
            className={clsx(
              "bg-white border rounded-xl p-4 flex items-start justify-between gap-3",
              !alert.is_read && "border-blue-200 bg-blue-50"
            )}
          >
            <div className="flex items-start gap-3">
              <span className="mt-0.5 shrink-0">{ICONS[alert.alert_type] ?? <AlertCircle size={18} />}</span>
              <div>
                <p className="text-sm text-gray-800">{alert.message}</p>
                <p className="text-xs text-gray-400 mt-1">{new Date(alert.created_at).toLocaleString("pt-PT")}</p>
              </div>
            </div>
            {!alert.is_read && (
              <button
                onClick={() => handleRead(alert.id)}
                className="text-xs text-blue-600 hover:underline shrink-0"
              >
                Marcar lido
              </button>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
