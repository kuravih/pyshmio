import unittest
from pyshmio import SharedMemory, Keyword, KeywordType, DataType
from pykato.log import setup_logger

logger = setup_logger("pyshmio_create", terminator="\n")


class TestPyshmioCreate(unittest.TestCase):
    # pylint: disable=missing-class-docstring

    def test_SharedMemory_create(self):
        shm = SharedMemory.create("source_8uint", 100 * 100, DataType.UINT8)
        assert isinstance(shm, SharedMemory)
        logger.info("shm.creation_time             : %s", shm.creation_time)
        logger.info("shm.last_access_time          : %s", shm.last_access_time)
        logger.info("shm.size                      : %s", shm.size)
        logger.info("shm.name                      : %s", shm.name)

    def test_SharedMemory_create_with_keywords(self):
        width, height = 10, 10
        kw_width = Keyword("WIDTH", KeywordType.LONG, width, "Width")
        kw_height = Keyword("HEIGHT", KeywordType.LONG, height, "Height")
        shm = SharedMemory.create("source_16uint", width * height, DataType.UINT16, [kw_width, kw_height])
        logger.info("shm.creation_time             : %s", shm.creation_time)
        logger.info("shm.last_access_time          : %s", shm.last_access_time)
        logger.info("shm.size                      : %s", shm.size)
        logger.info("shm.name                      : %s", shm.name)
        for ikey, key in enumerate(shm.keywords):
            logger.info("keyword %d = keywords[%s] = {.value = %s,.type = %s,.comment = %s}", ikey, key, shm.keywords[key].value, shm.keywords[key].type, shm.keywords[key].comment)
        logger.info("shm.shape                     : %s", shm.ndarray.shape)
        logger.info("shm.dtype                     : %s", shm.ndarray.dtype)
