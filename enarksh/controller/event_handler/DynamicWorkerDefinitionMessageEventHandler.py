"""
Enarksh

Copyright 2013-2016 Set Based IT Consultancy

Licence MIT
"""
import sys
import traceback

from enarksh.DataLayer import DataLayer
from enarksh.xml_reader.XmlReader import XmlReader
from enarksh.xml_reader.node.FakeParent import FakeParent


class DynamicWorkerDefinitionMessageEventHandler:
    """
    An event handler for a DynamicWorkerDefinitionMessage received events.
    """

    # ------------------------------------------------------------------------------------------------------------------
    @staticmethod
    def handle(_event, message, controller):
        """
        Handles a DynamicWorkerDefinitionMessage received event.

        :param * _event: Not used.
        :param enarksh.controller.message.DynamicWorkerDefinitionMessage.DynamicWorkerDefinitionMessage message: 
               The message.
        :param enarksh.controller.Controller.Controller controller: The controller.
        """
        del _event

        try:
            print('rnd_id: ' + str(message.rnd_id))

            # Get info of the dynamic node.
            info = DataLayer.enk_back_run_node_get_dynamic_info_by_generator(message.rnd_id)

            schedule = controller.get_schedule_by_sch_id(message.sch_id)
            parent = FakeParent(schedule,
                                controller.host_resources,
                                info['nod_id_outer_worker'],
                                info['rnd_id_outer_worker'])

            # Validate XML against XSD.
            reader = XmlReader()
            inner_worker = reader.parse_dynamic_worker(message.xml, parent)
            name = inner_worker.name

            # Note: Dynamic node is the parent of the worker node which is the parent of the inner worker node.
            inner_worker.set_levels(info['nod_recursion_level'] + 2)

            # Store the dynamically defined inner worker node.
            inner_worker.store(info['srv_id'], 0)

            # Create dependencies between the input and output port of the worker node and its child node(s).
            DataLayer.enk_back_node_dynamic_add_dependencies(info['nod_id_outer_worker'], inner_worker.nod_id)

            # XXX trigger reload of front end

            # Unload the schedule to force a reload of the schedule with new nodes added.
            controller.unload_schedule(message.sch_id)

            response = {'ret':     0,
                        'message': "Worker '%s' successfully loaded." % name}

        except Exception as exception:
            print(exception, file=sys.stderr)
            response = {'ret':     -1,
                        'message': str(exception)}
            traceback.print_exc(file=sys.stderr)

        # Send the message to the job.
        controller.message_controller.send_message('lockstep', response, True)

# ----------------------------------------------------------------------------------------------------------------------
