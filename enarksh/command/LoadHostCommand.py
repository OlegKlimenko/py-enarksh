"""
Enarksh

Copyright 2013-2016 Set Based IT Consultancy

Licence MIT
"""
from cleo import Command

from enarksh.style.EnarkshStyle import EnarkshStyle
from enarksh.util.LoadHost import LoadHost


class LoadHostCommand(Command):
    """
    Loads the host

    load_host
    """

    # ------------------------------------------------------------------------------------------------------------------
    def handle(self):
        """
        Executes the load host command.
        """
        self.output = EnarkshStyle(self.input, self.output)

        reader = LoadHost()
        reader.main()

# ----------------------------------------------------------------------------------------------------------------------
