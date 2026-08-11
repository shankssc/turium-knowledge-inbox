import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import type { QueryResponse } from "@/lib/api"

interface AnswerViewProps {
  result: QueryResponse | null
}

export function AnswerView({ result }: AnswerViewProps) {
  if (!result) return null

  return (
    <Card>
      <CardHeader>
        <CardTitle>Answer</CardTitle>
      </CardHeader>
      <CardContent className="flex flex-col gap-3">
        <p className="text-sm">{result.answer}</p>

        {result.sources.length > 0 && (
          <div className="flex flex-col gap-2 border-t border-neutral-200 pt-3">
            <span className="text-xs font-medium uppercase text-neutral-500">Sources</span>
            {result.sources.map((source, idx) => (
              <div key={idx} className="rounded-md bg-neutral-50 p-2 text-xs text-neutral-600">
                <div className="mb-1 flex items-center justify-between">
                  <span className="font-medium uppercase">{source.source_type}</span>
                  <span>{(source.score * 100).toFixed(0)}% match</span>
                </div>
                {source.source_url && (
                  <a
                    href={source.source_url}
                    target="_blank"
                    rel="noreferrer"
                    className="underline break-all"
                  >
                    {source.source_url}
                  </a>
                )}
                <p className="mt-1">{source.text}</p>
              </div>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  )
}