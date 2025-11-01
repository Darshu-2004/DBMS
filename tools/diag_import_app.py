import sys
try:
    import app
    print('OK: imported app')
except Exception as e:
    print('IMPORT ERROR:', type(e).__name__, str(e))
    import traceback
    traceback.print_exc()
    sys.exit(1)
