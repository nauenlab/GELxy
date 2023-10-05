


class TimingManager:
    TIME_STEP = 0.01  # 0.01 s

    def __init__(self):
        self.current_time = 0
        self.m1_lock = None
        self.m2_lock = None

    def reset(self, instance):
        if self.m1_lock == instance:
            self.m1_lock = None
        if self.m2_lock == instance:
            self.m2_lock = None

        if not self.is_locked():
            self.current_time = 0

    def lock(self, instance):
        if not self.m1_lock:
            self.m1_lock = instance
        elif not self.m2_lock:
            self.m2_lock = instance

    def is_locked(self):
        return self.m1_lock is not None or self.m2_lock is not None

    def increment(self, instance):
        if not self.is_locked():
            self.lock(instance)
        if self.instance_lock == instance:
            self.current_time += self.TIME_STEP
