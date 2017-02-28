
from .extensions import _

SESSION_LANG_KEY = "current_lang"
SESSION_TIMEZONE_KEY = "current_tz"

"""
verified
"""

STATUS_DRAFT = 0
STATUS_USED = 1
STATUS_TRASH = 9

STATUS = (
    (STATUS_DRAFT, _('Draft')), 
    (STATUS_USED, _('Used')), 
    (STATUS_TRASH, _('Used')), 
)

