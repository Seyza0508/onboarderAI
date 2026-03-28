"use client";

import { FormEvent, useEffect, useState } from "react";

import { sendChat } from "@/lib/api-client";
import { ChatResult } from "@/lib/types";

type ChatEntry = {
  question: string;
  answer: ChatResult;
};

export default function AssistantPage() {
  const [userId, setUserId] = useState("");
  const [question, setQuestion] = useState("");
  const [history, setHistory] = useState<ChatEntry[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const stored = localStorage.getItem("onboardai_user_id");
    if (stored) setUserId(stored);
  }, []);

  async function onSubmit(event: FormEvent) {
    event.preventDefault();
    setError(null);

    if (!userId) {
      setError("Enter a valid user ID.");
      return;
    }

    setLoading(true);
    try {
      const answer = await sendChat(Number(userId), question);
      setHistory((prev) => [{ question, answer }, ...prev]);
      setQuestion("");
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to send chat");
    } finally {
      setLoading(false);
    }
  }

  return (
    <section className="space-y-4">
      <h2 className="text-xl font-semibold">Onboarding Assistant</h2>

      <form className="card space-y-3" onSubmit={onSubmit}>
        <div>
          <label className="mb-1 block text-sm font-medium">User ID</label>
          <input className="input" value={userId} onChange={(e) => setUserId(e.target.value)} />
        </div>
        <div>
          <label className="mb-1 block text-sm font-medium">Question</label>
          <textarea
            className="input min-h-24"
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            placeholder="Example: I cannot access the repo, what should I do next?"
            required
          />
        </div>
        <button className="button" type="submit" disabled={loading}>
          {loading ? "Thinking..." : "Ask Assistant"}
        </button>
      </form>

      {error ? <p className="text-sm text-rose-700">{error}</p> : null}

      <div className="space-y-3">
        {history.map((entry, index) => (
          <article key={`${entry.question}-${index}`} className="card space-y-2">
            <p className="text-sm font-medium">Q: {entry.question}</p>
            <p className="whitespace-pre-line text-sm">{entry.answer.response}</p>
            <p className="text-xs text-slate-500">Sources: {entry.answer.sources.join(", ")}</p>
          </article>
        ))}
      </div>
    </section>
  );
}
