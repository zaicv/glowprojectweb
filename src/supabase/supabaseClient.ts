// src/supabase/supabaseClient.ts
import { createClient, type SupabaseClient } from "@supabase/supabase-js";

const supabaseUrl = import.meta.env.VITE_SUPABASE_URL as string | undefined;
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY as string | undefined;

const missingConfigMessage =
  "Supabase credentials are not configured. Set VITE_SUPABASE_URL and VITE_SUPABASE_ANON_KEY to enable backend features.";

// Only use createClient when we have valid-looking credentials (Vercel/env can pass "undefined" or placeholders)
const hasValidUrl =
  typeof supabaseUrl === "string" &&
  supabaseUrl.startsWith("https://") &&
  supabaseUrl.length > 10 &&
  !["undefined", "null", ""].includes(supabaseUrl.trim());
const hasValidKey =
  typeof supabaseAnonKey === "string" &&
  supabaseAnonKey.length > 20 &&
  !["undefined", "null", ""].includes(supabaseAnonKey.trim());

const fallbackClient = new Proxy(
  {},
  {
    get() {
      throw new Error(missingConfigMessage);
    },
  }
) as SupabaseClient<any, "public", any>;

function createSupabaseClient(): SupabaseClient<any, "public", any> {
  if (!hasValidUrl || !hasValidKey) {
    return fallbackClient;
  }
  try {
    return createClient(supabaseUrl!, supabaseAnonKey!, {
      auth: {
        persistSession: true,
        autoRefreshToken: true,
        detectSessionInUrl: true,
      },
    });
  } catch {
    console.warn(missingConfigMessage);
    return fallbackClient;
  }
}

export const supabase = createSupabaseClient();
export const isSupabaseConfigured = hasValidUrl && hasValidKey;