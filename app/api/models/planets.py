from pydantic import BaseModel


class PlanetModel(BaseModel):
    club_id: int
    planet: str


class PlanetModelDatabase(PlanetModel):
    code: int


class PlanetModelCheckIn(PlanetModel):
    user_code: int


class PlanetModelCheckOut(PlanetModelCheckIn):
    code_is_valid: bool = False


mercury = PlanetModelDatabase(club_id=99353432, code=0, planet="mercury")
venus = PlanetModelDatabase(club_id=198269701, code=0, planet="venus")
earth = PlanetModelDatabase(club_id=129636704, code=0, planet="earth")
mars = PlanetModelDatabase(club_id=110044637, code=0, planet="mars")
jupiter = PlanetModelDatabase(club_id=68365367, code=1, planet="jupiter")
saturn = PlanetModelDatabase(club_id=142758151, code=1, planet="saturn")
uranus = PlanetModelDatabase(club_id=106360242, code=1, planet="uranus")
neptune = PlanetModelDatabase(club_id=218344798, code=1, planet="neptune")

planets_list = [mercury, venus, earth, mars, jupiter, saturn, uranus, neptune]
