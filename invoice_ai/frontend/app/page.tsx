import { getServerSession } from "next-auth";
import { redirect } from "next/navigation";
import { authOptions } from "@/lib/auth";

export default async function Home() {
  const session = await getServerSession(authOptions);

  if (session) {
    redirect("/dashboard");
  }

  return (
    <main className="p-10 font-sans">
      <h1 className="text-3xl font-bold">Invoice AI</h1>

      <p className="mt-4 text-gray-600">
        AI-powered invoice processing platform
      </p>

      <div className="mt-6 space-y-2">
        <div>✔ Multi-tenant SaaS</div>
        <div>✔ Token-based AI billing</div>
        <div>✔ Fraud & compliance checks</div>
      </div>

      <a
        href="/api/auth/signin"
        className="inline-block mt-6 px-6 py-3 bg-green-600 hover:bg-green-700 transition text-white rounded"
      >
        Sign in with Google
      </a>
    </main>
  );
}
