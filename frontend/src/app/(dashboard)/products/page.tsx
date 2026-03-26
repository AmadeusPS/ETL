"use client";
import { useEffect, useState } from "react";
import { listProducts, createProduct, deleteProduct } from "@/lib/api";
import type { Product } from "@/types";
import { Plus, Trash2 } from "lucide-react";

export default function ProductsPage() {
  const [products, setProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState({ name: "", sku: "", category: "", current_price: "", target_margin: "" });

  const load = () =>
    listProducts().then((r) => {
      setProducts(r.data);
      setLoading(false);
    });

  useEffect(() => { load(); }, []);

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    await createProduct({
      name: form.name,
      sku: form.sku || undefined,
      category: form.category || undefined,
      current_price: form.current_price ? parseFloat(form.current_price) : undefined,
      target_margin: form.target_margin ? parseFloat(form.target_margin) : undefined,
    });
    setForm({ name: "", sku: "", category: "", current_price: "", target_margin: "" });
    setShowForm(false);
    load();
  };

  const handleDelete = async (id: number) => {
    await deleteProduct(id);
    setProducts((prev) => prev.filter((p) => p.id !== id));
  };

  if (loading) return <p className="text-gray-400">A carregar...</p>;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">Os meus produtos</h1>
        <button
          onClick={() => setShowForm(!showForm)}
          className="flex items-center gap-2 bg-blue-600 text-white rounded-lg px-4 py-2 text-sm font-medium hover:bg-blue-700"
        >
          <Plus size={16} /> Adicionar produto
        </button>
      </div>

      {showForm && (
        <form onSubmit={handleCreate} className="bg-white border rounded-xl p-5 grid grid-cols-2 gap-4">
          {[
            { key: "name", label: "Nome *", type: "text", required: true },
            { key: "sku", label: "SKU", type: "text", required: false },
            { key: "category", label: "Categoria", type: "text", required: false },
            { key: "current_price", label: "Preço atual (€)", type: "number", required: false },
            { key: "target_margin", label: "Margem objetivo (%)", type: "number", required: false },
          ].map(({ key, label, type, required }) => (
            <div key={key}>
              <label className="block text-sm font-medium mb-1">{label}</label>
              <input
                type={type}
                required={required}
                value={form[key as keyof typeof form]}
                onChange={(e) => setForm((prev) => ({ ...prev, [key]: e.target.value }))}
                className="w-full border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
          ))}
          <div className="col-span-2 flex gap-3">
            <button type="submit" className="bg-blue-600 text-white rounded-lg px-4 py-2 text-sm font-medium hover:bg-blue-700">
              Guardar
            </button>
            <button type="button" onClick={() => setShowForm(false)} className="text-gray-500 text-sm hover:underline">
              Cancelar
            </button>
          </div>
        </form>
      )}

      <div className="bg-white border rounded-xl overflow-hidden">
        <table className="w-full text-sm">
          <thead className="bg-gray-50 border-b">
            <tr>
              {["Nome", "SKU", "Categoria", "Preço", "Margem", ""].map((h) => (
                <th key={h} className="text-left px-4 py-3 font-medium text-gray-600">{h}</th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y">
            {products.length === 0 && (
              <tr><td colSpan={6} className="px-4 py-6 text-center text-gray-400">Sem produtos.</td></tr>
            )}
            {products.map((p) => (
              <tr key={p.id} className="hover:bg-gray-50">
                <td className="px-4 py-3 font-medium">{p.name}</td>
                <td className="px-4 py-3 text-gray-500">{p.sku ?? "—"}</td>
                <td className="px-4 py-3 text-gray-500">{p.category ?? "—"}</td>
                <td className="px-4 py-3">{p.current_price != null ? `€${p.current_price.toFixed(2)}` : "—"}</td>
                <td className="px-4 py-3">{p.target_margin != null ? `${p.target_margin}%` : "—"}</td>
                <td className="px-4 py-3">
                  <button onClick={() => handleDelete(p.id)} className="text-gray-400 hover:text-red-500">
                    <Trash2 size={16} />
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
