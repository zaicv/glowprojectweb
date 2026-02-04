/**
 * Stub for @supabase/supabase-js — Supabase removed for marketing deployment.
 * Any import of createClient or @supabase/supabase-js resolves here.
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

const stubClient = {
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
  rpc: () => resolveNull,
} as any;

/** Stub createClient — never calls real Supabase, never throws */
export function createClient(_url?: string, _key?: string) {
  return stubClient;
}

export default { createClient };
