import { useState } from "react";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { askQuestion, type QueryResponse } from "@/lib/api";

interface AskQuestionProps {
  onAnswer: (result: QueryResponse) => void;
}

export function AskQuestion({ onAnswer }: AskQuestionProps) {
  const [question, setQuestion] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const canSubmit = question.trim().length > 0 && !isSubmitting;

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!canSubmit) return;

    setIsSubmitting(true);
    setError(null);

    try {
      const result = await askQuestion(question.trim());
      onAnswer(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Something went wrong while asking.");
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Ask a question</CardTitle>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit} className="flex gap-2">
          <Input
            placeholder="What do you want to know?"
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            disabled={isSubmitting}
          />
          <Button type="submit" disabled={!canSubmit}>
            {isSubmitting ? "Asking..." : "Ask"}
          </Button>
        </form>
        {error && <p className="mt-2 text-sm text-red-600">{error}</p>}
      </CardContent>
    </Card>
  );
}
