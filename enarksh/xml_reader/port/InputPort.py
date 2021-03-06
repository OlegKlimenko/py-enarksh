"""
Enarksh

Copyright 2013-2016 Set Based IT Consultancy

Licence MIT
"""
from enarksh.DataLayer import DataLayer
from enarksh.xml_reader.port.Port import Port


class InputPort(Port):
    # ------------------------------------------------------------------------------------------------------------------
    def get_dependency_level(self):
        """
        :rtype: int
        """
        dependency_level = -1
        for dependency in self._dependencies:
            level = dependency.get_dependency_level()
            if level > dependency_level:
                dependency_level = level

        return dependency_level

    # ------------------------------------------------------------------------------------------------------------------
    def get_uri(self, obj_type='input_port'):
        """
        Returns the URI of this input port.

        :param str obj_type: The entity type.

        :rtype: str
        """
        if self._node:
            uri = self._node.get_uri(obj_type)
        else:
            uri = '//' + obj_type

        return uri + '/' + self._port_name

    # ------------------------------------------------------------------------------------------------------------------
    def store(self, nod_id):
        """
        Stores the definition of this port into the database.

        :param int nod_id: The ID of the node to which this node belongs
        """
        uri_id = DataLayer.enk_misc_insert_uri(self.get_uri())
        self._prt_id = DataLayer.enk_reader_port_store_input_port(nod_id,
                                                                  uri_id,
                                                                  self._port_name)

    # ------------------------------------------------------------------------------------------------------------------
    def store_dependencies(self):
        for dependency in self._dependencies:
            dependency.store(self, self._node.parent_node)

# ----------------------------------------------------------------------------------------------------------------------
