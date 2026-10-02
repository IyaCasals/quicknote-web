import { describe, expect, it } from "vitest";

import { filterNotes } from "./filters";
import type { Note } from "./types";

const notes: Note[] = [
  {
    id: "1",
    user_id: "u1",
    category_id: "c1",
    title: "Launch",
    content: "Email supplier",
    priority: "High",
    is_pinned: true,
    created_at: "2026-01-01T00:00:00Z",
    updated_at: "2026-01-03T00:00:00Z",
    categories: { id: "c1", name: "Work" }
  },
  {
    id: "2",
    user_id: "u1",
    category_id: null,
    title: "Journal",
    content: "Weekend ideas",
    priority: "Low",
    is_pinned: false,
    created_at: "2026-01-01T00:00:00Z",
    updated_at: "2026-01-04T00:00:00Z",
    categories: null
  }
];

describe("filterNotes", () => {
  it("searches title, content, and category", () => {
    expect(filterNotes(notes, { search: "supplier", categoryId: "all", priority: "All", pinnedOnly: false })).toHaveLength(1);
    expect(filterNotes(notes, { search: "work", categoryId: "all", priority: "All", pinnedOnly: false })[0].id).toBe("1");
  });

  it("filters by pinned and priority", () => {
    const result = filterNotes(notes, { search: "", categoryId: "all", priority: "High", pinnedOnly: true });
    expect(result.map((note) => note.id)).toEqual(["1"]);
  });
});
