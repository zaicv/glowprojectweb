import { useEffect, useState } from "react";
import { supabase } from "@/supabase/supabaseClient"; // adjust path as needed

const DropUpUserMenu = () => {
  const [user, setUser] = useState<any>(null);
  const [open, setOpen] = useState(false);

  useEffect(() => {
    const getUser = async () => {
      const { data, error } = await supabase.auth.getUser();
      if (error) console.error(error);
      else setUser(data.user);
    };
    getUser();
  }, []);

  const handleLogout = async () => {
    await supabase.auth.signOut();
    window.location.reload(); // or use router.push("/login")
  };

  if (!user) return null;

  return (
    <div className="relative inline-block text-left">
      <button
        onClick={() => setOpen(!open)}
        className="bg-gray-800 text-white px-4 py-2 rounded hover:bg-gray-700"
      >
        Menu
      </button>

      {open && (
        <div className="absolute bottom-full ml-20 mb-2  w-56 rounded-md shadow-lg bg-white ring-1 ring-black ring-opacity-5 p-4 z-50">
          <p className="text-sm font-medium text-gray-900">
            {user.user_metadata?.name || "User"}
          </p>
          <p className="text-xs text-gray-500 mb-3">{user.email}</p>
          <button
            onClick={handleLogout}
            className="w-full bg-red-500 text-white text-sm py-1.5 rounded hover:bg-red-600 transition"
          >
            Log Out
          </button>
        </div>
      )}
    </div>
  );
};

export default DropUpUserMenu;
