version = "0.0.6"

try:
    from . import reflectOnMee  # works when loaded as an Anki addon
except ImportError:
    import reflectOnMee  # fallback for direct use / test environment
