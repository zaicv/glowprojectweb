/**
 * Supabase stub — package removed for marketing site deployment.
 * Restore @supabase/supabase-js and replace with real client when re-enabling backend.
 */

const noop = () => {};
const reject = (msg = "Supabase is disabled") => Promise.reject(new Error(msg));
const resolveNull = () => Promise.resolve({ data: null, error: null });
const resolveEmpty = () => Promise.resolve({ data: [], error: null });

const stubChain = () => ({
  select: () => ({ data: null, error: null }),
  insert: () => ({ data: null, error: null }),
  update: () => ({ data: null, error: null }),
  delete: () => ({ data: null, error: null }),
  eq: () => stubChain(),
  single: () => resolveNull(),
});

export const supabase = {
  auth: {
    getSession: resolveNull,
    getUser: resolveNull,
    signInWithPassword: () => reject(),
    signUp: () => reject(),
    signOut: resolveNull,
    onAuthStateChange: () => ({ data: { subscription: { unsubscribe: noop } } }),
  },
  from: () => stubChain(),
  storage: {
    from: () => ({
      upload: () => reject(),
      getPublicUrl: () => ({ data: { publicUrl: "" } }),
      remove: () => resolveEmpty(),
    }),
  },
  channel: () => ({
    on: () => ({ subscribe: () => ({ unsubscribe: noop }) }),
    subscribe: () => ({ unsubscribe: noop }),
  }),
  removeChannel: noop,
} as any;

export const isSupabaseConfigured = false;
