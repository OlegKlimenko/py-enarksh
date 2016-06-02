import json
from lib.enarksh.Controller.Node.SimpleNode import SimpleNode


# ----------------------------------------------------------------------------------------------------------------------
class CommandJobNode(SimpleNode):
    """
    Class for objects in the controller of type 'CommandJob'.
    """
    # ------------------------------------------------------------------------------------------------------------------
    def __init__(self, node_data: dict):
        SimpleNode.__init__(self, node_data)

        self._user_name = node_data['nod_user_name']
        """
        The account under which the command must run.
        """

        self._command = json.loads(node_data['nod_command'])
        """
        The actual command of this job.
        """

    # ------------------------------------------------------------------------------------------------------------------
    def get_start_message(self):
        message = SimpleNode.get_start_message(self)

        message['user_name'] = self._user_name
        message['args'] = self._command

        return message


# ----------------------------------------------------------------------------------------------------------------------