


class EstimatedCompletionTime:
    def __init__(self, coordinates) -> None:
        self.coordinates = coordinates

    def get_completion_time(self):
        seconds = 0
        prev = None
        for i in self.coordinates:
            if prev:
                seconds += prev.movement_time(i)
            
            prev = i
        
        # offset for downtime between movements
        seconds += len(self.coordinates) * 0.2

        return seconds