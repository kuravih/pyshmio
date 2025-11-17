import unittest
from pyshmio import SharedMemory
from pykato.log import setup_logger

logger = setup_logger("pyshmio_open", terminator="\n")


class TestPyshmio(unittest.TestCase):
    # pylint: disable=missing-class-docstring

    def test_SharedMemory_open(self):
        shm = SharedMemory("stb001_stbsink")
        assert isinstance(shm, SharedMemory)
        logger.info("shm.creation_time             : %s", shm.creation_time)
        logger.info("shm.last_access_time          : %s", shm.last_access_time)
        logger.info("shm.size                      : %s", shm.size)
        logger.info("shm.name                      : %s", shm.name)
        for ikey, key in enumerate(shm.keywords):
            logger.info("keyword %d = keywords[%s] = {.value = %s,.type = %s,.comment = %s}", ikey, key, shm.keywords[key].value, shm.keywords[key].type, shm.keywords[key].comment)
        logger.info("shm.shape                     : %s", shm.ndarray.shape)
        logger.info("shm.dtype                     : %s", shm.ndarray.dtype)
