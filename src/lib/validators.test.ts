import { describe, expect, it } from "vitest";

import { validateEmail, validateNoteInput, validatePassword } from "./validators";

describe("validators", () => {
  it("normalizes valid email addresses", () => {
    expect(validateEmail(" USER@example.COM ")).toBe("user@example.com");
  });

  it("rejects invalid passwords", () => {
    expect(() => validatePassword("short")).toThrow("at least 6");
    expect(() => validatePassword("secret1", "secret2")).toThrow("do not match");
  });

  it("validates note input", () => {
    const note = validateNoteInput({
      title: "  A note  ",
      content: "  Body  ",
      category_id: null,
      priority: "High",
      is_pinned: true
    });

    expect(note.title).toBe("A note");
    expect(note.content).toBe("Body");
  });
});
