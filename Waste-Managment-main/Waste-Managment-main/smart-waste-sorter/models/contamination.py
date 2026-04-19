from datetime import datetime

class ContaminationLog:
    def __init__(self, error_code, description, bin_id, severity="low"):
        self.error_code = error_code
        self.timestamp = datetime.utcnow()
        self.description = description
        self.bin_id = bin_id
        self.severity = severity
        self.action_taken = None
        self.resolved = False

    def to_dict(self):
        return {
            "error_code": self.error_code,
            "timestamp": self.timestamp,
            "description": self.description,
            "bin_id": self.bin_id,
            "severity": self.severity,
            "action_taken": self.action_taken,
            "resolved": self.resolved
        }
