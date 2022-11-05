import os

MAYAN_DIG_URL = os.environ["MAYAN_DIG_URL"]
MAYAN_DIG_USER = os.environ["MAYAN_DIG_USER"]
MAYAN_DIG_PASSWORD = os.environ["MAYAN_DIG_PASSWORD"]
MAYAN_DIG_PATH_TEMPLATE = os.environ.get("MAYAN_DIG_PATH_TEMPLATE", "$cabinet/$type/$name")
