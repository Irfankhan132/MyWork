"use client";
import { useSession, signOut } from "next-auth/react";
import { useEffect } from "react";

export default function Dashboard() {
  const { data: session } = useSession();

  useEffect(() => {
    if (!session?.user) return;

    fetch(`${process.env.NEXT_PUBLIC_API_URL}/auth/sync`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        user_id: session.user.id,
        email: session.user.email,
        name: session.user.name,
      }),
    });
  }, [session]);

  return (
    <main className="p-10">
      <h1 className="text-2xl font-bold">Dashboard</h1>
      <p className="mt-2">{session?.user?.email}</p>

      <button
        onClick={() => signOut()}
        className="mt-6 px-4 py-2 bg-red-600 text-white rounded"
      >
        Sign out
      </button>
    </main>
  );
}
