import math


class PoolingAlgorithm:
    @staticmethod
    def haversine_distance_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        r = 6371.0
        d_lat = math.radians(lat2 - lat1)
        d_lon = math.radians(lon2 - lon1)
        a = (
            math.sin(d_lat / 2) ** 2
            + math.cos(math.radians(lat1))
            * math.cos(math.radians(lat2))
            * math.sin(d_lon / 2) ** 2
        )
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return r * c

    @classmethod
    def route_distance(cls, stops: list[tuple[float, float]]) -> float:
        if len(stops) < 2:
            return 0.0
        distance = 0.0
        for i in range(len(stops) - 1):
            distance += cls.haversine_distance_km(stops[i][0], stops[i][1], stops[i + 1][0], stops[i + 1][1])
        return distance
