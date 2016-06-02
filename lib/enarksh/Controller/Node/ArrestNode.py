from lib import enarksh
from lib.enarksh.Controller.StateChange import StateChange
from lib.enarksh.Controller.Node.SimpleNode import SimpleNode


# ----------------------------------------------------------------------------------------------------------------------
class ArrestNode(SimpleNode):
    """
    Class for objects in the controller of type 'ArrestNode'.
    """
    # ------------------------------------------------------------------------------------------------------------------
    @StateChange.wrapper
    def start(self):
        self._set_rst_id(enarksh.ENK_RST_ID_COMPLETED)

        return False

    # ------------------------------------------------------------------------------------------------------------------
    def get_start_message(self):
        raise Exception("Internal error.")


# ----------------------------------------------------------------------------------------------------------------------