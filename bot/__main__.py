import sys
from pyrogram import idle
from bot import app
import pkgutil
import bot.plugins
import importlib

def main():
    # Load all modules in bot.plugins
    for importer, modname, ispkg in pkgutil.iter_modules(bot.plugins.__path__):
        module = importlib.import_module(f"bot.plugins.{modname}")

    # Print the names of all loaded modules
    print("Loaded modules:")
    for module in sys.modules:
        if module.startswith("bot/plugins"):
            print(module)

    # Start the application and idle
    app.run()
    idle()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Exiting...")
    except Exception as e:
        print(f"An error occurred: {e}")