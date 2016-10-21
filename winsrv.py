import win32serviceutil
import win32service
import win32event
import servicemanager
import socket
from lyncweb import app


class AppServerSvc (win32serviceutil.ServiceFramework):
    _svc_name_ = "LyncLogWeb"
    _svc_display_name_ = "LyncLogWeb Service"
    _svc_description_ = "LyncLogWeb Python service for view log from db"

    def __init__(self,args):
        win32serviceutil.ServiceFramework.__init__(self,args)
        self.hWaitStop = win32event.CreateEvent(None,0,0,None)
        socket.setdefaulttimeout(60)

    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.hWaitStop)

    def SvcDoRun(self):
        servicemanager.LogMsg(servicemanager.EVENTLOG_INFORMATION_TYPE,
                              servicemanager.PYS_SERVICE_STARTED,
                              (self._svc_name_,''))
        self.main()

    def main(self):
        app.run(host="10.11.11.124", port=80)

if __name__ == '__main__':
    win32serviceutil.HandleCommandLine(AppServerSvc)
