import { describe, expect, it } from "vitest";

import { buildReportSummary } from "./reports";
import type { Category, Note } from "./types";

describe("buildReportSummary", () => {
  it("summarizes notes and category counts", () => {
    const categories: Category[] = [
      { id: "c1", user_id: "u1", name: "Work", created_at: "2026-01-01T00:00:00Z" }
    ];
    const notes: Note[] = [
      {
        id: "n1",
        user_id: "u1",
        category_id: "c1",
        title: "One",
        content: "",
        priority: "Normal",
        is_pinned: true,
        created_at: "2026-01-01T00:00:00Z",
        updated_at: "2026-01-01T00:00:00Z",
        categories: { id: "c1", name: "Work" }
      },
      {
        id: "n2",
        user_id: "u1",
        category_id: null,
        title: "Two",
        content: "",
        priority: "Low",
        is_pinned: false,
        created_at: "2026-01-01T00:00:00Z",
        updated_at: "2026-01-01T00:00:00Z",
        categories: null
      }
    ];

    expect(buildReportSummary(notes, categories)).toEqual({
      totalNotes: 2,
      pinnedNotes: 1,
      totalCategories: 1,
      notesByCategory: { Work: 1, Uncategorized: 1 }
    });
  });
});
