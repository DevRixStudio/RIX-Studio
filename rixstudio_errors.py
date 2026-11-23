class RixStudioError(Exception): pass
class NetworkError(RixStudioError): pass
class APIError(RixStudioError):
    def __init__(self,message,response=None,status_code=None):
        super().__init__(message); self.response=response; self.status_code=status_code
class UploadError(RixStudioError): pass
