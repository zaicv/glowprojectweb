// src/supabase/supabaseClient.ts
import { createClient, type SupabaseClient } from "@supabase/supabase-js";

const supabaseUrl = import.meta.env.VITE_SUPABASE_URL;
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY;

const missingConfigMessage =
  "Supabase credentials are not configured. Set VITE_SUPABASE_URL and VITE_SUPABASE_ANON_KEY to enable backend features.";

if (!supabaseUrl || !supabaseAnonKey) {
  console.warn(missingConfigMessage);
}

const fallbackClient = new Proxy(
  {},
  {
    get() {
      throw new Error(missingConfigMessage);
    },
  }
) as SupabaseClient<any, "public", any>;

export const supabase =
  supabaseUrl && supabaseAnonKey
    ? createClient(supabaseUrl, supabaseAnonKey, {
        auth: {
          persistSession: true,
          autoRefreshToken: true,
          detectSessionInUrl: true,
        },
      })
    : fallbackClient;

export const isSupabaseConfigured = Boolean(supabaseUrl && supabaseAnonKey);