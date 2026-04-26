"use client";

import { useRouter } from "next/navigation";
import { ReactNode, useEffect, useState } from "react";

type AuthGuardProps = {
  children: ReactNode;
};

export default function AuthGuard({ children }: AuthGuardProps) {
  const router = useRouter();
  const [ready, setReady] = useState(false);

  useEffect(() => {
    const sessionUser = sessionStorage.getItem("travelBuddyUser");

    if (!sessionUser) {
      localStorage.removeItem("travelBuddyUser");
      router.replace("/");
      return;
    }

    setReady(true);
  }, [router]);

  if (!ready) {
    return (
      <main className="auth-shell">
        <section className="auth-card">
          <p className="eyebrow">Checking access</p>
          <h1 className="section-title">Redirecting...</h1>
          <p className="auth-copy">
            Please login to open the planner and profile pages.
          </p>
        </section>
      </main>
    );
  }

  return <>{children}</>;
}
