
import sys
import os
import traceback
import importlib

# Add project root to sys.path
sys.path.insert(0, os.getcwd())

def test_imports():
    plugin_dir = os.path.join(os.getcwd(), 'src', 'plugins')
    print(f"Scanning {plugin_dir}")
    
    for filename in os.listdir(plugin_dir):
        if filename.endswith(".py") and filename not in {"__init__.py", "plugin_base.py", "plugin_manager.py", "plugin_loader.py"}:
            module_name = filename[:-3]
            print(f"--- Testing {module_name} ---")
            try:
                module = importlib.import_module(f"src.plugins.{module_name}")
                print(f"SUCCESS: Imported {module_name}")
                
                # Check for Plugin class
                if hasattr(module, 'Plugin'):
                    print(f"Found Plugin class in {module_name}")
                    try:
                        p = module.Plugin()
                        print(f"Instantiated Plugin: {p.name}")
                    except Exception as e:
                        print(f"FAILED to instantiate {module_name}.Plugin: {e}")
                        traceback.print_exc()
                else:
                    print(f"WARNING: No Plugin class in {module_name}")
                    
            except Exception as e:
                print(f"FAILED to import {module_name}: {e}")
                traceback.print_exc()

if __name__ == "__main__":
    test_imports()
