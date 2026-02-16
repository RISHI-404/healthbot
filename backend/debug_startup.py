
import asyncio
import logging
import sys
from app.main import app

# Configure logging to see all output
logging.basicConfig(level=logging.DEBUG)

async def debug_startup():
    print("Starting app simulation...")
    try:
        # Simulate lifespan startup
        async with app.router.lifespan_context(app):
            print("Startup successful!")
            # We don't need to keep it running, just check startup
    except Exception as e:
        print(f"Startup failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(debug_startup())
