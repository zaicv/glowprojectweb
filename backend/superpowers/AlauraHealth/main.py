import os
from typing import Dict, Any
from datetime import datetime
from dotenv import load_dotenv
from supabase import create_client, Client




class Superpower:
    def __init__(self):
        self.name = "Health Log"

        # Load environment variables
        load_dotenv(dotenv_path="/Users/zai/The GlowOS/glow/The Core/GlowGPT/.env")

        # Supabase credentials
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_ANON_KEY")
        if not url or not key:
            raise ValueError("❌ Missing Supabase credentials in environment variables.")
        
        self.supabase: Client = create_client(url, key)

        # Supported intents
        self.intent_map = {
            "log_health": "Log health metrics (weight, sleep, blood pressure, meals, water, etc.)",
            "update_health": "Update an existing health record",
            "view_health": "Fetch and view health records"
        }

    async def run(self, intent: str, **kwargs):
        try:
            print(f"🩺 HealthLog: Processing intent '{intent}' with kwargs: {kwargs}")

            if intent == "log_health":
                return await self.log_health_entry(**kwargs)
            elif intent == "update_health":
                return await self.update_health_entry(**kwargs)
            elif intent == "view_health":
                return await self.view_health_entries(**kwargs)
            else:
                return f"❌ Unknown HealthLog intent: {intent}"

        except Exception as e:
            print(f"❌ HealthLog run() error: {type(e).__name__}: {str(e)}")
            return f"❌ Error in HealthLog superpower: {str(e)}"

    async def log_health_entry(self, **details):
        """Insert or update a health record dynamically for today with correct schema"""
        try:
            user_id = details.get("user_id") or "c52927f7-0256-4f22-9071-77a09ffc90a1"
            today = details.get("date") or datetime.now().date().isoformat()

            # Allowed columns in your table
            allowed_columns = [
                "am_blood_pressure", "pm_blood_pressure", "weight",
                "water_intake", "meals_eaten", "hours_sleep", "sleep_debt", "meds_taken"
            ]
            cumulative_fields = ["meds_taken", "meals_eaten", "water_intake"]
            float_fields = ["weight", "hours_sleep", "sleep_debt"]
            overwrite_fields = ["am_blood_pressure", "pm_blood_pressure"]

            # Prepare new entry with only allowed columns
            new_entry = {"user_id": user_id, "date": today}
            for k in allowed_columns:
                if k in details and details[k] is not None:
                    if k in cumulative_fields:
                        new_entry[k] = int(details[k])
                    elif k in float_fields:
                        new_entry[k] = float(details[k])
                    elif k in overwrite_fields:
                        new_entry[k] = str(details[k])

            # Check if an entry exists for today
            resp = self.supabase.table("health") \
                .select("*") \
                .eq("user_id", user_id) \
                .eq("date", today) \
                .execute()

            existing = getattr(resp, "data", [])
            if existing:
                existing_id = existing[0]["id"]
                updated_values = existing[0].copy()

                for k, v in new_entry.items():
                    if k in cumulative_fields:
                        updated_values[k] = (existing[0].get(k, 0) or 0) + v
                    else:
                        updated_values[k] = v

                self.supabase.table("health").update(updated_values).eq("id", existing_id).execute()
                return f"✅ Updated today's health entry:\n```json\n{updated_values}\n```"
            else:
                # Ensure cumulative fields default to 0
                for key in cumulative_fields:
                    if key not in new_entry:
                        new_entry[key] = 0

                self.supabase.table("health").insert(new_entry).execute()
                return f"✅ Logged new health entry:\n```json\n{new_entry}\n```"

        except Exception as e:
            print(f"❌ HealthLog insert/update error: {e}")
            return f"❌ Failed to log health entry: {str(e)}"
        
    async def update_health_entry(self, **details):
        try:
            entry_id = details.get("id")
            if not entry_id:
                return "❌ entry_id is required to update health."

            # Cast numeric values before updating
            updates = {k: int(v) if isinstance(v, str) and v.isdigit() else v
                       for k, v in details.items() if k not in ["id", "intent"] and v is not None}

            self.supabase.table("health").update(updates).eq("id", entry_id).execute()
            return f"✅ Updated health entry {entry_id} with:\n```json\n{updates}\n```"

        except Exception as e:
            print(f"❌ HealthLog update error: {e}")
            return f"❌ Failed to update health entry: {str(e)}"

    async def view_health_entries(self, **details):
        try:
            user_id = details.get("user_id")
            if not user_id:
                return "❌ user_id is required to fetch records."

            limit = details.get("limit", 5)
            resp = self.supabase.table("health") \
                .select("*") \
                .eq("user_id", user_id) \
                .order("date", desc=True) \
                .limit(limit) \
                .execute()

            records = getattr(resp, "data", [])
            if not records:
                return "⚠️ No health records found."

            return f"📊 Recent Health Records:\n```json\n{records}\n```"

        except Exception as e:
            print(f"❌ HealthLog view error: {e}")
            return f"❌ Failed to fetch health records: {str(e)}"

    def get_help(self):
        return f"""
🩺 **HealthLog Superpower**

**Available Intents:**
{chr(10).join(f"• {intent}: {desc}" for intent, desc in self.intent_map.items())}

**Examples:**
• "log my weight as 162" → log_health  
• "I slept 7.5 hours last night" → log_health  
• "update entry 123 with pm blood pressure 118/76" → update_health  
• "show my last 5 health logs" → view_health  
"""