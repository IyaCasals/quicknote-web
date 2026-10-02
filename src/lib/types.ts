export type Priority = "Low" | "Normal" | "High";

export type ViewKey = "dashboard" | "notes" | "pinned" | "categories" | "reports";

export type Profile = {
  id: string;
  username: string;
  created_at: string;
};

export type Category = {
  id: string;
  user_id: string;
  name: string;
  created_at: string;
};

export type Note = {
  id: string;
  user_id: string;
  category_id: string | null;
  title: string;
  content: string;
  priority: Priority;
  is_pinned: boolean;
  created_at: string;
  updated_at: string;
  categories?: Pick<Category, "id" | "name"> | null;
};

export type NoteInput = {
  title: string;
  content: string;
  category_id: string | null;
  priority: Priority;
  is_pinned: boolean;
};

export type ReportSummary = {
  totalNotes: number;
  pinnedNotes: number;
  totalCategories: number;
  notesByCategory: Record<string, number>;
};
