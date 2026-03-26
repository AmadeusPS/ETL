"use client";
import { useEffect, useState } from "react";
import { listRecommendations, actionRecommendation } from "@/lib/api";
import type { AIRecommendation } from "@/types";
import { CheckCircle, XCircle, Zap } from "lucide-react";
import clsx from "clsx";

const STATUS_COLORS: Record<string, string> = {
  pending: "bg-yellow-100 text-yellow-700",
  accepted: "bg-green-100 text-green-700",
  rejected: "bg-red-100 text-red-700",
  applied: "bg-blue-100 text-blue-700",
};

export default function RecommendationsPage() {
  const [recs, setRecs] = useState<AIRecommendation[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    listRecommendations().then((r) => {
      setRecs(r.data);
      setLoading(false);
    });
  }, []);

  const handleAction = async (id: number, status: "accepted" | "rejected" | "applied") => {
    await actionRecommendation(id, status);
    setRecs((prev) => prev.map((r) => (r.id === id ? { ...r, status } : r)));
  };

  if (loading) return <p className="text-gray-400">A carregar...</p>;

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">Recomendações AI</h1>
      <div className="space-y-3">
        {recs.length === 0 && <p className="text-gray-400 text-sm">Sem recomendações disponíveis.</p>}
        {recs.map((rec) => (
          <div key={rec.id} className="bg-white border rounded-xl p-5">
            <div className="flex items-start justify-between gap-4">
              <div className="flex-1">
                <div className="flex items-center gap-2 mb-2">
                  <Zap className="text-yellow-500" size={16} />
                  <span className="text-sm font-semibold">Produto #{rec.product_id}</span>
                  <span className={clsx("text-xs px-2 py-0.5 rounded-full font-medium", STATUS_COLORS[rec.status])}>
                    {rec.status}
                  </span>
                </div>
                {rec.suggested_price != null && (
                  <p className="text-xl font-bold text-blue-600 mb-1">
                    Preço sugerido: €{rec.suggested_price.toFixed(2)}
                  </p>
                )}
                <p className="text-sm text-gray-600">{rec.reasoning}</p>
                <p className="text-xs text-gray-400 mt-2">{new Date(rec.created_at).toLocaleString("pt-PT")}</p>
              </div>

              {rec.status === "pending" && (
                <div className="flex flex-col gap-2 shrink-0">
                  <button
                    onClick={() => handleAction(rec.id, "applied")}
                    className="flex items-center gap-1 bg-blue-600 text-white rounded-lg px-3 py-1.5 text-xs font-medium hover:bg-blue-700"
                  >
                    <Zap size={12} /> Aplicar
                  </button>
                  <button
                    onClick={() => handleAction(rec.id, "accepted")}
                    className="flex items-center gap-1 text-green-600 border border-green-300 rounded-lg px-3 py-1.5 text-xs font-medium hover:bg-green-50"
                  >
                    <CheckCircle size={12} /> Aceitar
                  </button>
                  <button
                    onClick={() => handleAction(rec.id, "rejected")}
                    className="flex items-center gap-1 text-red-500 border border-red-200 rounded-lg px-3 py-1.5 text-xs font-medium hover:bg-red-50"
                  >
                    <XCircle size={12} /> Rejeitar
                  </button>
                </div>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
