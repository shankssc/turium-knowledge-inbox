import { useState } from "react";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { ingestNote, ingestUrl, type Item } from "@/lib/api";

type Mode = "note" | "url";

interface AddItemFormProps {
  onItemAdded: (item: Item) => void;
}

export function AddItemForm({ onItemAdded }: AddItemFormProps) {
  const [mode, setMode] = useState<Mode>("note");
  const [text, setText] = useState("");
  const [url, setUrl] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const currentValue = mode === "note" ? text : url;
  const canSubmit = currentValue.trim().length > 0 && !isSubmitting;

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!canSubmit) return;

    setIsSubmitting(true);
    setError(null);

    try {
      const item = mode === "note" ? await ingestNote(text.trim()) : await ingestUrl(url.trim());
      onItemAdded(item);
      setText("");
      setUrl("");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Something went wrong while saving.");
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Save something</CardTitle>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit} className="flex flex-col gap-3">
          <div className="flex gap-2">
            <Button
              type="button"
              variant={mode === "note" ? "default" : "outline"}
              size="sm"
              onClick={() => setMode("note")}
            >
              Note
            </Button>
            <Button
              type="button"
              variant={mode === "url" ? "default" : "outline"}
              size="sm"
              onClick={() => setMode("url")}
            >
              URL
            </Button>
          </div>

          {mode === "note" ? (
            <Textarea
              placeholder="Write a short note..."
              value={text}
              onChange={(e) => setText(e.target.value)}
              disabled={isSubmitting}
            />
          ) : (
            <Input
              type="url"
              placeholder="https://example.com/article"
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              disabled={isSubmitting}
            />
          )}

          {error && <p className="text-sm text-red-600">{error}</p>}

          <Button type="submit" disabled={!canSubmit}>
            {isSubmitting ? "Saving..." : "Save"}
          </Button>
        </form>
      </CardContent>
    </Card>
  );
}
