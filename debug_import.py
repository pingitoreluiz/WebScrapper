try:
    from playwright_stealth import stealth_async
    print("stealth_async found!")
except ImportError as e:
    print(f"stealth_async failed: {e}")
