"use client";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { LayoutDashboard, Package, Bell, Sparkles, LogOut } from "lucide-react";
import { signOut } from "@/lib/cognito";
import { useRouter } from "next/navigation";
import clsx from "clsx";

const NAV = [
  { href: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
  { href: "/products", label: "Produtos", icon: Package },
  { href: "/alerts", label: "Alertas", icon: Bell },
  { href: "/recommendations", label: "Recomendações AI", icon: Sparkles },
];

export default function Sidebar() {
  const pathname = usePathname();
  const router = useRouter();

  const handleLogout = async () => {
    await signOut();
    router.push("/login");
  };

  return (
    <aside className="w-60 min-h-screen bg-white border-r flex flex-col py-6 px-4">
      <div className="mb-8 px-2">
        <span className="text-xl font-bold text-blue-600">PriceWatch</span>
        <span className="text-xl font-bold text-gray-800">.pt</span>
      </div>

      <nav className="flex-1 space-y-1">
        {NAV.map(({ href, label, icon: Icon }) => (
          <Link
            key={href}
            href={href}
            className={clsx(
              "flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition-colors",
              pathname === href
                ? "bg-blue-50 text-blue-700"
                : "text-gray-600 hover:bg-gray-100 hover:text-gray-900"
            )}
          >
            <Icon size={18} />
            {label}
          </Link>
        ))}
      </nav>

      <button
        onClick={handleLogout}
        className="flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium text-gray-500 hover:bg-gray-100 hover:text-gray-900 transition-colors"
      >
        <LogOut size={18} />
        Sair
      </button>
    </aside>
  );
}
