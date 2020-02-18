from typing import Dict


class UploadOption:
    def __init__(self, data: Dict):
        if isinstance(data, Dict):
            self.file = data.get("file", None)
            self.title = data.get("title", "Test Title")
            self.description = data.get("description", "Test Description")
            self.category = data.get("category", 22)
            self.keywords = data.get("keywords", "")
            self.privacyStatus = data.get("privacyStatus", "private")
            self.logging_level = data.get("logging_level", "WARNING")
        else:
            # type is argparse.Namespace.
            self.file = data.file
            self.title = data.title
            self.description = data.description
            self.category = data.category
            self.keywords = data.keywords
            self.privacyStatus = data.privacyStatus
            # self.logging_level = data.logging_level
