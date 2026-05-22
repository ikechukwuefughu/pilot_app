from app import db 
from .household import Household 
from .parent import Parent 
from .child import Child 
from .child_contracts import ChildContract 
from .child_medical_info import ChildMedicalInfo 
from .child_emergency_contact import ChildEmergencyContact 
from .child_parent_relationship import ChildParentRelationship 
__all__ = [ 
    "Household", 
    "Parent", 
    "Child", 
    "ChildContract", 
    "ChildMedicalInfo", 
    "ChildEmergencyContact", 
    "ChildParentRelationship" 
]
# from app import db

# from .household import Household
# from .parent import Parent
# from .child import Child

# from .child_contracts import ChildContract
# from .child_medical_info import ChildMedicalInfo
# from .child_emergency_contact import ChildEmergencyContact
# from .child_parent_relationship import ChildParentRelationship

# from .branches import Branch
# from .rooms import Room

# from .educators import Educator
# from .educator_rooms import EducatorRoom
# from .educator_working_hours import EducatorWorkingHour
# from .educator_attendance import EducatorAttendance

# from .attendance_sessions import AttendanceSession

# from .child_rooms import ChildRoom
# # from app.models.child_attendance import ChildAttendance
# # from app.models.child_attendance_history import ChildAttendanceHistory
# from .child_attendance import ChildAttendance
# from .child_attendance_history import ChildAttendanceHistory

# __all__ = [
#     "Household",
#     "Parent",
#     "Child",

#     "ChildContract",
#     "ChildMedicalInfo",
#     "ChildEmergencyContact",
#     "ChildParentRelationship",

#     "Branch",
#     "Room",

#     "Educator",
#     "EducatorRoom",
#     "EducatorWorkingHour",
#     "EducatorAttendance",

#     "AttendanceSession",

#     "ChildRoom",
#     "ChildAttendance",
#     "ChildAttendanceHistory"
# ]
