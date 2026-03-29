import Link from "next/link";

export default function HomePage() {
  return (
    <section className="space-y-4">
      <h2 className="text-2xl font-semibold">Agentic Developer Onboarding Assistant</h2>
      <p className="text-sm text-slate-600">
        Use intake to create a new hire profile, assistant to ask onboarding questions, and dashboard to track progress
        and blockers.
      </p>
      <div className="flex flex-wrap gap-3">
        <Link className="button" href="/intake">
          Start Intake
        </Link>
        <Link className="button" href="/assistant">
          Open Assistant
        </Link>
        <Link className="button" href="/dashboard">
          View Dashboard
        </Link>
        <Link className="button" href="/manager">
          Manager View
        </Link>
      </div>
    </section>
  );
}
