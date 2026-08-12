import * as React from "react";

import { cn } from "@/lib/utils";

function Input({ className, type, ...props }: React.ComponentProps<"input">) {
  return (
    <input
      type={type}
      data-slot="input"
      className={cn(
        "flex h-9 w-full min-w-0 rounded-md border border-neutral-200 bg-white px-3 py-1 text-sm shadow-xs transition-colors outline-none placeholder:text-neutral-500 focus-visible:border-neutral-400 focus-visible:ring-2 focus-visible:ring-neutral-400/30 disabled:pointer-events-none disabled:cursor-not-allowed disabled:opacity-50",
        className,
      )}
      {...props}
    />
  );
}

export { Input };
