import { redirect } from "next/navigation";

// Root redirects to dashboard (auth guard handled by middleware/layout)
export default function Home() {
  redirect("/dashboard");
}
