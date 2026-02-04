""" This is used to initialize registry of all chains at startup """

from backend.core.binaprojects import BinaProjects
from backend.core.carrefour import CarrefourParent
# from backend.core.hazihinam import HaziHinam
# from backend.core.laibcatalog import LaibCatalog
from backend.core.publishedprices import PublishedPrices
from backend.core.shufersal import Shufersal
from backend.core.super_class import SupermarketChain


def initialize_backend():
    """
    Call this once at app startup.
    Ensures all supermarket chains subclasses are imported and registered.
    """
    # print("Registered chains:", SupermarketChain.registry)
    pass

