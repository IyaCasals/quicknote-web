import type { Category, Note, ReportSummary } from "./types";

export function buildReportSummary(notes: Note[], categories: Category[]): ReportSummary {
  const notesByCategory: Record<string, number> = {};

  for (const category of categories) {
    notesByCategory[category.name] = 0;
  }

  for (const note of notes) {
    const categoryName = note.categories?.name ?? "Uncategorized";
    notesByCategory[categoryName] = (notesByCategory[categoryName] ?? 0) + 1;
  }

  return {
    totalNotes: notes.length,
    pinnedNotes: notes.filter((note) => note.is_pinned).length,
    totalCategories: categories.length,
    notesByCategory
  };
}
