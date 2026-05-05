import os
import threading
import time

# 起始时间戳 (2020-01-01 00:00:00 UTC)，与 Java 版保持一致
_EPOCH = 1577836800000

# 各部分位数
_WORKER_ID_BITS = 5
_DATA_CENTER_ID_BITS = 5
_SEQUENCE_BITS = 12

# 最大值
_MAX_WORKER_ID = (1 << _WORKER_ID_BITS) - 1       # 31
_MAX_DATA_CENTER_ID = (1 << _DATA_CENTER_ID_BITS) - 1  # 31
_MAX_SEQUENCE = (1 << _SEQUENCE_BITS) - 1          # 4095

# 左移位数
_WORKER_SHIFT = _SEQUENCE_BITS                     # 12
_DATA_CENTER_SHIFT = _SEQUENCE_BITS + _WORKER_ID_BITS  # 17
_TIMESTAMP_SHIFT = _SEQUENCE_BITS + _WORKER_ID_BITS + _DATA_CENTER_ID_BITS  # 22


class SnowflakeGenerator:
    def __init__(self, worker_id: int | None = None, data_center_id: int | None = None):
        if worker_id is None:
            worker_id = int(os.getenv("SNOWFLAKE_WORKER_ID", "1"))
        if data_center_id is None:
            data_center_id = int(os.getenv("SNOWFLAKE_DATA_CENTER_ID", "1"))

        if not (0 <= worker_id <= _MAX_WORKER_ID):
            raise ValueError(f"worker_id 必须在 0-{_MAX_WORKER_ID} 之间")
        if not (0 <= data_center_id <= _MAX_DATA_CENTER_ID):
            raise ValueError(f"data_center_id 必须在 0-{_MAX_DATA_CENTER_ID} 之间")

        self._worker_id = worker_id
        self._data_center_id = data_center_id
        self._sequence = 0
        self._last_timestamp = -1
        self._lock = threading.Lock()

    def _current_millis(self) -> int:
        return int(time.time() * 1000)

    def _wait_next_millis(self, last_ts: int) -> int:
        ts = self._current_millis()
        while ts <= last_ts:
            ts = self._current_millis()
        return ts

    def next_id(self) -> int:
        with self._lock:
            ts = self._current_millis()

            if ts < self._last_timestamp:
                raise RuntimeError(f"时钟回拨 {self._last_timestamp - ts}ms，拒绝生成 id")

            if ts == self._last_timestamp:
                self._sequence = (self._sequence + 1) & _MAX_SEQUENCE
                if self._sequence == 0:
                    ts = self._wait_next_millis(self._last_timestamp)
            else:
                self._sequence = 0

            self._last_timestamp = ts

            return (
                ((ts - _EPOCH) << _TIMESTAMP_SHIFT)
                | (self._data_center_id << _DATA_CENTER_SHIFT)
                | (self._worker_id << _WORKER_SHIFT)
                | self._sequence
            )


# 全局单例，worker_id 通过环境变量 SNOWFLAKE_WORKER_ID 区分不同实例
snowflake = SnowflakeGenerator()
