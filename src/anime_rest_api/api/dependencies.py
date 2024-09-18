from fastapi import Depends

from anime_rest_api.db.connection import Db

DbDependency = Depends(Db.session)
