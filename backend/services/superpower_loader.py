# ============================================
# 🦸 Superpower Loader Service
# ============================================
# Dynamically discovers and loads superpowers from the superpowers/ folder

import importlib
import pkgutil
from typing import Dict, Any
import superpowers


def load_superpowers() -> Dict[str, Any]:
    """
    Dynamically load all superpowers from the superpowers package.
    
    Returns:
        Dict[str, Any]: Dictionary mapping superpower names to instances
    
    Example:
        powers = load_superpowers()
        # powers = {"youtube": YouTubePower(), "plex": PlexPower(), ...}
    """
    powers = {}
    package = superpowers  # points to the superpowers/ folder

    for _, module_name, ispkg in pkgutil.iter_modules(package.__path__):
        try:
            # Import dynamically (e.g., superpowers.Plex.main)
            module = importlib.import_module(f"superpowers.{module_name}.main")

            # Convention: module must expose Superpower class
            if hasattr(module, "Superpower"):
                power = module.Superpower()
                powers[power.name] = power
                print(f"✅ Loaded superpower: {power.name}")
            else:
                print(f"⚠️ No Superpower class in {module_name}")
        except Exception as e:
            print(f"❌ Failed loading {module_name}: {e}")

    print(f"🦸 Total superpowers loaded: {len(powers)}")
    return powers


def get_superpower(powers: Dict[str, Any], name: str) -> Any:
    """
    Get a specific superpower by name.
    
    Args:
        powers: Dictionary of loaded superpowers
        name: Name of the superpower to retrieve
    
    Returns:
        The superpower instance, or None if not found
    """
    return powers.get(name.lower())


def list_superpower_intents(powers: Dict[str, Any]) -> Dict[str, Dict[str, list]]:
    """
    Get all available intents for all superpowers.
    
    Returns:
        Dict mapping superpower names to their intent lists
    
    Example:
        {
            "youtube": {
                "intents": ["download_video", "download_audio", "search"],
                "description": "YouTube downloader"
            },
            "plex": {...}
        }
    """
    result = {}
    
    for name, power in powers.items():
        intent_map = getattr(power, 'intent_map', {})
        result[name] = {
            "intents": list(intent_map.keys()),
            "description": getattr(power, 'description', None),
            "intent_count": len(intent_map)
        }
    
    return result