try:
    from .IWantFreePCB import GiveMeFreePCB # Note the relative import!
    GiveMeFreePCB().register() # Instantiate and register to Pcbnew
except Exception as e:
    import logging
    logger = logging.getLogger()
    logger.debug(repr(e))