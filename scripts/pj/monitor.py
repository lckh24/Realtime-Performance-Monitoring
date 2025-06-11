import psutil
psutil.PROCFS_PATH = '/proc'
import datetime

class SystemMonitor:
    def __init__(self):
        pass

    def _bytes2human(self, n):
        symbols = ('B', 'KB', 'MB', 'GB', 'TB')
        for s in reversed(symbols):
            factor = 1024 ** symbols.index(s)
            if n >= factor:
                value = n / factor
                return round(value, 2)  
        return n  

    def get_stats(self):
        current_datetime = datetime.datetime.now()
        # CPU
        cpu_usage = psutil.cpu_percent(interval=1)
        cpu_stats = psutil.cpu_stats()
        
        # Memory
        mem = psutil.virtual_memory()

        # Disk
        disk = psutil.disk_usage('/')

        # Network
        net = psutil.net_io_counters()

        return {
            "timestamp": current_datetime.isoformat(),
            "cpu_usage_percent": cpu_usage,
            "cpu_interrupts": cpu_stats.interrupts,
            "cpu_syscalls": cpu_stats.syscalls,
            "memory_percent": mem.percent,
            "memory_used": self._bytes2human(mem.used),
            "memory_free": self._bytes2human(mem.free),
            "bytes_sent": self._bytes2human(net.bytes_sent),
            "bytes_received": self._bytes2human(net.bytes_recv),
            "disk_usage_percent": disk.percent
        }

# import psutil
# import time
# import datetime

# psutil.PROCFS_PATH = '/host_proc'

# class SystemMonitor:
#     def __init__(self):
#         self.prev_cpu_times = None

#     def _bytes2human(self, n):
#         symbols = ('B', 'KB', 'MB', 'GB', 'TB')
#         for s in reversed(symbols):
#             factor = 1024 ** symbols.index(s)
#             if n >= factor:
#                 value = n / factor
#                 return f"{value:.2f} {s}"
#         return f"{n} B"

#     def _read_cpu_times(self):
#         """Đọc CPU times từ /host_proc/stat"""
#         try:
#             with open('/host_proc/stat', 'r') as f:
#                 line = f.readline().strip()
#                 if line.startswith('cpu '):
#                     # Bỏ qua 'cpu' và lấy các giá trị số
#                     values = [int(x) for x in line.split()[1:]]
#                     return values
#         except Exception as e:
#             print(f"Error reading /host_proc/stat: {e}")
#             return None
#         return None

#     def _calculate_cpu_usage(self, prev_times, curr_times):
#         """Tính CPU usage dựa trên sự khác biệt của CPU times"""
#         if not prev_times or not curr_times:
#             return 0.0

#         # Tổng thời gian CPU giữa hai lần đo
#         prev_total = sum(prev_times)
#         curr_total = sum(curr_times)
#         delta_total = curr_total - prev_total

#         # Thời gian CPU idle (thường là giá trị thứ 4 trong /proc/stat)
#         prev_idle = prev_times[3]
#         curr_idle = curr_times[3]
#         delta_idle = curr_idle - prev_idle

#         # Tính phần trăm CPU usage
#         if delta_total > 0:
#             return ((delta_total - delta_idle) / delta_total) * 100
#         return 0.0

#     def get_stats(self):
#         current_datetime = datetime.datetime.now()

#         # Đọc CPU times hiện tại
#         curr_cpu_times = self._read_cpu_times()

#         # Tính CPU usage nếu có dữ liệu trước đó
#         cpu_usage = 0.0
#         if self.prev_cpu_times:
#             cpu_usage = self._calculate_cpu_usage(self.prev_cpu_times, curr_cpu_times)

#         # Lưu CPU times hiện tại để sử dụng cho lần tiếp theo
#         self.prev_cpu_times = curr_cpu_times

#         # Lấy các thông tin khác
#         try:
#             cpu_stats = psutil.cpu_stats()
#         except Exception as e:
#             cpu_stats = type('obj', (), {'interrupts': 0, 'syscalls': 0})()
#             print(f"Error getting cpu_stats: {e}")

#         mem = psutil.virtual_memory()
#         disk = psutil.disk_usage('/')
#         net = psutil.net_io_counters()

#         return {
#             "timestamp": current_datetime.isoformat(),
#             "cpu_usage_percent": cpu_usage,
#             "cpu_interrupts": cpu_stats.interrupts,
#             "cpu_syscalls": cpu_stats.syscalls,
#             "memory_percent": mem.percent,
#             "memory_used": self._bytes2human(mem.used),
#             "memory_free": self._bytes2human(mem.free),
#             "bytes_sent": self._bytes2human(net.bytes_sent),
#             "bytes_received": self._bytes2human(net.bytes_recv),
#             "disk_usage_percent": disk.percent
#         }
        



