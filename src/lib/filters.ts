import type { Note, Priority } from "./types";

export type NoteFilters = {
  search: string;
  categoryId: string;
  priority: Priority | "All";
  pinnedOnly: boolean;
};

export function filterNotes(notes: Note[], filters: NoteFilters) {
  const search = filters.search.trim().toLowerCase();

  return notes
    .filter((note) => {
      const categoryName = note.categories?.name ?? "";
      const matchesSearch =
        !search ||
        note.title.toLowerCase().includes(search) ||
        note.content.toLowerCase().includes(search) ||
        categoryName.toLowerCase().includes(search);
      const matchesCategory = filters.categoryId === "all" || note.category_id === filters.categoryId;
      const matchesPriority = filters.priority === "All" || note.priority === filters.priority;
      const matchesPinned = !filters.pinnedOnly || note.is_pinned;
      return matchesSearch && matchesCategory && matchesPriority && matchesPinned;
    })
    .sort((a, b) => {
      if (a.is_pinned !== b.is_pinned) {
        return a.is_pinned ? -1 : 1;
      }
      return new Date(b.updated_at).getTime() - new Date(a.updated_at).getTime();
    });
}
