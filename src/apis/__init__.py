from starlette.routing import Route
from src.apis.health_check import HealthCheck
from src.apis.register import Register
from src.apis.login import Login
from src.apis.change_password import ChangePassword
from src.apis.reset_password import ResetPassword
from src.apis.logout import Logout
from src.apis.home import Home
from src.apis.user_info import UserInfo
from src.apis.approve_request import ApproveRequest, AllApproveRequest
routes = [
    Route('/', Home),
    Route('/health_check', HealthCheck),
    Route('/register', Register),
    Route('/login', Login),
    Route('/logout', Logout),
    Route('/change_password', ChangePassword),
    Route('/reset_password', ResetPassword),
    Route('/user_infor', UserInfo),
    Route('/approve_request', ApproveRequest),
    Route('/all_approve_request', AllApproveRequest),


]
