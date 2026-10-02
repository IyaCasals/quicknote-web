const palette = [
  { background: "#e0f2fe", border: "#7dd3fc", text: "#075985" },
  { background: "#dcfce7", border: "#86efac", text: "#166534" },
  { background: "#fef3c7", border: "#fcd34d", text: "#92400e" },
  { background: "#fce7f3", border: "#f9a8d4", text: "#9d174d" },
  { background: "#ede9fe", border: "#c4b5fd", text: "#5b21b6" },
  { background: "#fee2e2", border: "#fca5a5", text: "#991b1b" },
  { background: "#ccfbf1", border: "#5eead4", text: "#115e59" },
  { background: "#e2e8f0", border: "#94a3b8", text: "#334155" }
];

export type CategoryColor = (typeof palette)[number];

export function getCategoryColor(seed: string | null | undefined): CategoryColor {
  const value = seed?.trim() || "Uncategorized";
  let hash = 0;

  for (const character of value) {
    hash = (hash * 31 + character.charCodeAt(0)) >>> 0;
  }

  return palette[hash % palette.length];
}
