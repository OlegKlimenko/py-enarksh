"""
Enarksh

Copyright 2013-2016 Set Based IT Consultancy

Licence MIT
"""
import os
import pwd
import signal

import zmq

import enarksh
from enarksh.event.Event import Event
from enarksh.event.EventActor import EventActor
from enarksh.event.EventController import EventController
from enarksh.message.ExitMessage import ExitMessage
from enarksh.message.MessageController import MessageController
from enarksh.spawner.JobHandler import JobHandler
from enarksh.spawner.event_handler.EventQueueEmptyEventHandler import EventQueueEmptyEventHandler
from enarksh.spawner.event_handler.ExitMessageEventHandler import ExitMessageEventHandler
from enarksh.spawner.event_handler.SIGCHLDEventHandler import SIGCHLDEventHandler
from enarksh.spawner.event_handler.SpawnJobMessageEventHandler import SpawnJobMessageEventHandler
from enarksh.spawner.message.SpawnJobMessage import SpawnJobMessage


class Spawner(EventActor):
    """
    The spawner.
    """
    # ------------------------------------------------------------------------------------------------------------------
    instance = None
    """
    The instance of this class.

    :type: None|enarksh.spawner.Spawner.Spawner
    """

    # ------------------------------------------------------------------------------------------------------------------
    def __init__(self):
        """
        Object constructor.
        """
        Spawner.instance = self

        self._event_controller = EventController()
        """
        The event controller.

        :type: enarksh.event.EventController.EventController
        """

        EventActor.__init__(self)

        self._message_controller = MessageController()
        """
        The message controller.

        :type: enarksh.message.MessageController.MessageController
        """

        self._job_handlers = {}
        """
        The job handlers. A dictionary from PID to the job handler for the process (of the job).

        :type: dict[int,enarksh.spawner.JobHandler.JobHandler]
        """

        self._sigchld_event = Event(self)
        """
        Event for SIGCHLD has been received.

        :type: enarksh.event.Event.Event
        """

        self._zmq_incoming_message_event = Event(self)
        """
        Event for a ZMQ message is available.

        :type: enarksh.event.Event.Event
        """

    # ------------------------------------------------------------------------------------------------------------------
    @property
    def sigchld_event(self):
        """
        Returns the event for SIGCHLD has been received.

        :rtype: enarksh.event.Event.Event
        """
        return self._sigchld_event

    # ------------------------------------------------------------------------------------------------------------------
    @property
    def job_handlers(self):
        """
        Returns the job handlers for the currently running processes.

        :rtype: dict[int,enarksh.spawner.JobHandler.JobHandler]
        """
        return self._job_handlers

    # ------------------------------------------------------------------------------------------------------------------
    @property
    def zmq_incoming_message_event(self):
        """
        Returns the event for a ZMQ message is available.

        :rtype: enarksh.event.Event.Event
        """
        return self._zmq_incoming_message_event

    # ------------------------------------------------------------------------------------------------------------------
    def add_job_handler(self, job_handler):
        """
        Adds a job handler to this spawner.

        :param enarksh.spawner.JobHandler.JobHandler job_handler: The job handler.
        """
        self._job_handlers[job_handler.pid] = job_handler

    # ------------------------------------------------------------------------------------------------------------------
    def remove_job_handler(self, pid):
        """
        Removes a job handler to this spawner.

        :param int pid: The (original) PID of the process that the jon handlers was handling.
        """
        del self._job_handlers[pid]

    # ------------------------------------------------------------------------------------------------------------------
    @staticmethod
    def sigchld_handler(*_):
        """
        Static method for SIGCHLD. Set a flag that a child has exited.
        """
        Spawner.instance.sigchld_event.fire()

    # ------------------------------------------------------------------------------------------------------------------
    def _install_signal_handlers(self):
        """
        Install signal handlers for SIGCHLD and SIGHUP.
        """
        # Install signal handler for child has exited.
        signal.signal(signal.SIGCHLD, self.sigchld_handler)

    # ------------------------------------------------------------------------------------------------------------------
    @staticmethod
    def _set_unprivileged_user():
        """
        Set the real and effective user and group to an unprivileged user.
        """
        _, _, uid, gid, _, _, _ = pwd.getpwnam('enarksh')

        os.setresgid(gid, gid, 0)
        os.setresuid(uid, uid, 0)

    # ------------------------------------------------------------------------------------------------------------------
    def _startup(self):
        """
        Performs the necessary actions for starting the spawner daemon.
        """
        # Log stop of the spawner.
        print('Start spawner')

        # Set the effective user and group to an unprivileged user and group.
        self._set_unprivileged_user()

        # Install signal handlers.
        self._install_signal_handlers()

        # Read all user names under which the controller is allowed to start jobs.
        JobHandler.read_allowed_users()

    # ------------------------------------------------------------------------------------------------------------------
    @staticmethod
    def _shutdown():
        """
        Performs the necessary actions for stopping the spawner.
        """
        # Log stop of the spawner.
        print('Stop spawner')

    # ------------------------------------------------------------------------------------------------------------------
    def _register_sockets(self):
        """
        Registers ZMQ sockets for communication with other processes in Enarksh.
        """
        # Register socket for receiving asynchronous incoming messages.
        self._message_controller.register_end_point('pull', zmq.PULL, enarksh.SPAWNER_PULL_END_POINT)

        # Register socket for sending asynchronous messages to the controller.
        self._message_controller.register_end_point('controller', zmq.PUSH, enarksh.CONTROLLER_PULL_END_POINT)

        # Register socket for sending asynchronous messages to the logger.
        self._message_controller.register_end_point('logger', zmq.PUSH, enarksh.LOGGER_PULL_END_POINT)

    # ------------------------------------------------------------------------------------------------------------------
    def _register_message_types(self):
        """
        Registers all message type that the spawner handles at the message controller.
        """
        self._message_controller.register_message_type(ExitMessage.MESSAGE_TYPE)
        self._message_controller.register_message_type(SpawnJobMessage.MESSAGE_TYPE)

    # ------------------------------------------------------------------------------------------------------------------
    def _register_events_handlers(self):
        """
        Registers all event handlers at the event controller.
        """
        EventQueueEmptyEventHandler.init()

        # Register message received event handlers.
        self._message_controller.register_listener(ExitMessage.MESSAGE_TYPE, ExitMessageEventHandler.handle)
        self._message_controller.register_listener(SpawnJobMessage.MESSAGE_TYPE,
                                                   SpawnJobMessageEventHandler.handle,
                                                   self)
        # Register other event handlers.
        self._sigchld_event.register_listener(SIGCHLDEventHandler.handle, self)
        self._zmq_incoming_message_event.register_listener(self._message_controller.receive_message)
        self._event_controller.event_queue_empty.register_listener(EventQueueEmptyEventHandler.handle, self)

    # ------------------------------------------------------------------------------------------------------------------
    def main(self):
        """
        The main function of the job spawner.
        """
        self._startup()

        self._register_sockets()

        self._register_message_types()

        self._register_events_handlers()

        self._message_controller.no_barking(3)

        self._event_controller.loop()

        self._shutdown()

# ----------------------------------------------------------------------------------------------------------------------
