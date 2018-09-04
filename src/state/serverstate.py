from rx import Observable, Observer
from rx.subjects import BehaviorSubject
from src.common.singleton_decorator import singleton
from src.common.consts import DB_MONITOR_SUB, BC_MONITOR_SUB

@singleton
class ServerState:
    db_data = None
    monitor_data = None

    bc_monitorSub = BehaviorSubject(None)
    db_monitorSub = BehaviorSubject(None)

    bc_monitor = Observable
    db_monitor = Observable

    def set_db_data(self, data):
        self.db_data = data
        self.bc_monitor.map(self.set_db_data(self.db_data)).publish()

    def get_db_data(self):
        return self.db_datas

    def setMonitor(self, d):
        self.monitor_data = d

    def getMonitor(self):
        return self.monitor_data

    # select method will use to get observerable
    def select(self, observer_name):
        if observer_name == BC_MONITOR_SUB:
            return self.bc_monitorSub
        elif observer_name == DB_MONITOR_SUB:
            return self.db_monitorSub
        else:
            # print observer_name + ' is not recognize observable.'
            return None

    # dispatch method will use to update data on the observer
    def dispatch(self, observer_name, payload):
        if observer_name == BC_MONITOR_SUB:
            self.bc_monitorSub.on_next(payload)
            return payload
        elif observer_name == DB_MONITOR_SUB:
            self.db_monitorSub.on_next(payload)
            return payload
        else:
            # print observer_name + ' is not recognize observable.'
            return None
