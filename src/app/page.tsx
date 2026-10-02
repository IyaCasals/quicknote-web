"use client";

import { AuthError, type Session, type User } from "@supabase/supabase-js";
import { BarChart3, Folder, Home, ListTodo, Pin, type LucideIcon } from "lucide-react";
import { FormEvent, useEffect, useMemo, useState } from "react";

import { filterNotes } from "@/lib/filters";
import { buildReportSummary } from "@/lib/reports";
import { getSupabase, hasSupabaseConfig } from "@/lib/supabase";
import type { Category, Note, NoteInput, Priority, Profile, ViewKey } from "@/lib/types";
import { priorities, requireText, validateEmail, validateNoteInput, validatePassword } from "@/lib/validators";

type Message = { text: string; tone: "success" | "error" } | null;

const emptyNoteInput: NoteInput = {
  title: "",
  content: "",
  category_id: null,
  priority: "Normal",
  is_pinned: false
};

const navItems: Array<{ key: ViewKey; label: string; Icon: LucideIcon }> = [
  { key: "dashboard", label: "Dashboard", Icon: Home },
  { key: "notes", label: "All Notes", Icon: ListTodo },
  { key: "pinned", label: "Pinned", Icon: Pin },
  { key: "categories", label: "Categories", Icon: Folder },
  { key: "reports", label: "Reports", Icon: BarChart3 }
];

export default function QuickNotePage() {
  const [session, setSession] = useState<Session | null>(null);
  const [profile, setProfile] = useState<Profile | null>(null);
  const [notes, setNotes] = useState<Note[]>([]);
  const [categories, setCategories] = useState<Category[]>([]);
  const [activeView, setActiveView] = useState<ViewKey>("dashboard");
  const [search, setSearch] = useState("");
  const [categoryFilter, setCategoryFilter] = useState("all");
  const [priorityFilter, setPriorityFilter] = useState<Priority | "All">("All");
  const [message, setMessage] = useState<Message>(null);
  const [loading, setLoading] = useState(true);

  const configured = hasSupabaseConfig();

  useEffect(() => {
    if (!configured) {
      setLoading(false);
      return;
    }

    const supabase = getSupabase();
    supabase.auth.getSession().then(({ data }) => {
      setSession(data.session);
      setLoading(false);
    });

    const { data: listener } = supabase.auth.onAuthStateChange((_event, nextSession) => {
      setSession(nextSession);
    });

    return () => listener.subscription.unsubscribe();
  }, [configured]);

  useEffect(() => {
    if (!session?.user) {
      setProfile(null);
      setNotes([]);
      setCategories([]);
      return;
    }
    void loadData(session.user);
  }, [session?.user?.id]);

  async function loadData(user: User) {
    const supabase = getSupabase();
    setLoading(true);

    const [profileResult, categoriesResult, notesResult] = await Promise.all([
      supabase.from("profiles").select("*").eq("id", user.id).single(),
      supabase.from("categories").select("*").eq("user_id", user.id).order("name"),
      supabase
        .from("notes")
        .select("*, categories(id, name)")
        .eq("user_id", user.id)
        .order("is_pinned", { ascending: false })
        .order("updated_at", { ascending: false })
    ]);

    if (profileResult.error) {
      setMessage({ text: profileResult.error.message, tone: "error" });
    } else {
      setProfile(profileResult.data);
    }

    if (categoriesResult.error) {
      setMessage({ text: categoriesResult.error.message, tone: "error" });
    } else {
      setCategories(categoriesResult.data ?? []);
    }

    if (notesResult.error) {
      setMessage({ text: notesResult.error.message, tone: "error" });
    } else {
      setNotes((notesResult.data ?? []) as Note[]);
    }

    setLoading(false);
  }

  async function refreshData() {
    if (session?.user) {
      await loadData(session.user);
    }
  }

  const filteredNotes = useMemo(
    () =>
      filterNotes(notes, {
        search,
        categoryId: categoryFilter,
        priority: priorityFilter,
        pinnedOnly: activeView === "pinned"
      }),
    [notes, search, categoryFilter, priorityFilter, activeView]
  );

  const summary = useMemo(() => buildReportSummary(notes, categories), [notes, categories]);

  if (!configured) {
    return <SetupMissing />;
  }

  if (loading && !session) {
    return <main className="center-screen">Loading QuickNote...</main>;
  }

  if (!session) {
    return <AuthScreen onMessage={setMessage} message={message} />;
  }

  return (
    <main className="app-shell">
      <header className="topbar">
        <div>
          <h1>QuickNote</h1>
          <p>{profile?.username ?? session.user.email}</p>
        </div>
        <button className="mobile-logout" onClick={() => getSupabase().auth.signOut()}>
          Logout
        </button>
        <form
          className="top-search"
          onSubmit={(event) => {
            event.preventDefault();
            setActiveView("notes");
          }}
        >
          <input value={search} onChange={(event) => setSearch(event.target.value)} placeholder="Search notes..." />
          <button type="submit">Search</button>
        </form>
      </header>

      <aside className="sidebar">
        {navItems.map(({ key, label, Icon }) => (
          <button className={activeView === key ? "active" : ""} key={key} onClick={() => setActiveView(key)}>
            <Icon aria-hidden="true" size={18} strokeWidth={2.2} />
            <span>{label}</span>
          </button>
        ))}
        <button className="logout" onClick={() => getSupabase().auth.signOut()}>
          Logout
        </button>
      </aside>

      <section className="workspace">
        {message && <StatusMessage message={message} onClose={() => setMessage(null)} />}
        {activeView === "dashboard" && (
          <DashboardView summary={summary} notes={notes.slice(0, 6)} onOpenNotes={() => setActiveView("notes")} />
        )}
        {(activeView === "notes" || activeView === "pinned") && (
          <NotesView
            categories={categories}
            notes={filteredNotes}
            search={search}
            categoryFilter={categoryFilter}
            priorityFilter={priorityFilter}
            pinnedOnly={activeView === "pinned"}
            onSearch={setSearch}
            onCategoryFilter={setCategoryFilter}
            onPriorityFilter={setPriorityFilter}
            onMessage={setMessage}
            onRefresh={refreshData}
            userId={session.user.id}
          />
        )}
        {activeView === "categories" && (
          <CategoriesView
            categories={categories}
            notes={notes}
            userId={session.user.id}
            onMessage={setMessage}
            onRefresh={refreshData}
          />
        )}
        {activeView === "reports" && <ReportsView summary={summary} />}
      </section>
    </main>
  );
}

function SetupMissing() {
  return (
    <main className="center-screen">
      <section className="auth-card">
        <h1>QuickNote setup needed</h1>
        <p>Add Supabase environment variables before running the web app.</p>
        <code>NEXT_PUBLIC_SUPABASE_URL</code>
        <code>NEXT_PUBLIC_SUPABASE_ANON_KEY</code>
      </section>
    </main>
  );
}

function AuthScreen({ message, onMessage }: { message: Message; onMessage: (message: Message) => void }) {
  const [mode, setMode] = useState<"login" | "register">("login");
  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [busy, setBusy] = useState(false);

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setBusy(true);
    onMessage(null);

    try {
      const supabase = getSupabase();
      const normalizedEmail = validateEmail(email);
      validatePassword(password, mode === "register" ? confirmPassword : undefined);

      if (mode === "register") {
        const cleanedUsername = requireText(username, "Username", 80);
        const { error } = await supabase.auth.signUp({
          email: normalizedEmail,
          password,
          options: { data: { username: cleanedUsername } }
        });
        if (error) throw error;
        onMessage({ text: "Account created. Check your email if confirmation is enabled, then log in.", tone: "success" });
        setMode("login");
      } else {
        const { error } = await supabase.auth.signInWithPassword({ email: normalizedEmail, password });
        if (error) throw error;
      }
    } catch (error) {
      onMessage({ text: friendlyError(error), tone: "error" });
    } finally {
      setBusy(false);
    }
  }

  return (
    <main className="center-screen">
      <form className="auth-card" onSubmit={submit}>
        <h1>QuickNote</h1>
        <p>{mode === "login" ? "Sign in to your notes" : "Create your personal workspace"}</p>
        {message && <StatusMessage message={message} onClose={() => onMessage(null)} />}
        {mode === "register" && (
          <label>
            Username
            <input value={username} onChange={(event) => setUsername(event.target.value)} />
          </label>
        )}
        <label>
          Email
          <input type="email" value={email} onChange={(event) => setEmail(event.target.value)} />
        </label>
        <label>
          Password
          <input type="password" value={password} onChange={(event) => setPassword(event.target.value)} />
        </label>
        {mode === "register" && (
          <label>
            Confirm password
            <input type="password" value={confirmPassword} onChange={(event) => setConfirmPassword(event.target.value)} />
          </label>
        )}
        <button className="primary" disabled={busy} type="submit">
          {busy ? "Please wait..." : mode === "login" ? "Login" : "Register"}
        </button>
        <button
          className="link-button"
          type="button"
          onClick={() => {
            onMessage(null);
            setMode(mode === "login" ? "register" : "login");
          }}
        >
          {mode === "login" ? "Create account" : "Back to login"}
        </button>
      </form>
    </main>
  );
}

function DashboardView({
  summary,
  notes,
  onOpenNotes
}: {
  summary: ReturnType<typeof buildReportSummary>;
  notes: Note[];
  onOpenNotes: () => void;
}) {
  return (
    <div className="page-stack">
      <div className="page-heading">
        <h2>Dashboard</h2>
        <button onClick={onOpenNotes}>+ New Note</button>
      </div>
      <div className="metric-grid">
        <Metric label="Total Notes" value={summary.totalNotes} />
        <Metric label="Pinned Notes" value={summary.pinnedNotes} />
        <Metric label="Categories" value={summary.totalCategories} />
      </div>
      <div className="two-column">
        <section className="panel">
          <h3>Recent Notes</h3>
          {notes.length === 0 ? (
            <p className="empty">No notes yet. Create your first note.</p>
          ) : (
            notes.map((note) => <NoteListItem key={note.id} note={note} compact />)
          )}
        </section>
        <section className="panel">
          <h3>Notes by Category</h3>
          {Object.keys(summary.notesByCategory).length === 0 ? (
            <p className="empty">No category activity yet.</p>
          ) : (
            Object.entries(summary.notesByCategory).map(([name, count]) => (
              <div className="summary-row" key={name}>
                <span>{name}</span>
                <strong>{count}</strong>
              </div>
            ))
          )}
        </section>
      </div>
    </div>
  );
}

function NotesView({
  categories,
  notes,
  search,
  categoryFilter,
  priorityFilter,
  pinnedOnly,
  userId,
  onSearch,
  onCategoryFilter,
  onPriorityFilter,
  onMessage,
  onRefresh
}: {
  categories: Category[];
  notes: Note[];
  search: string;
  categoryFilter: string;
  priorityFilter: Priority | "All";
  pinnedOnly: boolean;
  userId: string;
  onSearch: (value: string) => void;
  onCategoryFilter: (value: string) => void;
  onPriorityFilter: (value: Priority | "All") => void;
  onMessage: (message: Message) => void;
  onRefresh: () => Promise<void>;
}) {
  const [editing, setEditing] = useState<Note | null>(null);
  const [creating, setCreating] = useState(false);

  return (
    <div className="page-stack">
      <div className="page-heading">
        <h2>{pinnedOnly ? "Pinned Notes" : "All Notes"}</h2>
        <button onClick={() => setCreating(true)}>+ New Note</button>
      </div>
      <div className="filterbar">
        <input value={search} onChange={(event) => onSearch(event.target.value)} placeholder="Title, content, or category" />
        <select value={categoryFilter} onChange={(event) => onCategoryFilter(event.target.value)}>
          <option value="all">All categories</option>
          {categories.map((category) => (
            <option key={category.id} value={category.id}>
              {category.name}
            </option>
          ))}
        </select>
        <select value={priorityFilter} onChange={(event) => onPriorityFilter(event.target.value as Priority | "All")}>
          <option value="All">All priorities</option>
          {priorities.map((priority) => (
            <option key={priority} value={priority}>
              {priority}
            </option>
          ))}
        </select>
      </div>
      {notes.length === 0 ? (
        <section className="panel">
          <p className="empty">No matching notes. Create a note or clear the filters.</p>
        </section>
      ) : (
        <div className="note-list">
          {notes.map((note) => (
            <NoteListItem key={note.id} note={note} onEdit={() => setEditing(note)} />
          ))}
        </div>
      )}
      {(creating || editing) && (
        <NoteEditor
          categories={categories}
          note={editing}
          userId={userId}
          onClose={() => {
            setCreating(false);
            setEditing(null);
          }}
          onMessage={onMessage}
          onRefresh={onRefresh}
        />
      )}
    </div>
  );
}

function NoteEditor({
  categories,
  note,
  userId,
  onClose,
  onMessage,
  onRefresh
}: {
  categories: Category[];
  note: Note | null;
  userId: string;
  onClose: () => void;
  onMessage: (message: Message) => void;
  onRefresh: () => Promise<void>;
}) {
  const [input, setInput] = useState<NoteInput>(
    note
      ? {
          title: note.title,
          content: note.content,
          category_id: note.category_id,
          priority: note.priority,
          is_pinned: note.is_pinned
        }
      : emptyNoteInput
  );
  const [busy, setBusy] = useState(false);

  async function save(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setBusy(true);

    try {
      const payload = validateNoteInput(input);
      const supabase = getSupabase();
      const result = note
        ? await supabase.from("notes").update(payload).eq("id", note.id).eq("user_id", userId)
        : await supabase.from("notes").insert({ ...payload, user_id: userId });
      if (result.error) throw result.error;
      onMessage({ text: note ? "Note updated." : "Note created.", tone: "success" });
      await onRefresh();
      onClose();
    } catch (error) {
      onMessage({ text: friendlyError(error), tone: "error" });
    } finally {
      setBusy(false);
    }
  }

  async function deleteNote() {
    if (!note || !window.confirm("Delete this note permanently?")) return;
    const { error } = await getSupabase().from("notes").delete().eq("id", note.id).eq("user_id", userId);
    if (error) {
      onMessage({ text: error.message, tone: "error" });
      return;
    }
    onMessage({ text: "Note deleted.", tone: "success" });
    await onRefresh();
    onClose();
  }

  return (
    <div className="modal-backdrop">
      <form className="modal" onSubmit={save}>
        <div className="page-heading">
          <h2>{note ? "Edit Note" : "New Note"}</h2>
          <button className="ghost" type="button" onClick={onClose}>
            Cancel
          </button>
        </div>
        <label>
          Title
          <input value={input.title} onChange={(event) => setInput({ ...input, title: event.target.value })} />
        </label>
        <label>
          Content
          <textarea value={input.content} onChange={(event) => setInput({ ...input, content: event.target.value })} />
        </label>
        <div className="form-grid">
          <label>
            Category
            <select
              value={input.category_id ?? ""}
              onChange={(event) => setInput({ ...input, category_id: event.target.value || null })}
            >
              <option value="">Uncategorized</option>
              {categories.map((category) => (
                <option key={category.id} value={category.id}>
                  {category.name}
                </option>
              ))}
            </select>
          </label>
          <label>
            Priority
            <select
              value={input.priority}
              onChange={(event) => setInput({ ...input, priority: event.target.value as Priority })}
            >
              {priorities.map((priority) => (
                <option key={priority} value={priority}>
                  {priority}
                </option>
              ))}
            </select>
          </label>
          <label className="check-row">
            <input
              checked={input.is_pinned}
              type="checkbox"
              onChange={(event) => setInput({ ...input, is_pinned: event.target.checked })}
            />
            Pinned
          </label>
        </div>
        <div className="modal-actions">
          {note && (
            <button className="danger" type="button" onClick={deleteNote}>
              Delete
            </button>
          )}
          <button className="primary" disabled={busy} type="submit">
            {busy ? "Saving..." : "Save"}
          </button>
        </div>
      </form>
    </div>
  );
}

function CategoriesView({
  categories,
  notes,
  userId,
  onMessage,
  onRefresh
}: {
  categories: Category[];
  notes: Note[];
  userId: string;
  onMessage: (message: Message) => void;
  onRefresh: () => Promise<void>;
}) {
  const [name, setName] = useState("");

  async function createCategory(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    try {
      const cleaned = requireText(name, "Category name", 80);
      const { error } = await getSupabase().from("categories").insert({ name: cleaned, user_id: userId });
      if (error) throw error;
      setName("");
      onMessage({ text: "Category added.", tone: "success" });
      await onRefresh();
    } catch (error) {
      onMessage({ text: friendlyError(error), tone: "error" });
    }
  }

  async function renameCategory(category: Category, nextName: string) {
    try {
      const cleaned = requireText(nextName, "Category name", 80);
      const { error } = await getSupabase().from("categories").update({ name: cleaned }).eq("id", category.id).eq("user_id", userId);
      if (error) throw error;
      onMessage({ text: "Category renamed.", tone: "success" });
      await onRefresh();
    } catch (error) {
      onMessage({ text: friendlyError(error), tone: "error" });
    }
  }

  async function deleteCategory(category: Category) {
    if (!window.confirm("Delete this category? Existing notes will become uncategorized.")) return;
    const { error } = await getSupabase().from("categories").delete().eq("id", category.id).eq("user_id", userId);
    if (error) {
      onMessage({ text: error.message, tone: "error" });
      return;
    }
    onMessage({ text: "Category deleted.", tone: "success" });
    await onRefresh();
  }

  return (
    <div className="page-stack">
      <h2>Categories</h2>
      <form className="filterbar" onSubmit={createCategory}>
        <input value={name} onChange={(event) => setName(event.target.value)} placeholder="New category name" />
        <button type="submit">Add</button>
      </form>
      <section className="panel">
        {categories.length === 0 ? (
          <p className="empty">No categories yet. Add one above.</p>
        ) : (
          categories.map((category) => (
            <EditableCategory
              key={category.id}
              category={category}
              count={notes.filter((note) => note.category_id === category.id).length}
              onDelete={() => deleteCategory(category)}
              onRename={(nextName) => renameCategory(category, nextName)}
            />
          ))
        )}
      </section>
    </div>
  );
}

function EditableCategory({
  category,
  count,
  onRename,
  onDelete
}: {
  category: Category;
  count: number;
  onRename: (name: string) => void;
  onDelete: () => void;
}) {
  const [name, setName] = useState(category.name);

  return (
    <div className="category-row">
      <input value={name} onChange={(event) => setName(event.target.value)} />
      <span>{count} notes</span>
      <button onClick={() => onRename(name)}>Rename</button>
      <button className="danger" onClick={onDelete}>
        Delete
      </button>
    </div>
  );
}

function ReportsView({ summary }: { summary: ReturnType<typeof buildReportSummary> }) {
  return (
    <div className="page-stack">
      <h2>Reports</h2>
      <section className="panel">
        <Metric label="Total notes" value={summary.totalNotes} />
        <Metric label="Pinned notes" value={summary.pinnedNotes} />
        <Metric label="Total categories" value={summary.totalCategories} />
      </section>
      <section className="panel">
        <h3>Notes per category</h3>
        {Object.entries(summary.notesByCategory).map(([name, count]) => (
          <div className="summary-row" key={name}>
            <span>{name}</span>
            <strong>{count}</strong>
          </div>
        ))}
      </section>
    </div>
  );
}

function Metric({ label, value }: { label: string; value: number }) {
  return (
    <section className="metric">
      <span>{label}</span>
      <strong>{value}</strong>
    </section>
  );
}

function NoteListItem({ note, compact = false, onEdit }: { note: Note; compact?: boolean; onEdit?: () => void }) {
  return (
    <article className="note-card">
      <div>
        <h3>
          {note.is_pinned && <span aria-label="Pinned note">Pinned - </span>}
          {note.title}
        </h3>
        {!compact && <p>{note.content || "No content"}</p>}
        <small>
          {note.categories?.name ?? "Uncategorized"} | {note.priority} | Updated {formatDate(note.updated_at)}
        </small>
      </div>
      {onEdit && <button onClick={onEdit}>Edit</button>}
    </article>
  );
}

function StatusMessage({ message, onClose }: { message: NonNullable<Message>; onClose: () => void }) {
  return (
    <div className={`status ${message.tone}`}>
      <span>{message.text}</span>
      <button onClick={onClose}>Dismiss</button>
    </div>
  );
}

function formatDate(value: string) {
  return new Intl.DateTimeFormat(undefined, {
    year: "numeric",
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit"
  }).format(new Date(value));
}

function friendlyError(error: unknown) {
  if (error instanceof AuthError || error instanceof Error) {
    return error.message;
  }
  return "Something went wrong. Please try again.";
}
