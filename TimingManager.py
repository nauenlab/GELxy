


class TimingManager:
    TIME_STEP = 0.01  # 0.01 s

    def __init__(self):
        self.current_time = 0
        self.instance_lock = None

    def reset(self):
        self.instance_lock = None
        self.current_time = 0

    def increment(self, instance):
        if not self.instance_lock:
            self.instance_lock = instance
        elif self.instance_lock == instance:
            self.current_time += self.TIME_STEP
