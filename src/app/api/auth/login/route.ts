import { createClient } from "@supabase/supabase-js";
import { NextResponse } from "next/server";

function getSupabaseUrl() {
  return process.env.NEXT_PUBLIC_SUPABASE_URL;
}

function getPublishableKey() {
  return process.env.NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY || process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY;
}

export async function POST(request: Request) {
  const { identifier, password } = (await request.json()) as {
    identifier?: string;
    password?: string;
  };

  const cleanedIdentifier = identifier?.trim();
  const supabaseUrl = getSupabaseUrl();
  const publishableKey = getPublishableKey();
  const serviceRoleKey = process.env.SUPABASE_SERVICE_ROLE_KEY;

  if (!cleanedIdentifier || !password) {
    return NextResponse.json({ error: "Username/email and password are required." }, { status: 400 });
  }

  if (!supabaseUrl || !publishableKey || !serviceRoleKey) {
    return NextResponse.json({ error: "Authentication is not configured." }, { status: 500 });
  }

  try {
    let email = cleanedIdentifier;

    if (!cleanedIdentifier.includes("@")) {
      const admin = createClient(supabaseUrl, serviceRoleKey, {
        auth: { persistSession: false, autoRefreshToken: false }
      });

      const { data: profile, error: profileError } = await admin
        .from("profiles")
        .select("id")
        .ilike("username", cleanedIdentifier)
        .maybeSingle();

      if (profileError || !profile) {
        return NextResponse.json({ error: "Invalid username/email or password." }, { status: 401 });
      }

      const { data: userResult, error: userError } = await admin.auth.admin.getUserById(profile.id);
      if (userError || !userResult.user.email) {
        return NextResponse.json({ error: "Invalid username/email or password." }, { status: 401 });
      }

      email = userResult.user.email;
    }

    const authClient = createClient(supabaseUrl, publishableKey, {
      auth: { persistSession: false, autoRefreshToken: false }
    });
    const { data, error } = await authClient.auth.signInWithPassword({ email, password });

    if (error || !data.session) {
      return NextResponse.json({ error: "Invalid username/email or password." }, { status: 401 });
    }

    return NextResponse.json({
      session: data.session,
      user: data.user
    });
  } catch {
    return NextResponse.json({ error: "Unable to sign in right now." }, { status: 500 });
  }
}
