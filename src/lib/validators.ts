import type { NoteInput, Priority } from "./types";

export const priorities: Priority[] = ["Low", "Normal", "High"];

export function requireText(value: string, fieldName: string, maxLength?: number) {
  const cleaned = value.trim();
  if (!cleaned) {
    throw new Error(`${fieldName} is required.`);
  }
  if (maxLength && cleaned.length > maxLength) {
    throw new Error(`${fieldName} must be ${maxLength} characters or fewer.`);
  }
  return cleaned;
}

export function validateEmail(email: string) {
  const cleaned = requireText(email, "Email", 255).toLowerCase();
  if (!/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(cleaned)) {
    throw new Error("Enter a valid email address.");
  }
  return cleaned;
}

export function validatePassword(password: string, confirmPassword?: string) {
  if (password.length < 6) {
    throw new Error("Password must be at least 6 characters.");
  }
  if (confirmPassword !== undefined && password !== confirmPassword) {
    throw new Error("Passwords do not match.");
  }
  return password;
}

export function validateNoteInput(input: NoteInput): NoteInput {
  const title = requireText(input.title, "Title", 160);
  if (!priorities.includes(input.priority)) {
    throw new Error("Priority must be Low, Normal, or High.");
  }
  return {
    ...input,
    title,
    content: input.content.trim()
  };
}
