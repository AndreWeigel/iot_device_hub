from .user import User
from .device import Device

# Rebuild forward references
User.model_rebuild()
Device.model_rebuild()
