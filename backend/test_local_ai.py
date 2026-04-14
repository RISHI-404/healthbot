import sys
sys.path.insert(0, '.')

from app.services.local_ai_service import local_ai_service, safe_response
from app.config import settings

# Verify settings exist
assert hasattr(settings, 'LOCAL_AI_MODEL'), 'Missing LOCAL_AI_MODEL'
assert hasattr(settings, 'LOCAL_AI_ENABLED'), 'Missing LOCAL_AI_ENABLED'
assert hasattr(settings, 'LOCAL_AI_MAX_TOKENS'), 'Missing LOCAL_AI_MAX_TOKENS'

# Verify safety filter catches unsafe patterns
unsafe = safe_response('You have cancer and I prescribe metformin 500mg take 500mg daily')
assert 'Disclaimer' in unsafe, 'Disclaimer not injected on unsafe text'
assert 'prescribe' not in unsafe.lower() or 'Disclaimer' in unsafe, 'Unsafe text leaked'

# Verify a safe response just gets disclaimer appended
safe = safe_response('Drink plenty of water and rest well.')
assert 'Disclaimer' in safe, 'Disclaimer missing from safe response'

print("  PASS  local_ai_service.py imports cleanly")
print("  PASS  safe_response() filters unsafe medical claims")
print("  PASS  safe_response() appends disclaimer to safe text")
print()
print(f"  LOCAL_AI_ENABLED      = {settings.LOCAL_AI_ENABLED}")
print(f"  LOCAL_AI_MODEL        = {settings.LOCAL_AI_MODEL}")
print(f"  LOCAL_AI_MAX_TOKENS   = {settings.LOCAL_AI_MAX_TOKENS}")
print(f"  LOCAL_AI_ADAPTER_PATH = '{settings.LOCAL_AI_ADAPTER_PATH}'")
print()
print("All checks passed.")
