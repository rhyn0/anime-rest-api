from fastapi import Depends

from anime_rest_api.db import DatabaseConnection

DbDependency = Depends(DatabaseConnection.instance().session)
