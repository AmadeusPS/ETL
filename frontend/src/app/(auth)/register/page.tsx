"use client";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { getCurrentAccount, signIn } from "@/lib/cognito";
import { registerUser } from "@/lib/api";

/**
 * Register page – handles the post-B2C-redirect flow.
 *
 * Azure AD B2C manages the actual sign-up UI. This page:
 *  1. Detects if the user just came back from a B2C redirect (has account)
 *  2. Calls our backend /auth/register to create the local DB record
 *  3. Redirects to /dashboard
 *
 * If no account is detected yet, it triggers the B2C redirect.
 */
export default function RegisterPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    (async () => {
      try {
        const account = await getCurrentAccount();
        if (account) {
          // Came back from B2C with a valid session → sync to backend
          await registerUser();
          router.push("/dashboard");
        } else {
          // Not authenticated yet → redirect to B2C sign-up/sign-in
          await signIn();
        }
      } catch (err: unknown) {
        setLoading(false);
        setError(err instanceof Error ? err.message : "Registo falhou");
      }
    })();
  }, [router]);

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="w-full max-w-md bg-white rounded-2xl shadow-lg p-8 text-center">
        <h1 className="text-2xl font-bold mb-2">PriceWatch.pt</h1>
        {error ? (
          <>
            <p className="text-red-600 text-sm mt-4">{error}</p>
            <a href="/login" className="mt-4 inline-block text-blue-600 hover:underline text-sm">
              Voltar ao login
            </a>
          </>
        ) : (
          <p className="text-gray-500 mt-4">
            {loading ? "A completar registo..." : "A redirecionar..."}
          </p>
        )}
      </div>
    </div>
  );
}
