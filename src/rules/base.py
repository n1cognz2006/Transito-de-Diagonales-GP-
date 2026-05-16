from abc import ABC, abstractmethod


class Rule(ABC):
    name: str = "base"

    @abstractmethod
    def update(self, frame_idx, t_sec, active_track_ids, history, cfg, log):
        ...
