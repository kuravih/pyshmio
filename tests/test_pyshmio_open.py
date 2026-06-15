import unittest
from pyshmio import SharedMemory, KeywordType
from pykato.log import setup_logger

logger = setup_logger("pyshmio_open", terminator="\n")


class TestPyshmioOpen(unittest.TestCase):
    # pylint: disable=missing-class-docstring

    def test_SharedMemory_stbsink_open(self):
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

    def test_SharedMemory_set_keyword_value(self):
        shm = SharedMemory("stb001_stbsink")
        keywords = shm.keywords
        if not keywords:
            self.skipTest("no keywords on stb001_stbsink")
        key = next(iter(keywords))
        keyword = keywords[key]
        original_value = keyword.value
        if keyword.type == KeywordType.LONG:
            new_value = original_value + 1
        elif keyword.type == KeywordType.DOUBLE:
            new_value = original_value + 1.0
        else:
            new_value = original_value
        shm.keywords[key].value = new_value
        assert shm.keywords[key].value == new_value, f"expected {new_value}, got {shm.keywords[key].value}"
        logger.info("keyword write: %s %s -> %s", key, original_value, new_value)
        shm.keywords[key].value = original_value
        assert shm.keywords[key].value == original_value

    def test_SharedMemory_stbsource_open(self):
        shm = SharedMemory("stb001_stbsource")
        assert isinstance(shm, SharedMemory)
        logger.info("shm.creation_time             : %s", shm.creation_time)
        logger.info("shm.last_access_time          : %s", shm.last_access_time)
        logger.info("shm.size                      : %s", shm.size)
        logger.info("shm.name                      : %s", shm.name)
        for ikey, key in enumerate(shm.keywords):
            logger.info("keyword %d = keywords[%s] = {.value = %s,.type = %s,.comment = %s}", ikey, key, shm.keywords[key].value, shm.keywords[key].type, shm.keywords[key].comment)
        logger.info("shm.shape                     : %s", shm.ndarray.shape)
        logger.info("shm.dtype                     : %s", shm.ndarray.dtype)
