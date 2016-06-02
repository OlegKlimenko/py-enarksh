from lib import enarksh
from lib.enarksh.XmlReader.Resource.CountingResource import CountingResource
from lib.enarksh.XmlReader.Resource.ReadWriteLockResource import ReadWriteLockResource
from lib.enarksh.XmlReader.Resource.Resource import Resource


# ----------------------------------------------------------------------------------------------------------------------
def create_resource(rtp_id, rsc_id, node) -> Resource:
    """
    A factory for creating nodes.
    """
    if rtp_id == enarksh.ENK_RTP_ID_COUNTING:
        resource = CountingResource(node)

    elif rtp_id == enarksh.ENK_RTP_ID_READ_WRITE:
        resource = ReadWriteLockResource(node)

    else:
        raise Exception("Unexpected resource type ID '%s'.", rtp_id)

    resource.load_db(rsc_id)

    return resource


# ----------------------------------------------------------------------------------------------------------------------
