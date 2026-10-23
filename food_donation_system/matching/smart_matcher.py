import math

class SmartMatcher:
    def __init__(self, ngos):
        """
        ngos: List of NGO dictionaries fetched from DB
        """
        self.ngos = ngos

    @staticmethod
    def haversine_distance(lat1, lon1, lat2, lon2):
        """
        Calculate the great circle distance in kilometers between two points on Earth.
        """
        R = 6371.0  # Earth radius in kilometers
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        a = (math.sin(dlat / 2) ** 2 +
             math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
             math.sin(dlon / 2) ** 2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return round(R * c, 2)

    def match(self, donor_lat, donor_lon, estimated_servings, safety_tag):
        """
        Ranks candidate NGOs based on multi-criteria optimization:
        - Distance (closer is better)
        - Capacity (can accept estimated_servings)
        - Urgency Bonus (prioritizes closest high-capacity NGOs for Urgent items)
        """
        urgency_weights = {
            "Urgent": 25.0,
            "Medium": 15.0,
            "Fresh": 5.0,
            "Unsafe": 0.0
        }
        urgency_bonus = urgency_weights.get(safety_tag, 10.0)

        matches = []
        for ngo in self.ngos:
            distance_km = self.haversine_distance(donor_lat, donor_lon, ngo['lat'], ngo['lon'])
            
            # Check capacity match ratio
            capacity = ngo['capacity_servings']
            capacity_ratio = min(1.0, capacity / max(1, estimated_servings))
            
            # Distance Penalty (decreases score as distance increases)
            distance_score = max(0.0, 60.0 - (distance_km * 4.0))
            
            # Capacity Score (rewards NGOs that have adequate capacity)
            capacity_score = capacity_ratio * 30.0
            
            # Total Composite Match Score (0 - 100%)
            raw_score = distance_score + capacity_score + urgency_bonus
            match_percentage = round(min(99.9, max(10.0, raw_score)), 1)
            
            # Estimated transit time assuming average city speed of 25 km/h
            estimated_transit_mins = int(round((distance_km / 25.0) * 60 + 5))

            matches.append({
                "ngo_id": ngo['id'],
                "name": ngo['name'],
                "contact": ngo['contact'],
                "address": ngo['address'],
                "lat": ngo['lat'],
                "lon": ngo['lon'],
                "capacity_servings": capacity,
                "operating_hours": ngo['operating_hours'],
                "distance_km": distance_km,
                "transit_time_mins": estimated_transit_mins,
                "match_score": match_percentage,
                "capacity_sufficient": capacity >= estimated_servings
            })

        # Sort by highest match score
        matches.sort(key=lambda x: x['match_score'], reverse=True)
        return matches
