"use client";
import { useState } from "react";
import { signIn } from "@/lib/cognito";

export default function LoginPage() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleLogin = async () => {
    setLoading(true);
    setError(null);
    try {
      // Redirects to Azure AD B2C hosted UI (sign-in page).
      // On success, B2C redirects back to /dashboard with auth token.
      await signIn();
    } catch (err: unknown) {
      setLoading(false);
      setError(err instanceof Error ? err.message : "Login falhou");
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="w-full max-w-md bg-white rounded-2xl shadow-lg p-8">
        <h1 className="text-2xl font-bold text-center mb-2">PriceWatch.pt</h1>
        <p className="text-center text-gray-500 mb-8">
          Monitorização de preços da concorrência
        </p>

        {error && (
          <p className="mb-4 text-center text-red-600 text-sm">{error}</p>
        )}

        <button
          onClick={handleLogin}
          disabled={loading}
          className="w-full bg-blue-600 text-white rounded-lg py-3 font-medium hover:bg-blue-700 disabled:opacity-50 transition-colors"
        >
          {loading ? "A redirecionar..." : "Entrar"}
        </button>

        <p className="text-center mt-4 text-sm text-gray-500">
          Ainda não tem conta?{" "}
          <button
            onClick={handleLogin}
            className="text-blue-600 hover:underline"
          >
            Criar conta
          </button>
          <span className="block text-xs text-gray-400 mt-1">
            (O mesmo botão permite registo e login via Azure AD B2C)
          </span>
        </p>
      </div>
    </div>
  );
}
